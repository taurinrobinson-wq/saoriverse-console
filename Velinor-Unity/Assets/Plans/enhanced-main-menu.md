# Velinor Title Screen & Persistence Architecture

## Project Overview
- **Game Title:** Velinor
- **Platform:** PC (Windows Standalone)
- **Input System:** New Input System
- **Render Pipeline:** URP (Ultra)

## 1. Persistence Architecture (Tri-Tier)
The system uses three distinct categories of persistent JSON data stored in `Application.persistentDataPath`. Every file includes an integer `schemaVersion`.

### A. Global Settings (`settings.json`)
- **Ownership:** `SettingsManager`
- **Contents:** Installation-level preferences (Audio volumes, Resolution, Fullscreen, Active Profile Slot).
- **Behavior:** Persists independently of profiles. Available on first launch.

### B. Global Meta-Progress (`meta_progress.json`)
- **Ownership:** `MetaProgressManager`
- **Contents:** Account-wide unlocks (Asset Gallery, NPC Biographies, Endings, Completion status).
- **Behavior:** Unlocks are earned by any profile but stored globally.

### C. Individual Profile Data (`profiles/profile_01.json` etc.)
- **Ownership:** `ProfileManager`
- **Slots:** 3 fixed slots. Filenames are stable (`profile_01.json`) and do not change on rename.
- **Contents:** 
    - Display Name (player-chosen).
    - Status: `gameStarted`, `hasValidContinuePoint`.
    - Progression: `lastSavedScene`, `lastSpawnID`.
    - Inventory: `quantities`, `learnedSchematicIds`.
    - Economy: `Bits` (Currency).
    - Stats: `playerTone`, `npcRemnants`.
    - Narrative: `GameFlags`, `DiaryEntries`, `CodexState` (Tags, Glyphs).
    - Meta: `playtime`, `lastSaveTimestamp`.

## 2. Core UI Flows

### Main Title Presentation
- The screen remains cinematic (Existing Logo, Ambience, Eyes Closed).
- Options: [NEW GAME or CONTINUE], [PROFILE], [SETTINGS], [EXTRAS].
- The first button toggles between NEW GAME and CONTINUE based specifically on the active profile's `hasValidContinuePoint`.

### New Game Sequence (Production)
1. Player selects **NEW GAME**.
2. **Slot Selection:**
   - If no production profile is active: Automatically target the first available empty slot and open **Profile Entry Overlay**.
   - If no empty slot exists and all three production slots are occupied: Open **Profile Management** instead (no auto-overwrite).
   - If an active profile is selected and has progress and NEW GAME would reset that same profile: Show **Overwrite Warning** (identifying the specific profile). The presence of progress in some other profile must not trigger an overwrite warning for the current operation.
3. **Profile Entry:** Physical keyboard input, 16 char max.
4. **Activation:** After successful creation, make that profile active and continue automatically into the transition sequence.
5. **Transition:** Hide UI Panels -> Delay (0.5s) -> **Eye Opening Animation** -> **Glitch Transition** -> Load opening scene.
6. **Initialization:** The first valid continue point (`hasValidContinuePoint = true`) is created only after the opening gameplay scene has loaded and reached its safe initialization point. Profile creation alone does not establish a continue point.

### Continue Sequence (Production)
1. Player selects **CONTINUE** (Only available if `hasValidContinuePoint` is true).
2. Disable menu input -> Hide UI -> Play **Eye Opening Animation** immediately.
3. **Glitch Transition** -> Load `lastSavedScene` and teleport to `lastSpawnID`.

### Profile Management Panel
- Accessed via **PROFILE**. Shows 3 slots.
- Occupied slots display: Name, Location, Playtime.
- Sub-modal for occupied slots: [Activate/Continue], [Rename], [Delete (requires confirmation)], [Back].
- Renaming only updates the internal `displayName` without changing the filename.

