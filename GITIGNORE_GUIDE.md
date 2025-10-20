# .gitignore Guide for SystemScanner

## Overview

The `.gitignore` file prevents unnecessary, sensitive, or generated files from being committed to version control.

## What Gets Ignored

### 1. **Python Build Artifacts** ❌
```
__pycache__/          # Python bytecode cache
*.pyc                 # Compiled Python files
*.pyo                 # Optimized Python files
*.egg-info/           # Package metadata
dist/                 # Distribution builds
build/                # Build artifacts
```

**Why**: These are automatically regenerated and should not be in version control.

### 2. **Virtual Environments** ❌
```
venv/
scanner_env/
.venv/
ENV/
```

**Why**: Virtual environments are user-specific and can be recreated with `pip install -r requirements.txt`.

### 3. **PyInstaller Builds** ❌
```
dist/
build/
*.exe (except SystemScanner.exe in releases)
```

**Why**: Executables are built from source and should be distributed via releases, not committed to repository.

### 4. **Test Files** ❌
```
test_*.pdf
test_*.csv
test_*.txt
test_security_report.pdf
workflow_test.pdf
```

**Why**: These are generated during testing and shouldn't clutter the repository.

### 5. **Scan Results & User Data** ❌
```
scan_results_*.txt
scan_results_*.csv
scan_results_*.pdf
SystemScan_Report_*.pdf
```

**Why**: Contains user-specific data and potentially sensitive system information.

### 6. **IDE/Editor Files** ❌
```
.vscode/              # Visual Studio Code
.idea/                # PyCharm/IntelliJ
*.sublime-project     # Sublime Text
*.swp                 # Vim
```

**Why**: IDE settings are user-specific preferences.

### 7. **Operating System Files** ❌
```
# Windows
Thumbs.db
Desktop.ini
*.lnk

# macOS
.DS_Store
.AppleDouble

# Linux
*~
.directory
```

**Why**: OS-specific files that don't belong in the project.

### 8. **Logs and Temporary Files** ❌
```
*.log
*.tmp
*.bak
debug.log
temp/
cache/
```

**Why**: Temporary files that change frequently and have no long-term value.

### 9. **Sensitive Data** ❌
```
*.key
*.pem
*.cert
secrets.*
.env
api_keys.txt
credentials.json
```

**Why**: **Security critical** - Never commit passwords, API keys, or certificates!

## What Gets Committed ✅

### Source Code ✅
```
check.py
pdf_reporter.py
system_info.py
```

### Documentation ✅
```
README.md
LICENSE
*.md files
CHANGELOG.md
```

### Configuration Templates ✅
```
requirements.txt
SystemScanner.spec
version_info.txt
app.manifest
```

### Build Scripts ✅
```
build.bat
setup.py (if created)
```

### Assets ✅
```
scanner.ico (if added)
images/ (if added)
```

## Special Cases

### PyInstaller Spec File
```python
# .gitignore includes:
*.spec.bak

# But keeps:
SystemScanner.spec  # This is committed
```

**Why**: The `.spec` file is configuration for building, but `.spec.bak` backups are ignored.

### Executable Files
```python
# Ignores all .exe files:
*.exe

# Except (if you want to commit a release):
!SystemScanner.exe
```

**Why**: Generally don't commit executables, but you could make an exception for official releases.

## Best Practices

### 1. **Never Commit Secrets** 🔒
```bash
# BAD - Never do this:
git add credentials.json
git add .env

# GOOD - Use .gitignore:
echo "credentials.json" >> .gitignore
echo ".env" >> .gitignore
```

### 2. **Don't Commit Build Artifacts** 🔨
```bash
# BAD:
git add dist/SystemScanner.exe
git add build/

# GOOD:
# These are already in .gitignore
# Use GitHub Releases for distributing builds
```

### 3. **Keep User Data Private** 🔐
```bash
# BAD:
git add scan_results_20251020_153000.pdf

# GOOD:
# Already ignored by pattern: scan_results_*.pdf
```

