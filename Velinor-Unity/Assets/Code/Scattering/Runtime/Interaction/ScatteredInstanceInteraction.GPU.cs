using System;
using System.Collections.Generic;
using Unity.Collections;
using Unity.Collections.LowLevel.Unsafe;
using Unity.Mathematics;
using UnityEngine;
using UnityEngine.Rendering;

namespace TimeGhost
{
    public class ScatteredInstanceInteractionGPU
    {
        static class UniformIDs
        {
            //Copy
            public static int _CopyDstBuffer;
            public static int _CopySrcBuffer;
            public static int _CopySrcOffsetInWords;
            public static int _CopyDstOffsetInWords;
            public static int _TotalWordCountToCopy;
            
            //Interaction
            public static int _FreePagesBufferRW;
            public static int _FreePagesBuffer;
            public static int _FreePagesRange;

            public static int _ReservedPagesBufferRW;
            public static int _ReservedPagesBuffer;

            public static int _PerTileHeaderBufferRW;
            public static int _PerTileHeaderBuffer;
            
            public static int _Counters;
            public static int _CountersRW;

            public static int _TilesToFreeBuffer;
            public static int _TilesToFreeCount;

            public static int _ReservedPagesToDefragment;
            public static int _DefragmentTileOffset;

            public static int _TileIndexAndPageEntryCountsBuffer;
            public static int _TotalNumberOfTiles;

            public static int _NumberOfTileHeadersToMap;
            public static int _TileHeaderMappingBuffer;

            public static int _PerInstanceStateBuffer;
            public static int _PerInstanceStateBufferRW;
            
            public static int _PerInstancePropertiesBufferRW;
            public static int _PerInstancePropertiesBuffer;
            
            public static int _UploadBatchDataBuffer;
            public static int _UploadBatchEntries;
            
            public static int _AffectedTilePageAndColliderMasksBuffer;
            public static int _CollidersBuffer;
            public static int _AffectedTilePageAndColliderMasksBufferOffset;
            public static int _CollidersBufferOffset;

            public static int _TimeStep;
            public static int _UpdateSimulationArgsBuffer;
   
            public static int ScatteredInstanceInteractionConstants;

        }
        static class Kernels
        {
            public static int kCopyBuffer;
            public static int kResetFreeAndReservedPageCounters;
            public static int kResetDefragmentCounter;
            public static int kResetPerTileHeaders;
            public static int kSetupPerTileHeaderMappings;
            public static int kAppendFreePages;
            public static int kIncrementFreePagesCounter;
            public static int kFreePages;
            public static int kDefragmentPages;
            public static int kReservePages;
            public static int kUploadTileData;
            public static int kApplyCapsuleCollider;
            public static int kSetupUpdateSimulationArgs;
            public static int kUpdateSimulation;
            public static int kUpdatePreviousPosition;
        }
        
        public struct CapsuleColliderEntry
        {
            public float4 wp0Radius;
            public float4 wp1;

        }

        private static ComputeShader s_ComputeShader;
        
        private GraphicsBuffer m_PerTileHeadersBuffer;
        private GraphicsBuffer m_CountersBuffer;
        
        private GraphicsBuffer[] m_PageIndicesBuffer = new GraphicsBuffer[2];

        private GraphicsBuffer m_FreePagesBuffer;
        private GraphicsBuffer m_PerInstancePropertiesBuffer;
        private GraphicsBuffer m_PerInstanceStateBuffer;
        private GraphicsBuffer m_UploadBatchInfoBuffer;
        private GraphicsBuffer m_UploadBatchDataBuffer;
        private GraphicsBuffer m_ScratchBuffer;
        private GraphicsBuffer m_ConstantsBuffer;
        private GraphicsBuffer m_IndirectDispatchArgsBuffer;
        private GraphicsBuffer m_CollidersBuffer;

        private bool m_Initialized = false;
        
        private static readonly int c_MaxPagesToUploadPerFrame = 200;
        
        private List<GraphicsBuffer> m_BuffersToRelease;

