# FirstPerson System on External Drive

## ✅ Status: Configured for External Storage

Your FirstPerson local emotional processing system has been successfully moved to your external hard
drive to conserve local storage.

##

## 📍 Location Setup

### Local Machine

```text
```


/Users/taurinrobinson/saoriverse-console
├── parser/                    (code - ~245MB)
├── .venv → symlink to external ↓
├── data → symlink to external ↓
└── setup_external.sh (setup script)

```



### External Drive: "My Passport for Mac"
```text

```text
```


/Volumes/My Passport for Mac/FirstPerson
├── venv/                      (~1.2GB Python environment)
├── data/                      (~500MB, grows with data)
└── saoriverse-console/        (backup copy)

```



##

## 💾 Storage Savings

| Location | Space Used | Space Freed |
|----------|-----------|------------|
| **Before** | 1.9GB (local machine) | - |
| **After** | 245MB (local) | **1.65GB freed** |
| **Moved** | 1.7GB (external drive) | - |

**Result**: Freed up ~1.65GB on your local machine! 🎉
##

## 🚀 How to Use

### 1. Mount External Drive

The external drive should auto-mount when connected. To verify:

```bash

ls /Volumes/

```text
```text

```

### 2. Run Setup Script (if needed)

```bash


cd /Users/taurinrobinson/saoriverse-console

```text
```


This script:

- Verifies external drive is mounted
- Checks all symlinks are in place
- Shows system status
- Ready to run!

### 3. Start FirstPerson

Once external drive is mounted:

```bash
cd /Users/taurinrobinson/saoriverse-console
```sql

```sql
```


Then in Streamlit sidebar, select **"Local Mode"** for full sovereignty!

### 4. Run Tests

```bash

cd /Users/taurinrobinson/saoriverse-console

```text

```

##

## 🔗 How Symlinks Work

Your local project uses **symbolic links** (symlinks) to point to files on the external drive:

```bash


## Local machine
/Users/taurinrobinson/saoriverse-console/.venv → Points to external drive /Volumes/My Passport for
Mac/FirstPerson/venv

/Users/taurinrobinson/saoriverse-console/data → Points to external drive

```text
```text

```

**Benefits:**

- ✅ Code changes sync automatically
- ✅ Works transparently (you don't notice the symlink)
- ✅ External drive storage for large files
- ✅ Local machine stays clean

**View symlinks:**

```bash


cd /Users/taurinrobinson/saoriverse-console

```text
```


##

## ⚠️ Important Notes

### External Drive Must Be Mounted

FirstPerson **requires** the external drive to be mounted to run:

```bash

## If external drive isn't mounted:
cd /Users/taurinrobinson/saoriverse-console
.venv/bin/python test_local_mode.py

```text

```text
```


**Solution**: Connect external drive, it will auto-mount.

If it doesn't auto-mount:

```bash


## Manual mount command

```text

```

### Python Paths Are Fixed

The Python environment on the external drive has **absolute paths** baked in. This means:

- ✅ Works fine as long as external drive path stays the same
- ⚠️ If you move the folder on external drive, symlinks break
- ⚠️ If you change external drive names, update symlinks

### Git Works Normally

The `.git` folder is still on your local machine, so Git works normally:

```bash

cd /Users/taurinrobinson/saoriverse-console git status git add . git commit -m "message"

```text
```text

```

All code changes sync to Git regardless of external storage.

##

## 🔧 Troubleshooting

### "Permission denied" errors

```bash



## Fix permissions on external drive
chmod -R 755 "/Volumes/My Passport for Mac/FirstPerson"

```text
```


### Symlinks broken

```bash

## Check if external drive is mounted
ls /Volumes/ | grep "My Passport"

## If not mounted, connect it or run:
diskutil mount "/Volumes/My Passport for Mac"

## Verify symlinks
cd /Users/taurinrobinson/saoriverse-console
```text

```text
```


### Still can't run?

```bash


## Run the setup script to fix everything
cd /Users/taurinrobinson/saoriverse-console

```text

```

##

## 📊 Backup Considerations

Since your data is now on an external drive:

### Data to Backup

- `data/lexicons/` - Your emotion keywords
- `data/poetry/` - Your poetry enrichment
- `parser/learned_lexicon.json` - Learned patterns

### How to Backup

```bash


## All FirstPerson data
cp -r "/Volumes/My Passport for Mac/FirstPerson" /Volumes/[another-drive]/FirstPerson-backup

## Just data

```text
```text

```

##

## 🌍 Using From Different Locations

### Home (Local Machine)

Everything works as-is since external drive is mounted.

### Work (Different Mac)

You'll need to:

1. Connect external drive to work Mac
2. Clone the repo: `git clone [repo-url]`
3. Create symlinks pointing to external drive
4. Run: `./setup_external.sh`

### Without External Drive

For quick testing, you can:

```bash



## Copy venv locally (1.2GB)
cp -r "/Volumes/My Passport for Mac/FirstPerson/venv" /Users/taurinrobinson/saoriverse-console/.venv

## Remove symlink, use local copy
cd /Users/taurinrobinson/saoriverse-console rm .venv

## Now use local .venv

```text
```


Then move it back to external:

```bash
rm -rf .venv
```text

```text
```


##

## 📈 What's on External Drive

### Virtual Environment (~1.2GB)

- Python 3.8
- spaCy + models
- NLTK + corpora
- All dependencies
- Binary files (cannot easily compress)

### Data Directory (~500MB now, grows)

- `lexicons/nrc_emotion_lexicon_bootstrap.txt` - Current
- Space for full NRC lexicon (14,182 words)
- Poetry database (when added)
- User interaction history
- Metaphor database (when added)

### Backup Copy (~245MB)

- Original project code
- Useful for recovery

##

## 🎯 Quick Commands Reference

```bash


## Check setup
cd /Users/taurinrobinson/saoriverse-console
./setup_external.sh

## Run tests
.venv/bin/python test_local_mode.py

## Start FirstPerson
.venv/bin/streamlit run main_v2.py  # (ARCHIVED: emotional_os_ui_v2.py)

## Check external drive
du -sh "/Volumes/My Passport for Mac/FirstPerson"

## Verify symlinks (2)
ls -la .venv data

## Check if mounted
mount | grep "My Passport"

```


##

## ✨ Summary

Your FirstPerson system is now:

✅ Running on external drive for storage efficiency ✅ Accessible from local machine via symlinks ✅
All functionality preserved ✅ ~1.65GB freed on local machine ✅ Ready for poetry enrichment (data
grows as needed)

**Everything works the same way - just more storage-efficient!** 🚀
