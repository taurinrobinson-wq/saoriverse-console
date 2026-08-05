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

#if ENABLE_INPUT_SYSTEM
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
                    move = context.ReadValue<Vector2>();
                    break;

                case "Look":
                    if (cursorInputForLook)
                    {
                        look = context.ReadValue<Vector2>();
                    }
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
            }
        }
#else
        private void Update()
        {
            // Old input system fallback
            move = new Vector2(Input.GetAxis("Horizontal"), Input.GetAxis("Vertical"));
            look = new Vector2(Input.GetAxis("Mouse X"), Input.GetAxis("Mouse Y"));
            jump = Input.GetKeyDown(KeyCode.Space);
            sprint = Input.GetKey(KeyCode.LeftShift);
            interact = Input.GetKeyDown(KeyCode.E);
        }
#endif

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