        private ScatteredInstanceInteractionConstants constants;
        
        const uint c_MaxDispatchSize = 0xFFFF;
        
        #region API
        
        //API to outside
        internal static int GetPageSize()
        {
            return (int) ScatteredInstanceInteractionDataSettings.SCATTERED_INSTANCE_INTERACTION_PAGE_SIZE;
        }

        internal static int GetMaximumNumberOfPagesToUploadPerBatch()
        {
            return c_MaxPagesToUploadPerFrame;
        }

        internal void Init(int2 numberOfTilesPerDimension, int2 globalTileDimensions)
        { 
            Deinit();

            if (numberOfTilesPerDimension.x == 0  || numberOfTilesPerDimension.y == 0)
            {
                Debug.LogError("tried to initialize ScatteredInstanceInteraction.GPU with 0 tilesPerDimension, skipping");
                return;
            }
            
            CommandBuffer cmd = CommandBufferPool.Get("ScatteredInstanceInteractionInit");
            if (m_BuffersToRelease == null)
            {
                m_BuffersToRelease = new List<GraphicsBuffer>(10);
            }
            InitializeGPU(cmd, numberOfTilesPerDimension, globalTileDimensions);
            Graphics.ExecuteCommandBuffer(cmd);
            CommandBufferPool.Release(cmd);
            m_Initialized = true;
        }

        internal void Deinit()
        {
            if (m_Initialized)
            {
                FreeGPUResources();
                m_Initialized = false;
            }

            SetEnabled(false);

        }

        internal void SetColliderSmoothingMargin(float colliderSmoothingMargin)
        {
            constants._ColliderMarginUnused = new float4(math.saturate(colliderSmoothingMargin), 0.0f, 0.0f, 0.0f);
        }

        internal void PushConstantsToGPU()
        {
            var constantContents = new NativeArray<ScatteredInstanceInteractionConstants>(1, Allocator.Temp);
            constantContents[0] = constants;
            m_ConstantsBuffer.SetData(constantContents);
            constantContents.Dispose();
        }
        
        internal void RefreshPages(NativeArray<int3> pagesToReserveParameters, NativeArray<int> tilesToFreeParameters, int numberOfTilesToRefresh, int numberOfTotalRequiredPages)
        {
            if (!m_Initialized) return;
            CommandBuffer cmd = CommandBufferPool.Get("ScatteredInstanceTileRefresh");

            EnsurePerInstanceData(cmd, numberOfTotalRequiredPages);
            if (numberOfTilesToRefresh > 0)
            {
                FreeTilePages(cmd, tilesToFreeParameters, numberOfTilesToRefresh);
                ReserveTilePages(cmd, pagesToReserveParameters, numberOfTilesToRefresh);

            }

            Graphics.ExecuteCommandBuffer(cmd);
            CommandBufferPool.Release(cmd);

            ExecutePendingBufferReleases();
            
            SetEnabled(true);
            SetGlobalRenderingResources();

        }

        internal void SetupActiveTileToAbsoluteTileMapping(NativeArray<int2> activeTileToAbsoluteTileMappings)
        {
            if (!m_Initialized) return;
            CommandBuffer cmd = CommandBufferPool.Get("ScatteredInstanceTileMapping");
            EnsureScratchBuffer(activeTileToAbsoluteTileMappings.Length * 2 * 4);
            
            cmd.SetBufferData(m_ScratchBuffer, activeTileToAbsoluteTileMappings);

            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kSetupPerTileHeaderMappings, UniformIDs._TileHeaderMappingBuffer, m_ScratchBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kSetupPerTileHeaderMappings, UniformIDs._PerTileHeaderBufferRW, m_PerTileHeadersBuffer);
            cmd.SetComputeIntParam(s_ComputeShader, UniformIDs._NumberOfTileHeadersToMap, activeTileToAbsoluteTileMappings.Length);
            cmd.DispatchCompute(s_ComputeShader, Kernels.kSetupPerTileHeaderMappings, GetDispatchGroupsCount(Kernels.kSetupPerTileHeaderMappings, (uint)activeTileToAbsoluteTileMappings.Length), 1,1);
            