### Settings Panel (Staged)
- **Staging:** Changes apply to a `WorkingSettings` object and preview immediately (Audio/Resolution).
- **Display Preview:** Resolution/Fullscreen changes trigger a confirmation modal with a 15s countdown. **KEEP** accepts into `WorkingSettings` but does NOT write to `settings.json`.
- **Confirm:** Saves `WorkingSettings` to `settings.json`.
- **Cancel:** Discards `WorkingSettings`. Restores values from `LastSavedSettings`.
- **Reset:** Reverts `WorkingSettings` to project defaults.

## 3. Development & Testing Overrides

### Centralized Override System
- **Class:** `DevelopmentOverrides` (Editor-only ScriptableObject).
- **Availability:** Restricted via `#if UNITY_EDITOR`. Controls are excluded from release builds.
- **Effective State:** `effective access = production access OR applicable development override`.
- **Suppression:** "Disable Save Writes" is enabled by default in Editor to prevent profile contamination. Separate permissions exist for [Production Profiles], [Test Profile], [Global Settings], and [Meta Progress].

### Override Categories
- **Profile/Save:** Bypass profile requirement, use Dedicated Test Profile (`development/test_profile.json`), separate from the 3 production slots.
- **Progression:** Ignore locks, override `GameFlags`, bypass scene-entry requirements.
- **Inventory:** Unlock Inventory, unlock all schematics, grant test items/tools, set Bits.
- **Extras:** Unlock all Gallery/Bios, mark game completed.
- **Scene Testing:** Start directly in any scene from Editor. Uses **Bootstrap Logic** to initialize persistent managers automatically.

## 4. Implementation Responsibilities & Snapshots

### Profile Snapshot Architecture
1. **Save Coordinator:** Scans participating systems to gather/restore state.
2. **Participating Systems:** `InventoryService`, `CurrencySystem` (Bits), `StatManager`, `DiaryManager`, `GameFlags`, `CodexManager`.
3. **State Integrity:** Snapshot captures production state. Overrides only affect "Effective State" during the session.
4. **Authoritative Migration:** Existing PlayerPrefs (`CurrencySystem`) and fixed JSON files (`DiaryManager`) will be migrated into the unified Profile DTO. There will be only one authoritative persisted value for Bits after migration.

### Initialization Order
1. `SettingsManager` (Load Global)
2. `DevelopmentOverrides` (Apply Editor bypasses)
3. `ProfileManager` (Restore Profile or Test Profile)
4. Subsystems (`Inventory`, `Currency`, `Stats`, etc. restore from Snapshot)
5. Scene Content (Evaluates `EffectiveState`)

## 5. Implementation Order
1. Audit & finalize DTO models (Schema Versioning & `hasValidContinuePoint`).
2. Implement `DevelopmentOverrides` and Save-Write Protection.
3. Implement `SettingsManager` with Staging and Resolution Reversion (KEEP != Save).
4. Implement `ProfileManager` (3 slots, stable filenames, sanitization).
5. Build `SaveCoordinator` (Snapshot capture/restore).
6. Migrate `DiaryManager`, `CurrencySystem`, `StatManager`, `GameFlags` to Profile DTO.
7. Update `TitleScreenManager` (Sequencing and Slot selection logic).
8. Create UI Prefabs (`UI_ProfilePanel`, `UI_SettingsPanel`, `UI_ExtrasPanel`).
9. Finalize Editor Tooling and Presets.

## 6. Verification Plan

### Production Tests
- **First Launch:** No data, verify title presentation.
- **Settings:** Staging, Confirmation, Cancellation, Resolution REVERT/Timeout (Verify `settings.json` is not written on KEEP).
- **Profiles:** Slot creation, auto-selection, Overwrite warning (current profile only), Renaming (displayName only), Deletion confirmation.
- **Persistence:** Save during gameplay (Establishing `hasValidContinuePoint`), restart app, CONTINUE loads correct checkpoint.
- **Corruption:** Verify malformed JSON doesn't crash the game or wipe data.

### Development Tests
- **Direct Scene Play:** Enter Play Mode from `InsideMarket_02` directly; verify managers initialize via bootstrap.
- **Write Protection:** Change inventory with writes disabled; verify production profile remains unchanged.
- **State Separation:** Verify overrides don't contaminate persistent files.
- **Release Safety:** Build project; verify no debug UI, test profiles, or bypasses are present.
