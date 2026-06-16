using UnityEngine;
using Velinor.Core;

namespace StarterAssets
{
	[RequireComponent(typeof(SphereCollider))]
	public class InteractableObject : MonoBehaviour, IInteractable
	{
		[Header("Interaction")]
		[SerializeField] protected string interactPrompt = "Press E to interact";
		[SerializeField] protected float interactionRadius = 2f;

		[Header("Effects")]
		[SerializeField] protected GameObject particleEffectPrefab;
		[SerializeField] protected AudioClip interactionSound;

		protected AudioSource audioSource;
		protected SphereCollider triggerCollider;

		protected virtual void Start()
		{
			audioSource = GetComponent<AudioSource>();
			if (audioSource == null)
			{
				audioSource = gameObject.AddComponent<AudioSource>();
			}

			triggerCollider = GetComponent<SphereCollider>();
			if (triggerCollider != null)
			{
				triggerCollider.isTrigger = true;
				triggerCollider.radius = interactionRadius;
			}
		}

		public virtual void Interact(GameObject player)
		{
			Debug.Log($"Interacting with {gameObject.name}");

			// Play particle effect
			if (particleEffectPrefab != null)
			{
				Instantiate(particleEffectPrefab, transform.position, Quaternion.identity);
			}

			// Play sound
			if (interactionSound != null && audioSource != null)
			{
				audioSource.PlayOneShot(interactionSound);
			}
		}

		protected virtual void OnTriggerEnter(Collider other)
		{
			if (other.CompareTag("Player"))
			{
				OnPlayerEnter(other.gameObject);
			}
		}

		protected virtual void OnTriggerExit(Collider other)
		{
			if (other.CompareTag("Player"))
			{
				OnPlayerExit(other.gameObject);
			}
		}

		protected virtual void OnPlayerEnter(GameObject player)
		{
			// Override in subclasses
		}

		protected virtual void OnPlayerExit(GameObject player)
		{
			// Override in subclasses
		}
	}
}