### 4. **Verify Before Committing** ✅
```bash
# Check what will be committed:
git status

# Check what's being ignored:
git status --ignored

# See all files (including ignored):
git ls-files --others --ignored --exclude-standard
```

## Common Git Commands

### Check Ignored Files
```bash
# See all ignored files
git status --ignored

# Check if specific file is ignored
git check-ignore -v scan_results.pdf
```

### Force Add Ignored File (if needed)
```bash
# Normally ignored, but force add:
git add -f important_file.pdf

# Not recommended for most ignored files!
```

### Clean Ignored Files
```bash
# Remove all untracked files (dry run):
git clean -xdn

# Actually remove (careful!):
git clean -xdf
```

### Update After Changing .gitignore
```bash
# If you added new patterns and want to remove already-tracked files:
git rm -r --cached .
git add .
git commit -m "Update .gitignore and remove tracked files"
```

## Testing Your .gitignore

### 1. Check What Would Be Committed
```bash
# See untracked files:
git status

# Should NOT show:
# - __pycache__/
# - *.pyc
# - venv/
# - scan_results_*.pdf
# - test_*.pdf
# etc.
```

### 2. Verify Specific Files
```bash
# Check if file is ignored:
git check-ignore -v test_report.pdf
# Output: .gitignore:123:test_*.pdf    test_report.pdf

git check-ignore -v check.py
# Output: (nothing - file is NOT ignored, will be tracked)
```

### 3. List All Ignored Files
```bash
# See everything that's being ignored:
git ls-files --others --ignored --exclude-standard
```

## Troubleshooting

### Problem: File is tracked but should be ignored

**Solution**:
```bash
# Remove from tracking (keeps local file):
git rm --cached filename.pdf

# Commit the change:
git commit -m "Stop tracking filename.pdf"
```

### Problem: .gitignore not working

**Cause**: File was already tracked before adding to .gitignore

**Solution**:
```bash
# Remove all cached files:
git rm -r --cached .

# Re-add everything (gitignore now applies):
git add .

# Commit:
git commit -m "Apply .gitignore rules"
```

### Problem: Want to track a normally-ignored file

**Solution**:
```bash
# Force add:
git add -f special_file.exe

# Or add exception to .gitignore:
!special_file.exe
```

## File Structure Example

```
SystemScanner/
├── .git/                    # Git repository (auto-created)
├── .gitignore              # This file ✅ COMMIT
├── check.py                # Source code ✅ COMMIT
├── pdf_reporter.py         # Source code ✅ COMMIT
├── system_info.py          # Source code ✅ COMMIT
├── requirements.txt        # Dependencies ✅ COMMIT
├── SystemScanner.spec      # Build config ✅ COMMIT
├── build.bat               # Build script ✅ COMMIT
├── README.md               # Documentation ✅ COMMIT
├── LICENSE                 # License ✅ COMMIT
│
├── __pycache__/            # ❌ IGNORED
├── venv/                   # ❌ IGNORED
├── scanner_env/            # ❌ IGNORED
├── build/                  # ❌ IGNORED
├── dist/                   # ❌ IGNORED
│   └── SystemScanner.exe   # ❌ IGNORED
├── test_report.pdf         # ❌ IGNORED
├── scan_results_*.pdf      # ❌ IGNORED
├── *.log                   # ❌ IGNORED
└── .vscode/                # ❌ IGNORED
```

## Summary

✅ **DO Commit**:
- Source code (`.py` files)
- Documentation (`.md` files)
- Configuration files (`requirements.txt`, `.spec`)
- Build scripts (`.bat` files)
- License and README

❌ **DON'T Commit**:
- Build artifacts (`dist/`, `build/`, `.exe`)
- Virtual environments (`venv/`, `scanner_env/`)
- User data (scan results, PDFs)
- IDE settings (`.vscode/`, `.idea/`)
- OS files (`Thumbs.db`, `.DS_Store`)
- Secrets (`.env`, `credentials.json`)
- Temporary files (`.tmp`, `.log`, `.bak`)
- Python cache (`__pycache__/`, `*.pyc`)

Following these rules keeps your repository clean, secure, and professional! 🚀
