using UnityEngine;
using System;

namespace Velinor.Economy
{
    /// <summary>
    /// Tracks player currency (Bits) across scenes.
    /// 
    /// Bits are abstract currency established in dialogue:
    /// "Bits? Yeah. Money. You seriously got nothin'?"
    /// 
    /// The game does NOT model:
    /// - Physical coin denominations
    /// - Banking systems
    /// - Currency backing or historical origin
    /// 
    /// The game models ONLY:
    /// 1. Bits are the unit of exchange in the marketplace
    /// 2. Lioren earns them through trade, salvage, and work
    /// 3. Bits are exchanged for goods, services, and tools
    /// 4. Who values what matters more than how many bits something costs
    /// </summary>
    public class CurrencySystem : MonoBehaviour
    {
        public static CurrencySystem Instance { get; private set; }

        [SerializeField] private int initialBits = 0;

        private int currentBits;

        public event Action<int, string> OnBitsEarned;   // amount, reason
        public event Action<int, string> OnBitsSpent;    // amount, reason
        public event Action<int> OnBitsChanged;          // new total

        public int CurrentBits
        {
            get => currentBits;
            private set => currentBits = Mathf.Max(0, value);
        }

        private const string BITS_SAVE_KEY = "velinor_bits_total";

        private void Awake()
        {
            if (Instance != null)
            {
                Destroy(gameObject);
                return;
            }

            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        private void Start()
        {
            LoadBits();
        }

        /// <summary>
        /// Earn bits from NPC trades, completed tasks, etc.
        /// Fired immediately on success and persisted.
        /// </summary>
        public void Earn(int amount, string reason)
        {
            if (amount <= 0)
            {
                Debug.LogWarning($"CurrencySystem.Earn: amount must be positive. Got {amount} for reason: {reason}");
                return;
            }

            CurrentBits += amount;
            OnBitsEarned?.Invoke(amount, reason);
            OnBitsChanged?.Invoke(CurrentBits);
            SaveBits();

            Debug.Log($"[CurrencySystem] Earned {amount} bits ({reason}). Total: {CurrentBits}");
        }

        /// <summary>
        /// Spend bits on purchases or services.
        /// Returns true if successful, false if insufficient funds.
        /// On success, fires events and persists.
        /// </summary>
        public bool Spend(int amount, string reason)
        {
            if (amount <= 0)
            {
                Debug.LogWarning($"CurrencySystem.Spend: amount must be positive. Got {amount} for reason: {reason}");
                return false;
            }

            if (CurrentBits < amount)
            {
                Debug.LogWarning($"[CurrencySystem] Insufficient bits. Need {amount}, have {CurrentBits}");
                return false;
            }

            CurrentBits -= amount;
            OnBitsSpent?.Invoke(amount, reason);
            OnBitsChanged?.Invoke(CurrentBits);
            SaveBits();

            Debug.Log($"[CurrencySystem] Spent {amount} bits ({reason}). Total: {CurrentBits}");
            return true;
        }

        /// <summary>
        /// Check if player has enough bits without spending.
        /// </summary>
        public bool CanAfford(int amount)
        {
            return CurrentBits >= amount;
        }

        /// <summary>
        /// Set bits directly (for testing, loading from save, or editor debugging).
        /// </summary>
        public void SetBits(int amount)
        {
            CurrentBits = Mathf.Max(0, amount);
            OnBitsChanged?.Invoke(CurrentBits);
            SaveBits();
        }

        private void SaveBits()
        {
            PlayerPrefs.SetInt(BITS_SAVE_KEY, CurrentBits);
            PlayerPrefs.Save();
        }

        private void LoadBits()
        {
            if (PlayerPrefs.HasKey(BITS_SAVE_KEY))
            {
                CurrentBits = PlayerPrefs.GetInt(BITS_SAVE_KEY);
            }
            else
            {
                CurrentBits = initialBits;
                SaveBits();
            }

            Debug.Log($"[CurrencySystem] Initialized with {CurrentBits} bits");
        }

        /// <summary>
        /// Reset to initial state (for testing or new game).
        /// </summary>
        public void ResetToInitial()
        {
            CurrentBits = initialBits;
            SaveBits();
            OnBitsChanged?.Invoke(CurrentBits);
            Debug.Log($"[CurrencySystem] Reset to {initialBits} bits");
        }
    }
}
