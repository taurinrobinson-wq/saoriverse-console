using UnityEngine;
using Velinor.Core;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace StarterAssets
{
	[RequireComponent(typeof(CharacterController))]
	public class VelinorPlayerController : MonoBehaviour
	{
		[Header("Player")]
		[Tooltip("Move speed of the character in m/s")]
		public float MoveSpeed = 2.0f;

		[Tooltip("Acceleration and deceleration")]
		public float SpeedChangeRate = 10.0f;

		[Header("Player Grounded")]
		[Tooltip("If the character is grounded or not")]
		public bool Grounded = true;

		[Tooltip("Useful for rough ground")]
		public float GroundedOffset = -0.14f;

		[Tooltip("The radius of the grounded check")]
		public float GroundedRadius = 0.28f;

		[Tooltip("What layers the character uses as ground")]
		public LayerMask GroundLayers;

		[Header("First-Person Camera")]
		[Tooltip("Height of camera from player root")]
		public float CameraHeight = 0.93f;

		[Tooltip("How far in degrees can you move the camera up")]
		public float TopClamp = 70.0f;

		[Tooltip("How far in degrees can you move the camera down")]
		public float BottomClamp = -30.0f;

		[Tooltip("Mouse look sensitivity")]
		public Vector2 LookSensitivity = new Vector2(7.5f, 5.0f);

		// camera
		private float _cameraPitch = 0.0f;
		private float _cameraYaw = 0.0f;

		// player
		private float _speed;
		private float _animationBlend;
		private float _verticalVelocity;
		private float _terminalVelocity = 53.0f;
		private float _gravity = -15.0f;

		// animation IDs
		private int _animIDSpeed;
		private int _animIDGrounded;
		private int _animIDMotionSpeed;

		private Animator _animator;
		private CharacterController _controller;
		private VelinorStarterAssetsInputs _input;
		private GameObject _mainCamera;

		private const float _threshold = 0.01f;
		private bool _hasAnimator;

		private bool IsCurrentDeviceMouse
		{
			get
			{
				return true; // Simplified: assume keyboard/mouse input
			}
		}

		private void Awake()
		{
			if (_mainCamera == null)
			{
				_mainCamera = GameObject.FindGameObjectWithTag("MainCamera");
			}

			// Smart camera positioning:
			// If camera is already far from player origin (third-person), leave it
			// Otherwise, position for first-person at player head
			if (_mainCamera != null)
			{
				float distFromOrigin = _mainCamera.transform.localPosition.magnitude;
				
				// If camera is more than 1 unit away, assume it's third-person and leave it alone
				if (distFromOrigin < 1f)
				{
					// First-person: position at player head
					_mainCamera.transform.SetParent(transform);
					_mainCamera.transform.localPosition = new Vector3(0, CameraHeight, 0);
					_mainCamera.transform.localRotation = Quaternion.identity;
				}
				// Else: camera is already positioned for third-person, don't override
			}
		}

		private void Start()
		{
			_hasAnimator = TryGetComponent(out _animator);
			_controller = GetComponent<CharacterController>();
			_input = GetComponent<VelinorStarterAssetsInputs>();

			AssignAnimationIDs();

			// For third-person, set camera to look slightly down at player
			// Check if camera is positioned for third-person
			if (_mainCamera != null)
			{
				float distFromOrigin = _mainCamera.transform.localPosition.magnitude;
				if (distFromOrigin > 1f)
				{
					// Third-person: look slightly downward
					_cameraPitch = -15f;
				}
			}
		}

		private void Update()
		{
			_hasAnimator = TryGetComponent(out _animator);

			// Hybrid Interaction Model: Cursor management
			if (_input.rightClickHeld)
			{
				Cursor.lockState = CursorLockMode.Locked;
				Cursor.visible = false;
			}
			else
			{
				Cursor.lockState = CursorLockMode.None;
				Cursor.visible = true;
			}

			GroundedCheck();
			Move();
			HandleInteraction();
            
            if (Time.frameCount % 60 == 0)
            {
                Debug.Log($"[VPC] Move Input: {_input.moveInput}, RightClick: {_input.rightClickHeld}, Grounded: {Grounded}, Speed: {_speed}");
            }
		}

		private void LateUpdate()
		{
			CameraRotation();
		}

		private void AssignAnimationIDs()
		{
			_animIDSpeed = Animator.StringToHash("Speed");
			_animIDGrounded = Animator.StringToHash("Grounded");
			_animIDMotionSpeed = Animator.StringToHash("MotionSpeed");
		}

		private void GroundedCheck()
		{
			Vector3 spherePosition = new Vector3(transform.position.x, transform.position.y - GroundedOffset,
				transform.position.z);
			Grounded = Physics.CheckSphere(spherePosition, GroundedRadius, GroundLayers,
				QueryTriggerInteraction.Ignore);

			if (_hasAnimator)
			{
				_animator.SetBool(_animIDGrounded, Grounded);
			}
		}

		private void CameraRotation()
		{
			// Hybrid Interaction Model: Get look input (only when right-click held)
			Vector2 lookInput = _input.GetLook();

			// First-person mouse look
			if (lookInput.sqrMagnitude >= _threshold)
			{
				float deltaTimeMultiplier = IsCurrentDeviceMouse ? 1.0f : Time.deltaTime;

				// Horizontal rotation (turn left/right)
				_cameraYaw += lookInput.x * deltaTimeMultiplier * LookSensitivity.x;

				// Vertical rotation (look up/down) - applied to camera only
				_cameraPitch -= lookInput.y * deltaTimeMultiplier * LookSensitivity.y;
				_cameraPitch = ClampAngle(_cameraPitch, BottomClamp, TopClamp);
			}

			// Apply rotation to main camera
			if (_mainCamera != null)
			{
				_mainCamera.transform.localRotation = Quaternion.Euler(_cameraPitch, _cameraYaw, 0.0f);
			}

			// Rotate player body to face camera direction (for animations and interactions)
			transform.rotation = Quaternion.Euler(0.0f, _cameraYaw, 0.0f);
		}

		private void Move()
		{
			// Hybrid Interaction Model: Get movement input (always active)
			Vector2 moveInput = _input.GetMove();

			// Set target speed to walk speed only (no sprint)
			float targetSpeed = MoveSpeed;

			// If there is no input, set the target speed to 0
			if (moveInput == Vector2.zero) targetSpeed = 0.0f;

			float currentHorizontalSpeed = new Vector3(_controller.velocity.x, 0.0f, _controller.velocity.z).magnitude;

			float speedOffset = 0.1f;
			float inputMagnitude = _input.analogMovement ? moveInput.magnitude : 1f;

			// Accelerate or decelerate to target speed
			if (currentHorizontalSpeed < targetSpeed - speedOffset ||
				currentHorizontalSpeed > targetSpeed + speedOffset)
			{
				_speed = Mathf.Lerp(currentHorizontalSpeed, targetSpeed * inputMagnitude,
					Time.deltaTime * SpeedChangeRate);

				_speed = Mathf.Round(_speed * 1000f) / 1000f;
			}
			else
			{
				_speed = targetSpeed;
			}

			_animationBlend = Mathf.Lerp(_animationBlend, targetSpeed, Time.deltaTime * SpeedChangeRate);
			if (_animationBlend < 0.01f) _animationBlend = 0f;

			// ISOMETRIC FIX: Use fixed camera angle (30 degrees) for consistent WASD mapping
			// This makes movement direction independent of camera yaw rotation
			Vector3 inputDirection = new Vector3(moveInput.x, 0.0f, moveInput.y).normalized;

			Vector3 moveDirection = Vector3.zero;
			if (inputDirection.magnitude > 0)
			{
				// For isometric: assume camera is looking at ~30 degree angle
				// Forward direction is toward +Z, Right is toward +X
				// This makes WASD always map to the same world directions
				const float isometricAngle = 0f; // 0 degrees = straight forward in world space
				
				Vector3 cameraForward = new Vector3(
					Mathf.Sin(isometricAngle * Mathf.Deg2Rad),
					0,
					Mathf.Cos(isometricAngle * Mathf.Deg2Rad)
				).normalized;

				Vector3 cameraRight = new Vector3(
					Mathf.Cos(isometricAngle * Mathf.Deg2Rad),
					0,
					-Mathf.Sin(isometricAngle * Mathf.Deg2Rad)
				).normalized;

				moveDirection = (cameraForward * inputDirection.z + cameraRight * inputDirection.x).normalized;
			}

			// Apply gravity
			if (Grounded && _verticalVelocity < 0.0f)
			{
				_verticalVelocity = -2f;
			}
			else if (!Grounded)
			{
				if (_verticalVelocity < _terminalVelocity)
				{
					_verticalVelocity += _gravity * Time.deltaTime;
				}
			}

			// Move the player
			_controller.Move(moveDirection * (_speed * Time.deltaTime) +
							 new Vector3(0.0f, _verticalVelocity, 0.0f) * Time.deltaTime);

			// Update animator
			if (_hasAnimator)
			{
				_animator.SetFloat(_animIDSpeed, _animationBlend);
				_animator.SetFloat(_animIDMotionSpeed, inputMagnitude);
			}
		}

		private static float ClampAngle(float lfAngle, float lfMin, float lfMax)
		{
			if (lfAngle < -360f) lfAngle += 360f;
			if (lfAngle > 360f) lfAngle -= 360f;
			return Mathf.Clamp(lfAngle, lfMin, lfMax);
		}

		private void HandleInteraction()
		{
			// Raycast from camera for hover-based interactables
			if (_mainCamera != null)
			{
				Ray ray = new Ray(_mainCamera.transform.position, _mainCamera.transform.forward);

				if (Physics.Raycast(ray, out RaycastHit hit, 5f))
				{
					IInteractable interactable = hit.collider.GetComponent<IInteractable>();
					if (interactable != null)
					{
						// Call OnHover if the interactable supports it
						if (interactable is IInteractableHoverable hoverableInteractable)
						{
							hoverableInteractable.OnHover();
						}

						// Hybrid Interaction Model: Left-click always available (when cursor visible)
						bool leftClickPressed = false;
#if ENABLE_INPUT_SYSTEM
						if (UnityEngine.InputSystem.Mouse.current != null)
						{
							leftClickPressed = UnityEngine.InputSystem.Mouse.current.leftButton.wasPressedThisFrame;
						}
#else
						leftClickPressed = Input.GetMouseButtonDown(0);
#endif

						if (leftClickPressed && Cursor.visible)
						{
							interactable.Interact(gameObject);
						}
					}
				}
			}

			// E-key interaction
			if (_input.interact)
			{
				bool interacted = false;

				// 1. Proximity check (new fallback)
				Collider[] nearby = Physics.OverlapSphere(transform.position, 3.0f);
				foreach (var col in nearby)
				{
					IInteractable interactable = col.GetComponent<IInteractable>();
					if (interactable != null)
					{
						interactable.Interact(gameObject);
						interacted = true;
						break;
					}
				}

				// 2. Raycast fallback if proximity didn't find anything
				if (!interacted && _mainCamera != null)
				{
					Ray ray = new Ray(_mainCamera.transform.position, _mainCamera.transform.forward);
					if (Physics.Raycast(ray, out RaycastHit hit, 5f))
					{
						IInteractable interactable = hit.collider.GetComponent<IInteractable>();
						if (interactable != null)
						{
							interactable.Interact(gameObject);
						}
					}
				}

				_input.interact = false; // Consume the input
			}
		}


		private void OnDrawGizmosSelected()
		{
			Color transparentGreen = new Color(0.0f, 1.0f, 0.0f, 0.35f);
			Color transparentRed = new Color(1.0f, 0.0f, 0.0f, 0.35f);

			if (Grounded) Gizmos.color = transparentGreen;
			else Gizmos.color = transparentRed;

			Gizmos.DrawSphere(
				new Vector3(transform.position.x, transform.position.y - GroundedOffset, transform.position.z),
				GroundedRadius);
		}
	}
}
