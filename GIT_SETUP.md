# Git Setup Guide for SystemScanner

## Quick Start

### 1. Initialize Git Repository
```bash
cd C:\SystemScanner
git init
```

### 2. Add .gitignore
```bash
# .gitignore is already created
git add .gitignore
git commit -m "Add .gitignore"
```

### 3. Add Source Files
```bash
# Add all source code and documentation
git add *.py *.md *.txt *.bat *.spec *.manifest
git commit -m "Initial commit: SystemScanner security audit tool"
```

### 4. Create GitHub Repository (Optional)
```bash
# On GitHub, create new repository: SystemScanner

# Link local to remote:
git remote add origin https://github.com/yourusername/SystemScanner.git

# Push to GitHub:
git branch -M main
git push -u origin main
```

---

## What Gets Committed

### ✅ Source Code
```
check.py
pdf_reporter.py
system_info.py
```

### ✅ Configuration
```
requirements.txt
SystemScanner.spec
version_info.txt
app.manifest
```

### ✅ Build Scripts
```
build.bat
```

### ✅ Documentation
```
README.md
LICENSE
*.md files
```

### ✅ Git Files
```
.gitignore
```

---

## What Gets Ignored

### ❌ Build Artifacts
```
build/
dist/
*.exe
__pycache__/
*.pyc
```

### ❌ Virtual Environments
```
venv/
scanner_env/
ENV/
```

### ❌ IDE Settings
```
.vscode/
.idea/
*.sublime-project
```

### ❌ User Data
```
scan_results_*.pdf
test_*.pdf
*.log
```

### ❌ OS Files
```
Thumbs.db
.DS_Store
Desktop.ini
```

### ❌ Sensitive Data
```
.env
credentials.json
*.key
*.pem
```

---

## Recommended Git Workflow

### Initial Setup
```bash
# 1. Initialize
git init

# 2. Add .gitignore first
git add .gitignore
git commit -m "Add .gitignore"

# 3. Add source files
git add *.py requirements.txt
git commit -m "Add source code"

# 4. Add configuration
git add *.spec *.txt *.manifest *.bat
git commit -m "Add build configuration"

# 5. Add documentation
git add *.md
git commit -m "Add documentation"
```

### Daily Workflow
```bash
# Check status
git status

# Add changes
git add check.py
git commit -m "Fix: Port blocking detection for UDP ports"

# Push to remote
git push
```

### Before Building
```bash
# Make sure build artifacts aren't tracked
git status

# Should NOT show:
# - dist/
# - build/
# - *.exe
```

---

## Verification

### Test .gitignore
```bash
# Run verification script
python verify_gitignore.py

# Or manually check
git status --ignored
```

### Check What Will Be Committed
```bash
# See tracked files
git ls-files

# See ignored files
git ls-files --others --ignored --exclude-standard

# Check specific file
git check-ignore -v test_report.pdf
```

---

## Common Scenarios

### Scenario 1: Accidentally Added Build Files
```bash
# Remove from tracking (keeps local file)
git rm --cached dist/SystemScanner.exe
git commit -m "Remove build artifacts from tracking"
```

### Scenario 2: Update .gitignore
```bash
# After modifying .gitignore
git add .gitignore
git commit -m "Update .gitignore to exclude test files"

# Remove newly-ignored files from tracking
git rm -r --cached .
git add .
git commit -m "Apply updated .gitignore"
```

### Scenario 3: Clean Working Directory
```bash
# Remove all untracked and ignored files (CAREFUL!)
git clean -xdf

# Safe preview first:
git clean -xdn
```

---

## GitHub Repository Setup

### 1. Create Repository on GitHub
- Go to https://github.com/new
- Name: `SystemScanner`
- Description: `Windows Security Audit Tool - Scan for VPN/Chat/Remote apps and security settings`
- Public or Private: Your choice
- **DO NOT** initialize with README (you already have one)

### 2. Link Local to Remote
```bash
git remote add origin https://github.com/yourusername/SystemScanner.git
git branch -M main
git push -u origin main
```

### 3. Add README Badges (Optional)
Add to top of README.md:
```markdown
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

---

## .gitignore Best Practices

### 1. ✅ Commit .gitignore First
```bash
git add .gitignore
git commit -m "Add .gitignore"
# Then add other files
```

### 2. ✅ Never Commit Secrets
```bash
# BAD:
git add .env
git add credentials.json

# GOOD: Already in .gitignore
```

### 3. ✅ Don't Commit Build Artifacts
```bash
# BAD:
git add dist/SystemScanner.exe

# GOOD: Use GitHub Releases instead
```

### 4. ✅ Keep User Data Private
```bash
# BAD:
git add scan_results_20251020.pdf

# GOOD: Already ignored by pattern
```

---

## File Structure in Git

```
SystemScanner/  (Git Root)
│
├── .git/                       # Git metadata (auto-created)
├── .gitignore                  # ✅ COMMIT
│
├── check.py                    # ✅ COMMIT (source)
├── pdf_reporter.py             # ✅ COMMIT (source)
├── system_info.py              # ✅ COMMIT (source)
│
├── requirements.txt            # ✅ COMMIT (config)
├── SystemScanner.spec          # ✅ COMMIT (config)
├── version_info.txt            # ✅ COMMIT (config)
├── app.manifest                # ✅ COMMIT (config)
├── build.bat                   # ✅ COMMIT (script)
│
├── README.md                   # ✅ COMMIT (docs)
├── LICENSE                     # ✅ COMMIT (docs)
├── *.md                        # ✅ COMMIT (docs)
│
├── __pycache__/                # ❌ IGNORED
├── venv/                       # ❌ IGNORED
├── scanner_env/                # ❌ IGNORED
├── build/                      # ❌ IGNORED
├── dist/                       # ❌ IGNORED
├── *.exe                       # ❌ IGNORED
├── test_*.pdf                  # ❌ IGNORED
├── scan_results_*.pdf          # ❌ IGNORED
├── *.log                       # ❌ IGNORED
└── .vscode/                    # ❌ IGNORED
```

---

## Troubleshooting

### Problem: File shows in `git status` but should be ignored

**Check**:
```bash
git check-ignore -v filename.pdf
```

**If not ignored**:
1. Add pattern to .gitignore
2. Remove from tracking: `git rm --cached filename.pdf`
3. Commit: `git commit -m "Ignore filename.pdf"`

### Problem: Can't push to GitHub

**Solutions**:
```bash
# Check remote:
git remote -v

# Set correct remote:
git remote set-url origin https://github.com/user/repo.git

# Force push (CAREFUL):
git push -f origin main
```

### Problem: Merge conflicts in .gitignore

**Solution**:
```bash
# Accept both versions:
# Edit .gitignore manually
# Remove conflict markers (<<<<, ====, >>>>)
git add .gitignore
git commit -m "Resolve .gitignore conflict"
```

---

## Summary

✅ **Created**: `.gitignore` with comprehensive rules
✅ **Ignores**: Build artifacts, user data, IDE files, secrets
✅ **Tracks**: Source code, documentation, configuration
✅ **Verified**: Use `verify_gitignore.py` to test

**Next Steps**:
1. Initialize Git: `git init`
2. Commit .gitignore: `git add .gitignore && git commit -m "Add .gitignore"`
3. Commit source: `git add *.py && git commit -m "Add source code"`
4. Push to GitHub (optional)

Your repository is now ready for version control! 🚀