            Graphics.ExecuteCommandBuffer(cmd);
            CommandBufferPool.Release(cmd);
            
            
            ExecutePendingBufferReleases();
            
        }

        internal void UploadPages(NativeArray<ScatteredInstanceDataUploadBatch> uploadBatches ,NativeArray<ScatteredInstancePropertiesPacked> uploadData, int batchCount)
        {
            if (!m_Initialized) return;
            CommandBuffer cmd = CommandBufferPool.Get("ScatteredInstanceDataUpload");
            
            cmd.SetBufferData(m_UploadBatchInfoBuffer, uploadBatches, 0, 0, batchCount);
            cmd.SetBufferData(m_UploadBatchDataBuffer, uploadData, 0, 0, batchCount * GetPageSize());

            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kUploadTileData, UniformIDs._UploadBatchDataBuffer, m_UploadBatchDataBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kUploadTileData, UniformIDs._UploadBatchEntries, m_UploadBatchInfoBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kUploadTileData, UniformIDs._PerTileHeaderBuffer, m_PerTileHeadersBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kUploadTileData, UniformIDs._ReservedPagesBuffer, m_PageIndicesBuffer[0]);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kUploadTileData, UniformIDs._PerInstancePropertiesBufferRW, m_PerInstancePropertiesBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kUploadTileData, UniformIDs._PerInstanceStateBufferRW, m_PerInstanceStateBuffer);
            
            cmd.DispatchCompute(s_ComputeShader, Kernels.kUploadTileData, batchCount, 1,1);
            
            Graphics.ExecuteCommandBuffer(cmd);
            CommandBufferPool.Release(cmd);
            
            ExecutePendingBufferReleases();
        }

        internal void UploadColliderData(NativeArray<CapsuleColliderEntry> colliderEntries,  int collidersCount, NativeArray<uint3> tilesPagesAndMasksAffectedByColliders,  int tilesPagesAndMasksCount)
        {
            if (!m_Initialized) return;
            if (tilesPagesAndMasksCount == 0) return;

            CommandBuffer cmd = CommandBufferPool.Get("ScatteredInstanceUploadColliderData");

            EnsureScratchBuffer(tilesPagesAndMasksCount * 3 * 4);
            
            cmd.SetBufferData(m_ScratchBuffer, tilesPagesAndMasksAffectedByColliders, 0, 0, tilesPagesAndMasksCount);
            cmd.SetBufferData(m_CollidersBuffer, colliderEntries, 0, 0, collidersCount);

            Graphics.ExecuteCommandBuffer(cmd);
            CommandBufferPool.Release(cmd);
            
            ExecutePendingBufferReleases();
        }


        internal void StepCollisions(int collidersOffset, int tilesPagesAndMasksOffset, int tilesPagesAndMasksCount, float deltaTime)
        {
            if (!m_Initialized) return;
            if (tilesPagesAndMasksCount == 0) return;

            CommandBuffer cmd = CommandBufferPool.Get("ScatteredInstanceApplyCollider");

            cmd.SetComputeIntParam(s_ComputeShader,  UniformIDs._AffectedTilePageAndColliderMasksBufferOffset, tilesPagesAndMasksOffset);
            cmd.SetComputeIntParam(s_ComputeShader,  UniformIDs._CollidersBufferOffset, collidersOffset);
            cmd.SetComputeFloatParam(s_ComputeShader, UniformIDs._TimeStep, deltaTime);
            
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kApplyCapsuleCollider, UniformIDs._AffectedTilePageAndColliderMasksBuffer, m_ScratchBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kApplyCapsuleCollider, UniformIDs._PerTileHeaderBuffer, m_PerTileHeadersBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kApplyCapsuleCollider, UniformIDs._ReservedPagesBuffer, m_PageIndicesBuffer[0]);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kApplyCapsuleCollider, UniformIDs._PerInstancePropertiesBufferRW, m_PerInstancePropertiesBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kApplyCapsuleCollider, UniformIDs._PerInstanceStateBufferRW, m_PerInstanceStateBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kApplyCapsuleCollider, UniformIDs._CollidersBuffer, m_CollidersBuffer);

            cmd.DispatchCompute(s_ComputeShader, Kernels.kApplyCapsuleCollider, tilesPagesAndMasksCount, 1, 1);
            

            Graphics.ExecuteCommandBuffer(cmd);
            CommandBufferPool.Release(cmd);
            
            ExecutePendingBufferReleases();
        }

        internal void PrepareSimulation()
        {
            if (!m_Initialized) return;
            if (m_PageIndicesBuffer[0] == null) return;
            CommandBuffer cmd = CommandBufferPool.Get("ScatteredInstancePrepareSimulation");

            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kSetupUpdateSimulationArgs, UniformIDs._UpdateSimulationArgsBuffer, m_IndirectDispatchArgsBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kSetupUpdateSimulationArgs, UniformIDs._Counters, m_CountersBuffer);
            cmd.DispatchCompute(s_ComputeShader, Kernels.kSetupUpdateSimulationArgs, 1, 1, 1);

            StoreOffsetHistoryForMotionVectors(cmd); //store previous position before starting next simulation cycle(s)
            
            Graphics.ExecuteCommandBuffer(cmd);
            CommandBufferPool.Release(cmd);
            
            ExecutePendingBufferReleases();
            
        }
        
        internal void StepSimulation(float deltaTimePerStep)
        {
            if (!m_Initialized) return;
            if(m_PageIndicesBuffer[0] == null) return;
            
            CommandBuffer cmd = CommandBufferPool.Get("ScatteredInstanceUpdateSimulation");

            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kUpdateSimulation, UniformIDs._ReservedPagesBuffer, m_PageIndicesBuffer[0]);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kUpdateSimulation, UniformIDs._PerInstanceStateBufferRW, m_PerInstanceStateBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kUpdateSimulation, UniformIDs._PerInstancePropertiesBuffer, m_PerInstancePropertiesBuffer);
            cmd.SetComputeFloatParam(s_ComputeShader, UniformIDs._TimeStep, deltaTimePerStep);
            cmd.DispatchCompute(s_ComputeShader, Kernels.kUpdateSimulation, m_IndirectDispatchArgsBuffer, 0);
            

            Graphics.ExecuteCommandBuffer(cmd);
            CommandBufferPool.Release(cmd);
            
            ExecutePendingBufferReleases();
        }


        
        
        #endregion
        #region Internals

        static GraphicsBuffer CreateGraphicsBuffer(GraphicsBuffer.Target t,int count, int stride,  string name)
        {
            var b =  new GraphicsBuffer(t, count, stride);
            b.name = name;
            return b;
        }

        void ExecutePendingBufferReleases()
        {
            foreach (var buff in m_BuffersToRelease)
            {
                buff.Dispose();
            }
            m_BuffersToRelease.Clear();
        }
        
        static void InitializeStaticFields<T>(Type type, Func<string, T> construct)
        {
            foreach (var field in type.GetFields())
            {
                field.SetValue(null, construct(field.Name));
            }
        }

        static int GetDispatchGroupsCount(int kernel, uint threadCount)
        {
            s_ComputeShader.GetKernelThreadGroupSizes(kernel, out var groupX, out var groupY, out var groupZ );
            return (int)((threadCount + groupX - 1) / groupX);
        }

        static void StaticInitialize()
        {
            if (s_ComputeShader == null)
            {
                s_ComputeShader = Resources.Load<ComputeShader>("ScatteredInstanceInteractionCS");
                InitializeStaticFields(typeof(UniformIDs), (string s) => Shader.PropertyToID(s));
                InitializeStaticFields(typeof(Kernels), (string s) => s_ComputeShader.FindKernel(s));
            }
        }
        void StoreOffsetHistoryForMotionVectors(CommandBuffer cmd)
        {
            
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kUpdatePreviousPosition, UniformIDs._ReservedPagesBuffer, m_PageIndicesBuffer[0]);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kUpdatePreviousPosition, UniformIDs._PerInstanceStateBufferRW, m_PerInstanceStateBuffer);
            cmd.DispatchCompute(s_ComputeShader, Kernels.kUpdatePreviousPosition, m_IndirectDispatchArgsBuffer, 0);
        }
        

        static void CopyBuffer(CommandBuffer cmd, GraphicsBuffer src, GraphicsBuffer dst, int srcOffsetInWords,
            int dstOffsetInWords, int copyCountInWords)
        {
            s_ComputeShader.GetKernelThreadGroupSizes(Kernels.kCopyBuffer, out var groupX, out var groupY, out var groupZ );
            int maximumNumberOfWordsToCopyPerDispatch = (int)(groupX * c_MaxDispatchSize);

            int wordsLeftToCopy =  copyCountInWords;
            int currentCopyBatchOffset = 0;
            
            while (wordsLeftToCopy > 0)
            {
                int batchSize = math.min(maximumNumberOfWordsToCopyPerDispatch, wordsLeftToCopy);
                cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kCopyBuffer, UniformIDs._CopyDstBuffer, dst);
                cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kCopyBuffer, UniformIDs._CopySrcBuffer, src);
                cmd.SetComputeIntParam(s_ComputeShader, UniformIDs._CopySrcOffsetInWords, srcOffsetInWords + currentCopyBatchOffset);
                cmd.SetComputeIntParam(s_ComputeShader, UniformIDs._CopyDstOffsetInWords, dstOffsetInWords + currentCopyBatchOffset);
                cmd.SetComputeIntParam(s_ComputeShader, UniformIDs._TotalWordCountToCopy, batchSize);
            
                cmd.DispatchCompute(s_ComputeShader, Kernels.kCopyBuffer, GetDispatchGroupsCount(Kernels.kCopyBuffer, (uint)batchSize), 1,1);

                currentCopyBatchOffset += batchSize;
                wordsLeftToCopy -= batchSize;
            }
            
            
        }
        
        public void AppendNewFreePages(CommandBuffer cmd, int freePageIndexOffset, int numberOfNewPages)
        {
            
            int[] parameters = { freePageIndexOffset, numberOfNewPages };
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kAppendFreePages, UniformIDs._FreePagesBufferRW, m_FreePagesBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kAppendFreePages, UniformIDs._Counters, m_CountersBuffer);
            cmd.SetComputeIntParams(s_ComputeShader, UniformIDs._FreePagesRange, parameters);
            cmd.DispatchCompute(s_ComputeShader, Kernels.kAppendFreePages, GetDispatchGroupsCount(Kernels.kAppendFreePages, (uint)numberOfNewPages), 1,1);
            
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kIncrementFreePagesCounter, UniformIDs._CountersRW, m_CountersBuffer);
            cmd.DispatchCompute(s_ComputeShader, Kernels.kIncrementFreePagesCounter, 1, 1, 1);
        }

        void ReserveTilePages(CommandBuffer cmd, NativeArray<int3> tilesToReserve, int tileCount)
        {
            EnsureScratchBuffer(tileCount * 3 * 4);

            cmd.SetBufferData(m_ScratchBuffer, tilesToReserve, 0, 0, tileCount);
            
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kReservePages, UniformIDs._TileIndexAndPageEntryCountsBuffer, m_ScratchBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kReservePages, UniformIDs._PerTileHeaderBufferRW, m_PerTileHeadersBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kReservePages, UniformIDs._CountersRW, m_CountersBuffer);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kReservePages, UniformIDs._ReservedPagesBufferRW, m_PageIndicesBuffer[0]);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kReservePages, UniformIDs._FreePagesBuffer, m_FreePagesBuffer);
            cmd.DispatchCompute(s_ComputeShader, Kernels.kReservePages, tileCount, 1, 1);
        }
        
        void FreeTilePages(CommandBuffer cmd, NativeArray<int> tilesToFree, int tilesToFreeCount)
        {
            //free pages
            {
                EnsureScratchBuffer(tilesToFreeCount * 4);
            
                cmd.SetBufferData(m_ScratchBuffer, tilesToFree, 0, 0, tilesToFreeCount);
                
                cmd.SetComputeIntParam(s_ComputeShader, UniformIDs._TilesToFreeCount, tilesToFreeCount);
                cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kFreePages, UniformIDs._TilesToFreeBuffer, m_ScratchBuffer);
                cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kFreePages, UniformIDs._PerTileHeaderBufferRW, m_PerTileHeadersBuffer);
                cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kFreePages, UniformIDs._CountersRW, m_CountersBuffer);
                cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kFreePages, UniformIDs._ReservedPagesBuffer, m_PageIndicesBuffer[0]);
                cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kFreePages, UniformIDs._FreePagesBufferRW, m_FreePagesBuffer);
                cmd.DispatchCompute(s_ComputeShader, Kernels.kFreePages, tilesToFreeCount, 1, 1);
            }

            //defragment
            {
                //reset defragment counter
                cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kResetDefragmentCounter, UniformIDs._CountersRW, m_CountersBuffer);
                cmd.DispatchCompute(s_ComputeShader, Kernels.kResetDefragmentCounter, 1, 1, 1);
                
                
                uint tilesToDefragment = (uint)m_PerTileHeadersBuffer.count;
                uint currentOffset = 0;
                
                while (currentOffset < tilesToDefragment)
                {
                    var currentDispatchSize = math.min(c_MaxDispatchSize, tilesToDefragment - currentOffset);
                    
                
                    cmd.SetComputeIntParam(s_ComputeShader, UniformIDs._DefragmentTileOffset, (int)currentOffset);
                    cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kDefragmentPages, UniformIDs._ReservedPagesToDefragment, m_PageIndicesBuffer[0]);
                    cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kDefragmentPages, UniformIDs._ReservedPagesBufferRW, m_PageIndicesBuffer[1]);
                    cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kDefragmentPages, UniformIDs._CountersRW, m_CountersBuffer);
                    cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kDefragmentPages, UniformIDs._PerTileHeaderBufferRW, m_PerTileHeadersBuffer);
                    cmd.DispatchCompute(s_ComputeShader, Kernels.kDefragmentPages, (int)currentDispatchSize, 1, 1);

                    currentOffset += currentDispatchSize;
                }
               
                //swap from previous to defragmented pages buffer
                CoreUtils.Swap(ref m_PageIndicesBuffer[0], ref m_PageIndicesBuffer[1]);

            }
            
        }
        
        private void InitializeGPU(CommandBuffer cmd, int2 numberOfTilesPerDimension, int2 globalTileDimensions)
        {
            StaticInitialize();

            int numberOfTiles = numberOfTilesPerDimension.x * numberOfTilesPerDimension.y;
            
            m_PerTileHeadersBuffer = CreateGraphicsBuffer(GraphicsBuffer.Target.Structured,
                numberOfTiles, UnsafeUtility.SizeOf<PerTileHeaderEntry>(), "PerTileHeaderBuffer");
            m_CountersBuffer =CreateGraphicsBuffer(GraphicsBuffer.Target.Structured, 2, sizeof(int), "CountersBuffer"); //counters for free, reserved pages

            m_UploadBatchInfoBuffer = CreateGraphicsBuffer(GraphicsBuffer.Target.Structured, c_MaxPagesToUploadPerFrame,
                UnsafeUtility.SizeOf<ScatteredInstanceDataUploadBatch>(), "UploadBatchBuffer");
            
            m_UploadBatchDataBuffer = CreateGraphicsBuffer(GraphicsBuffer.Target.Structured, c_MaxPagesToUploadPerFrame * GetPageSize(),
                UnsafeUtility.SizeOf<ScatteredInstancePropertiesPacked>(), "ScattaredInstancePropertiesUploadBuffer");

            m_ConstantsBuffer = CreateGraphicsBuffer(GraphicsBuffer.Target.Constant, 1,
                UnsafeUtility.SizeOf<ScatteredInstanceInteractionConstants>(), "ScatteredInstanceInteractionConstants");

            m_IndirectDispatchArgsBuffer = CreateGraphicsBuffer(GraphicsBuffer.Target.IndirectArguments, 4,
                sizeof(uint), "UpdateScatteredInstanceSimulationArgs");

            m_CollidersBuffer = CreateGraphicsBuffer(GraphicsBuffer.Target.Structured, 31,
                UnsafeUtility.SizeOf<CapsuleColliderEntry>(), "CapsuleCollidersBuffer");
            
            constants._ActiveGlobalTileDimensions = new int4(numberOfTilesPerDimension.x, numberOfTilesPerDimension.y, globalTileDimensions.x, globalTileDimensions.y);
            
            //reset counters
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kResetFreeAndReservedPageCounters, UniformIDs._CountersRW, m_CountersBuffer);
            cmd.DispatchCompute(s_ComputeShader, Kernels.kResetFreeAndReservedPageCounters, 1, 1, 1);
            
            cmd.SetComputeIntParam(s_ComputeShader, UniformIDs._TotalNumberOfTiles, numberOfTiles);
            cmd.SetComputeBufferParam(s_ComputeShader, Kernels.kResetPerTileHeaders, UniformIDs._PerTileHeaderBufferRW, m_PerTileHeadersBuffer);
            cmd.DispatchCompute(s_ComputeShader, Kernels.kResetPerTileHeaders, GetDispatchGroupsCount(Kernels.kResetPerTileHeaders, (uint)m_PerTileHeadersBuffer.count), 1, 1);
        }

        private void FreeGPUResources()
        {
            m_PerTileHeadersBuffer.Dispose();
            m_CountersBuffer.Dispose();
            
            m_PageIndicesBuffer[0].Dispose();
            m_PageIndicesBuffer[1].Dispose();
            m_FreePagesBuffer.Dispose();
            m_PerInstancePropertiesBuffer.Dispose();
            m_PerInstanceStateBuffer.Dispose();
            
            m_UploadBatchInfoBuffer.Dispose();
            m_UploadBatchDataBuffer.Dispose();
            
            m_IndirectDispatchArgsBuffer.Dispose();
            
            m_CollidersBuffer.Dispose();
            
            if (m_ScratchBuffer != null)
            {
                m_ScratchBuffer.Dispose();
            }
        }

        private void EnsureScratchBuffer(int sizeInBytes)
        {
            sizeInBytes = math.max(1, sizeInBytes);
            if (m_ScratchBuffer == null || !m_ScratchBuffer.IsValid() || m_ScratchBuffer.count < sizeInBytes)
            {
                if (m_ScratchBuffer != null && m_ScratchBuffer.IsValid())
                {
                    m_BuffersToRelease.Add(m_ScratchBuffer);
                }

                m_ScratchBuffer = CreateGraphicsBuffer(GraphicsBuffer.Target.Raw, (sizeInBytes + 3) / 4, 4, "Scratch");
            }
        }
        
        
        private void EnsurePerInstanceData(CommandBuffer cmd, int pagesNeeded)
        {
            int pageSize = GetPageSize();
            pagesNeeded = math.max(pagesNeeded, 1);
            
            if (m_PageIndicesBuffer[0] == null || !m_PageIndicesBuffer[0].IsValid() || pagesNeeded > m_PageIndicesBuffer[0].count)
            {
                int entryCount = pagesNeeded * pageSize;
                
                GraphicsBuffer newPageIndicesBuffer = CreateGraphicsBuffer(GraphicsBuffer.Target.Raw, pagesNeeded, sizeof(uint), "ReservedPageIndicesBuffer0");
                GraphicsBuffer newPageIndicesBuffer2 = CreateGraphicsBuffer(GraphicsBuffer.Target.Raw, pagesNeeded, sizeof(uint), "ReservedPageIndicesBuffer1");
                GraphicsBuffer newFreePagesBuffer = CreateGraphicsBuffer(GraphicsBuffer.Target.Raw, pagesNeeded, sizeof(uint), "FreePageIndicesBuffer");
                GraphicsBuffer newPerInstancePropertiesBuffer = CreateGraphicsBuffer(GraphicsBuffer.Target.Raw, entryCount,
                    UnsafeUtility.SizeOf<ScatteredInstancePropertiesPacked>(), "PerInstancePropertiesBuffer");
                GraphicsBuffer newPerInstanceStateBuffer = CreateGraphicsBuffer(GraphicsBuffer.Target.Raw, entryCount,
                    UnsafeUtility.SizeOf<ScatteredInstanceStatePacked>(), "PerInstanceStateBuffer");

                int oldPagesCount = 0;
                
                if (m_PageIndicesBuffer[0] != null && m_PageIndicesBuffer[0].IsValid())
                {

                    CopyBuffer(cmd, m_PageIndicesBuffer[0], newPageIndicesBuffer, 0, 0, m_PageIndicesBuffer[0].count);
                    CopyBuffer(cmd, m_FreePagesBuffer, newFreePagesBuffer, 0, 0, m_FreePagesBuffer.count);

                    oldPagesCount = m_FreePagesBuffer.count;
                    
                    int perInstancePropsWordCount = UnsafeUtility.SizeOf<ScatteredInstancePropertiesPacked>() / 4;
                    int perInstanceStateWordCount = UnsafeUtility.SizeOf<ScatteredInstanceStatePacked>() / 4;
                    
                    CopyBuffer(cmd, m_PerInstancePropertiesBuffer, newPerInstancePropertiesBuffer, 0, 0, m_PerInstancePropertiesBuffer.count * perInstancePropsWordCount);
                    CopyBuffer(cmd, m_PerInstanceStateBuffer, newPerInstanceStateBuffer, 0, 0, m_PerInstanceStateBuffer.count * perInstanceStateWordCount);
                    
                    
                    m_BuffersToRelease.Add(m_PageIndicesBuffer[0]);
                    m_BuffersToRelease.Add(m_PageIndicesBuffer[1]);
                    m_BuffersToRelease.Add(m_FreePagesBuffer);
                    m_BuffersToRelease.Add(m_PerInstancePropertiesBuffer);
                    m_BuffersToRelease.Add(m_PerInstanceStateBuffer);

                }
                
                m_PageIndicesBuffer[0] = newPageIndicesBuffer;
                m_PageIndicesBuffer[1] = newPageIndicesBuffer2;
                m_FreePagesBuffer = newFreePagesBuffer;
                m_PerInstancePropertiesBuffer = newPerInstancePropertiesBuffer;
                m_PerInstanceStateBuffer = newPerInstanceStateBuffer;

                int newPagesCount = m_FreePagesBuffer.count - oldPagesCount;
                if (newPagesCount > 0)
                {
                    AppendNewFreePages(cmd,oldPagesCount, m_FreePagesBuffer.count - oldPagesCount);
                }
                

            }

        }
        
        private void SetEnabled(bool enabled)
        {
            if (enabled)
            {
                Shader.EnableKeyword("SCATTERED_INSTANCE_INTERACTION_ENABLED");
            }
            else
            {
                Shader.DisableKeyword("SCATTERED_INSTANCE_INTERACTION_ENABLED");
            }
        }

        private void SetGlobalRenderingResources()
        {
            Shader.SetGlobalBuffer(UniformIDs._PerTileHeaderBuffer, m_PerTileHeadersBuffer);
            Shader.SetGlobalBuffer(UniformIDs._ReservedPagesBuffer, m_PageIndicesBuffer[0]);
            Shader.SetGlobalBuffer(UniformIDs._PerInstanceStateBuffer, m_PerInstanceStateBuffer);
            Shader.SetGlobalBuffer(UniformIDs._PerInstancePropertiesBuffer, m_PerInstancePropertiesBuffer);
            Shader.SetGlobalConstantBuffer(UniformIDs.ScatteredInstanceInteractionConstants, m_ConstantsBuffer, 0, m_ConstantsBuffer.stride);
        }

        #endregion   
    }
}