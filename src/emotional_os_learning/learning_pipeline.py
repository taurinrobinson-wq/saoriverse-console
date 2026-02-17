"""Background Learning Pipeline for FirstPerson.

Offline consolidation of proto-glyphs into new glyphs.
Runs asynchronously, never blocks conversation.

Schedule: Hourly or daily consolidation pass
Result: New glyphs added to emotional OS
"""

import asyncio
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import time
from threading import Thread, Event


class BackgroundLearningPipeline:
    """Background consolidation pipeline.
    
    Periodically:
    1. Cluster proto-glyphs
    2. Identify synthesis candidates
    3. Synthesize complex patterns
    4. Promote to glyphs
    5. Update emotional OS
    """

    def __init__(
        self,
        proto_manager,
        glyph_synthesizer=None,
        consolidation_interval_hours: int = 1,
    ):
        """Initialize learning pipeline.
        
        Args:
            proto_manager: ProtoGlyphManager instance
            glyph_synthesizer: Optional GlyphSynthesizer for OpenAI synthesis
            consolidation_interval_hours: How often to run consolidation (default: 1 hour)
        """
        self.proto_manager = proto_manager
        self.synthesizer = glyph_synthesizer
        self.consolidation_interval = consolidation_interval_hours * 3600  # Convert to seconds
        self.running = False
        self.last_consolidation = None
        self.consolidation_count = 0
        self.thread = None
        self.stop_event = Event()
        self.glyphs_created = []

    def run_periodic_consolidation(self) -> None:
        """Start the background consolidation loop.
        
        Runs in a separate thread, never blocks main conversation.
        Call once at startup.
        """
        if self.running:
            return  # Already running
        
        self.running = True
        self.stop_event.clear()
        self.thread = Thread(target=self._consolidation_loop, daemon=True)
        self.thread.start()
        print("[Learning] Background consolidation pipeline started")

    def _consolidation_loop(self) -> None:
        """Main background consolidation loop."""
        while not self.stop_event.is_set():
            try:
                # Sleep until next consolidation time
                time.sleep(self.consolidation_interval)
                
                if self.stop_event.is_set():
                    break
                
                # Run consolidation
                self.consolidate_once()
                
            except Exception as e:
                print(f"[Learning] Error in consolidation loop: {e}")
                time.sleep(60)  # Wait before retrying

    def consolidate_once(self) -> Dict:
        """Run one consolidation pass.
        
        Returns:
            Dictionary with consolidation results
        """
        print(f"[Learning] Starting consolidation pass #{self.consolidation_count + 1}")
        start_time = time.time()
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "proto_count_before": len(self.proto_manager.proto_glyphs),
            "glyphs_created": 0,
            "glyphs_synthesized": 0,
            "processing_time_s": 0.0,
        }
        
        # Step 1: Cluster proto-glyphs
        print("[Learning]   Clustering proto-glyphs...")
        clusters = self.proto_manager.cluster_proto_glyphs(
            similarity_threshold=0.8,
            min_cluster_size=2,
        )
        print(f"[Learning]   Found {len(clusters)} clusters")
        
        # Step 2: Get stable clusters
        print("[Learning]   Identifying stable clusters...")
        stable_clusters = self.proto_manager.get_stable_clusters(
            stability_threshold=0.75,
            min_size=3,
        )
        print(f"[Learning]   Found {len(stable_clusters)} stable clusters")
        
        # Step 3: Create glyphs from stable clusters
        for cluster in stable_clusters:
            glyph = self._synthesize_and_promote(
                cluster=cluster,
                use_openai=True,
            )
            
            if glyph:
                result["glyphs_created"] += 1
                self.glyphs_created.append(glyph)
                print(f"[Learning]   Created glyph: {glyph['name']}")
        
        # Step 4: Update metadata
        result["processing_time_s"] = time.time() - start_time
        result["proto_count_after"] = len([p for p in self.proto_manager.proto_glyphs.values() if not p.promoted])
        
        self.last_consolidation = datetime.now()
        self.consolidation_count += 1
        
        print(f"[Learning]   Consolidation complete. Created {result['glyphs_created']} glyphs in {result['processing_time_s']:.2f}s")
        
        return result

    def _synthesize_and_promote(
        self,
        cluster,
        use_openai: bool = True,
    ) -> Optional[Dict]:
        """Synthesize a new glyph from cluster and promote it."""
        # Collect examples from cluster
        examples = []
        for proto_id in cluster.proto_ids:
            proto = self.proto_manager.proto_glyphs[proto_id]
            examples.extend(proto.example_texts[:3])  # Keep top 3 per proto
        
        # Check if OpenAI synthesis is needed
        if use_openai and self.synthesizer:
            print(f"[Learning]   Synthesizing with OpenAI...")
            glyph_data = self.synthesizer.synthesize_from_cluster(
                cluster_centroid=cluster.centroid,
                example_texts=examples,
                existing_glyphs={},  # Would pass actual glyphs here
            )
            
            if not glyph_data:
                print(f"[Learning]   OpenAI synthesis failed, using local synthesis")
                return self._synthesize_local(cluster, examples)
            
            # Promote OpenAI-synthesized glyph
            return self.proto_manager.promote_to_glyph(
                cluster=cluster,
                glyph_name=glyph_data["name"],
                glyph_symbol=glyph_data["symbol"],
                gate_logic=glyph_data.get("gate_logic", {}),
            )
        else:
            # Use local synthesis
            return self._synthesize_local(cluster, examples)

    def _synthesize_local(
        self,
        cluster,
        examples: List[str],
    ) -> Dict:
        """Synthesize glyph using local tools only."""
        # Simple local synthesis: name based on dominant emotions
        emotion_names = {
            0: "Anger", 1: "Joy", 2: "Trust", 3: "Fear",
            4: "Surprise", 5: "Sadness", 6: "Disgust", 7: "Anticipation",
        }
        
        import numpy as np
        dominant_idx = np.argmax(cluster.centroid[:8])
        dominant_emotion = emotion_names.get(dominant_idx, "Unknown")
        
        glyph_name = f"Wave of {dominant_emotion}"
        glyph_symbol = "~"
        
        return self.proto_manager.promote_to_glyph(
            cluster=cluster,
            glyph_name=glyph_name,
            glyph_symbol=glyph_symbol,
            gate_logic={"trigger_threshold": 0.7},
        )

    def stop(self) -> Dict:
        """Stop the background pipeline gracefully."""
        print("[Learning] Stopping consolidation pipeline...")
        self.stop_event.set()
        
        if self.thread:
            self.thread.join(timeout=5)
        
        self.running = False
        
        return {
            "consolidation_passes": self.consolidation_count,
            "glyphs_created": len(self.glyphs_created),
            "last_consolidation": self.last_consolidation.isoformat() if self.last_consolidation else None,
        }

    def get_status(self) -> Dict:
        """Get current pipeline status."""
        return {
            "running": self.running,
            "consolidation_passes": self.consolidation_count,
            "glyphs_created": len(self.glyphs_created),
            "last_consolidation": self.last_consolidation.isoformat() if self.last_consolidation else None,
            "consolidation_interval_hours": self.consolidation_interval / 3600,
            "proto_count": len(self.proto_manager.proto_glyphs),
        }