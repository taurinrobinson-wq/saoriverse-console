# DraftShift Renamer - Replit Setup Guide

This guide covers setting up the DraftShift Renamer on a dedicated Replit project.

## Quick Setup for New Replit Project

### Step 1: Configure `.replit` file

Create a `.replit` file in the **root** of your Replit project with:

```toml
run = "cd draftshift-web && python run_server.py"
```

### Step 2: Ensure Project Structure

Your Replit project should have this structure:
```
/
├── .replit                    (configuration file)
├── replit.nix                (Nix environment)
├── draftshift-web/
│   ├── api.py               (FastAPI server)
│   ├── run_server.py        (startup script)
│   ├── filename_normalizer.py
│   ├── renamer_service.py
│   ├── requirements.txt
│   ├── package.json
│   ├── src/
│   │   └── (React components)
│   ├── public/
│   └── dist/                (built React - auto-generated)
```

### Step 3: Click "Run" on Replit

When you click **Run**, the sequence will be:

1. ✅ Change to `draftshift-web` directory 2. ✅ Check for `node_modules` → auto-install if missing 3.
✅ Check for `dist/` → auto-build if missing 4. ✅ Install Python dependencies (`pip install -r
requirements.txt`) 5. ✅ Start FastAPI server on port 8000 6. ✅ Serve React UI from `/`

### Step 4: Access Your App

Once running, your app will be available at:
- **https://DraftShift.replit.dev** (or whatever your Replit URL is)

You should see:
- **📋 Document Builder** tab
- **📁 File Renamer** tab (batch renaming tool)

## Troubleshooting

### Error: "Disk quota exceeded"
- **Solution**: Make sure `node_modules/` and `package-lock.json` are in `.gitignore`
- Don't commit these large folders to git

### Error: "Module not found"
- **Solution**: Make sure `run_server.py` is in `draftshift-web/` directory
- Check that file contains the startup logic with npm/build checks

### Error: "Port 8000 already in use"
- **Solution**: Replit automatically handles this, but if stuck:
  - Stop the running process and click "Run" again

### React not loading
- **Solution**: Check that `npm run build` succeeded
- Look for `draftshift-web/dist/` folder
- If missing, `run_server.py` will build it automatically

## What run_server.py Does

```python
## Checks if node_modules exists
if not os.path.exists("node_modules"):
    subprocess.run("npm install", shell=True)

## Checks if dist/ exists  
if not os.path.exists("dist"):
    subprocess.run("npm run build", shell=True)

## Then starts FastAPI server
uvicorn.run(app, host="0.0.0.0", port=8000)
```

This ensures everything is ready before the server starts.

## File Upload Testing

Once running, test the renamer with:

1. Click **📁 File Renamer** tab 2. Drag and drop a document (PDF, DOCX, TXT, etc.) 3. See preview
with:
   - Original filename
   - Renamed to: `YYMMDD – Document_Type.ext`
   - Detected date
   - Confidence score
4. Click **Download Renamed Files** to get ZIP

## Deployment Checklist

- [ ] `.replit` file exists in root
- [ ] `replit.nix` exists in root
- [ ] `draftshift-web/` folder contains all code
- [ ] `draftshift-web/run_server.py` exists
- [ ] `draftshift-web/requirements.txt` has all Python deps
- [ ] `draftshift-web/package.json` has all npm deps
- [ ] `node_modules/` is in `.gitignore`
- [ ] `package-lock.json` is in `.gitignore`
- [ ] All code committed to GitHub
- [ ] Replit project connected to GitHub repo

Once all checked, click **Run** on Replit!

---

## Still Having Issues?

Check these common problems:

1. **No `.replit` file** → Create one at project root with run command 2. **Wrong directory** → Make
sure you're running from root, not `draftshift-web/` 3. **Old Replit environment** → Clear cache or
reimport from GitHub fresh 4. **Missing dependencies** → Check `requirements.txt` and `package.json`
are complete

See [DEPLOYMENT_CHECKLIST.md](draftshift-web/DEPLOYMENT_CHECKLIST.md) for more detailed
troubleshooting.
