using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace StarterAssets
{
    public class VelinorStarterAssetsInputs : MonoBehaviour
    {
        [Header("Character Input Values")]
        public Vector2 move;
        public Vector2 look;
        public bool jump;
        public bool sprint;
        public bool interact;

        [Header("Hybrid Interaction Model")]
        [Tooltip("WASD movement is always enabled")]
        public Vector2 moveInput;

        [Tooltip("Camera look input (raw from mouse)")]
        public Vector2 lookInput;

        [Tooltip("True when right-click is held")]
        public bool rightClickHeld;

        [Header("Movement Settings")]
        public bool analogMovement;

        [Header("Mouse Cursor Settings")]
        public bool cursorLocked = true;
        public bool cursorInputForLook = true;

#if ENABLE_INPUT_SYSTEM
        private PlayerInput _playerInput;
#endif

        private void OnEnable()
        {
#if ENABLE_INPUT_SYSTEM
            _playerInput = GetComponent<PlayerInput>();
            if (_playerInput != null)
            {
                _playerInput.onActionTriggered += OnActionTriggered;
            }
#endif
        }

        private void OnDisable()
        {
#if ENABLE_INPUT_SYSTEM
            if (_playerInput != null)
            {
                _playerInput.onActionTriggered -= OnActionTriggered;
            }
#endif
        }

        private void Update()
        {
#if ENABLE_INPUT_SYSTEM
            // Track right-click using Input System
            if (Mouse.current != null)
            {
                rightClickHeld = Mouse.current.rightButton.isPressed;
            }
#else
            // Track right-click using old Input API
            rightClickHeld = Input.GetMouseButton(1);
#endif
        }

#if ENABLE_INPUT_SYSTEM
        public void OnMove(InputValue value)
        {
            moveInput = value.Get<Vector2>();
            move = moveInput; // Keep public field in sync
        }

        public void OnLook(InputValue value)
        {
            lookInput = value.Get<Vector2>();
        }

        public void OnJump(InputValue value)
        {
            jump = value.isPressed;
        }

        public void OnSprint(InputValue value)
        {
            sprint = value.isPressed;
        }

        public void OnInteract(InputValue value)
        {
            interact = value.isPressed;
        }

        private void OnActionTriggered(InputAction.CallbackContext context)
        {
            string actionName = context.action.name;

            switch (actionName)
            {
                case "Move":
                    moveInput = context.ReadValue<Vector2>();
                    move = moveInput;
                    break;

                case "Look":
                    lookInput = context.ReadValue<Vector2>();
                    look = GetLook(); // Apply right-click filter
                    break;

                case "Jump":
                    jump = context.performed;
                    break;

                case "Sprint":
                    sprint = context.performed;
                    break;

                case "Interact":
                    interact = context.performed;
                    break;
                    // Note: Right-click is tracked in Update() using Input.GetMouseButton(1)
                    // This works reliably across all input systems
            }
        }
#else
        private void UpdateFallbackInput()
        {
            // Old input system fallback
            moveInput = new Vector2(Input.GetAxis("Horizontal"), Input.GetAxis("Vertical"));
            move = moveInput; // Keep in sync
            
            lookInput = new Vector2(Input.GetAxis("Mouse X"), Input.GetAxis("Mouse Y"));
            look = GetLook(); // Apply right-click filter
            
            jump = Input.GetKeyDown(KeyCode.Space);
            sprint = Input.GetKey(KeyCode.LeftShift);
            interact = Input.GetKeyDown(KeyCode.E);
        }
#endif

        private void LateUpdate()
        {
            // Update fallback input after all input processing
#if !ENABLE_INPUT_SYSTEM
            UpdateFallbackInput();
#endif
        }

        /// <summary>
        /// Returns movement input. ALWAYS ACTIVE (not gated by right-click).
        /// </summary>
        public Vector2 GetMove()
        {
            return moveInput;
        }

        /// <summary>
        /// Returns camera look input. ONLY ACTIVE when right-click is held.
        /// </summary>
        public Vector2 GetLook()
        {
            if (rightClickHeld)
                return lookInput;
            else
                return Vector2.zero;
        }

        private void OnApplicationFocus(bool hasFocus)
        {
            SetCursorState(cursorLocked);
        }

        private void SetCursorState(bool newState)
        {
            Cursor.lockState = newState ? CursorLockMode.Locked : CursorLockMode.None;
        }

        // Mobile/UI input methods (called by UICanvasControllerInput)
        public void MoveInput(Vector2 newMoveDirection)
        {
            move = newMoveDirection;
        }

        public void LookInput(Vector2 newLookDirection)
        {
            look = newLookDirection;
        }

        public void JumpInput(bool newJumpState)
        {
            jump = newJumpState;
        }

        public void SprintInput(bool newSprintState)
        {
            sprint = newSprintState;
        }
    }
}
