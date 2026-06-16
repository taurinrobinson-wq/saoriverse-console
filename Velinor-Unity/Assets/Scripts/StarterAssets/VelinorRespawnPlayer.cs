using UnityEngine;
using Velinor.Core;

namespace StarterAssets
{
	[RequireComponent(typeof(CharacterController))]
	public class VelinorRespawnPlayer : MonoBehaviour
	{
		[Tooltip("The Y position threshold at which the player will respawn.")]
		public float yThreshold = -5f;

		private Vector3 _startingPosition;
		private Quaternion _startingRotation;
		private CharacterController _characterController;
		private VelinorPlayerController _playerController;

		[SerializeField] private AudioClip respawnSound;

		private void Start()
		{
			_startingPosition = transform.position;
			_startingRotation = transform.rotation;

			_characterController = GetComponent<CharacterController>();
			_playerController = GetComponent<VelinorPlayerController>();

			if (_characterController == null)
			{
				Debug.LogError("CharacterController component is required for VelinorRespawnPlayer script!");
			}

			if (_playerController == null)
			{
				Debug.LogError("VelinorPlayerController component is required for VelinorRespawnPlayer!");
			}
		}

		private void Update()
		{
			if (transform.position.y < yThreshold)
			{
				Respawn();
			}
		}

		private void Respawn()
		{
			if (_characterController != null)
			{
				_characterController.enabled = false;
			}

			transform.position = _startingPosition;
			transform.rotation = _startingRotation;

			if (_characterController != null)
			{
				_characterController.enabled = true;
			}

			if (respawnSound != null)
			{
				AudioSource.PlayClipAtPoint(respawnSound, transform.position);
			}

			Debug.Log("Player respawned!");
		}
	}
}
