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
		private StarterAssetsInputs _input;
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

			// For first-person, position camera at player head
			if (_mainCamera != null)
			{
				_mainCamera.transform.SetParent(transform);
				_mainCamera.transform.localPosition = new Vector3(0, CameraHeight, 0);
				_mainCamera.transform.localRotation = Quaternion.identity;
			}
		}

		private void Start()
		{
			_hasAnimator = TryGetComponent(out _animator);
			_controller = GetComponent<CharacterController>();
			_input = GetComponent<StarterAssetsInputs>();

			AssignAnimationIDs();

			// Lock and hide cursor
			Cursor.lockState = CursorLockMode.Locked;
			Cursor.visible = false;
		}

		private void Update()
		{
			_hasAnimator = TryGetComponent(out _animator);

			GroundedCheck();
			Move();
			HandleInteraction();
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
			// First-person mouse look
			if (_input.look.sqrMagnitude >= _threshold)
			{
				float deltaTimeMultiplier = IsCurrentDeviceMouse ? 1.0f : Time.deltaTime;

				// Horizontal rotation (turn left/right)
				_cameraYaw += _input.look.x * deltaTimeMultiplier * LookSensitivity.x;

				// Vertical rotation (look up/down) - applied to camera only
				_cameraPitch -= _input.look.y * deltaTimeMultiplier * LookSensitivity.y;
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
			// Set target speed to walk speed only (no sprint)
			float targetSpeed = MoveSpeed;

			// If there is no input, set the target speed to 0
			if (_input.move == Vector2.zero) targetSpeed = 0.0f;

			float currentHorizontalSpeed = new Vector3(_controller.velocity.x, 0.0f, _controller.velocity.z).magnitude;

			float speedOffset = 0.1f;
			float inputMagnitude = _input.analogMovement ? _input.move.magnitude : 1f;

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

			// Get movement direction relative to where player is looking (camera forward)
			Vector3 inputDirection = new Vector3(_input.move.x, 0.0f, _input.move.y).normalized;

			// Transform input to world space using camera direction
			Vector3 moveDirection = Vector3.zero;
			if (inputDirection.magnitude > 0)
			{
				// Forward relative to camera yaw
				Vector3 cameraForward = new Vector3(
					Mathf.Sin(_cameraYaw * Mathf.Deg2Rad),
					0,
					Mathf.Cos(_cameraYaw * Mathf.Deg2Rad)
				).normalized;

				// Right relative to camera
				Vector3 cameraRight = new Vector3(
					Mathf.Cos(_cameraYaw * Mathf.Deg2Rad),
					0,
					-Mathf.Sin(_cameraYaw * Mathf.Deg2Rad)
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
			if (_input.interact)
			{
				// Raycast from camera for first-person interaction
				if (_mainCamera != null)
				{
					Ray ray = new Ray(_mainCamera.transform.position, _mainCamera.transform.forward);

					if (Physics.Raycast(ray, out RaycastHit hit, 3f))
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
