# Git Synchronization Instructions for Gravidas Repository

## Overview

This guide provides step-by-step instructions to synchronize your local repository with GitHub.

**Location:** `/home/dpolonia/202511-Gravidas`

---

## Method 1: Quick Synchronization (Recommended for Most Cases)

### Step 1: Navigate to Repository

```bash
cd /home/dpolonia/202511-Gravidas
```

**Expected Output:**
```
(you should now be in the gravidas project directory)
```

### Step 2: Fetch Latest Changes from Remote

```bash
git fetch origin
```

**Expected Output:**
```
From http://local_proxy@127.0.0.1:46273/git/dpolonia/202511-Gravidas
 * [new branch]      ...
```

This downloads any new commits from GitHub without modifying your working directory.

### Step 3: Check Current Status

```bash
git status
```

**Expected Output (if already synchronized):**
```
On branch claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
Your branch is up to date with 'origin/claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU'.
nothing to commit, working tree clean
```

**If behind remote:**
```
Your branch is behind 'origin/...' by X commits.
```

### Step 4: Pull Changes (if needed)

If `git status` shows you're behind, run:

```bash
git pull origin claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

**Expected Output:**
```
From http://local_proxy@127.0.0.1:46273/git/dpolonia/202511-Gravidas
 * branch            claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU -> FETCH_HEAD
Already up to date.
```

### Step 5: Push Local Changes (if any)

If you have local commits not yet pushed:

```bash
git push -u origin claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

**Expected Output:**
```
Everything up-to-date
```

or

```
Counting objects: 5, done.
Writing objects: 100% (5/5), ...
 e746c4a..abc1234 claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU -> claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

---

## Method 2: One-Line Synchronization

If you want to do everything at once, use this single command:

```bash
cd /home/dpolonia/202511-Gravidas && git fetch origin && git pull && git push && git status
```

**This will:**
1. Navigate to repository
2. Fetch all remote changes
3. Pull changes to your branch
4. Push any local changes
5. Show final status

---

## Method 3: Comprehensive Synchronization (Step by Step)

Use this if you want the most detailed control:

### Step 1: Navigate to Directory

```bash
cd /home/dpolonia/202511-Gravidas
```

### Step 2: View Current Branch

```bash
git branch
```

**Expected Output:**
```
* claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
  claude/document-codebase-011CUuT7xrPhZ4T78nkXCurf
```

The branch with `*` is your current branch.

### Step 3: Check Recent Commits (Local)

```bash
git log --oneline -5
```

**Expected Output:**
```
e746c4a 🎯 PHASE 5: Workflow Pipeline Orchestration & Testing Framework
a6b989f TOPICS 6 & 7: Enhance reporting outputs & make CLI more flexible
bf4cdc1 TOPIC 5: Expand clinical analytics
ae495f6 TOPIC 4: Enrich cost reporting
1266bac TOPIC 3: Refine quantitative metrics
```

### Step 4: Fetch All Remote Branches

```bash
git fetch origin
```

### Step 5: Check for Differences

```bash
git log --oneline -5 origin/claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

**Compare output with Step 3 to see if they're identical**

### Step 6: Pull Changes

```bash
git pull origin claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

### Step 7: Push Changes

```bash
git push -u origin claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

### Step 8: Verify Synchronization

```bash
git status
```

**Expected Output:**
```
On branch claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
Your branch is up to date with 'origin/claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU'.
nothing to commit, working tree clean
```

---

## Troubleshooting

### Issue 1: "Permission Denied" Error

**Problem:**
```
Permission denied (publickey).
fatal: Could not read from remote repository.
```

**Solution:**
This is a network/authentication issue. Try:

```bash
git config --get remote.origin.url
```

You should see:
```
http://local_proxy@127.0.0.1:46273/git/dpolonia/202511-Gravidas
```

If you see an `ssh://` URL instead, reconfigure to HTTP:

```bash
git remote set-url origin http://local_proxy@127.0.0.1:46273/git/dpolonia/202511-Gravidas
```

### Issue 2: "Your branch is ahead of origin"

**Problem:**
```
Your branch is ahead of 'origin/...' by 2 commits.
```

**Solution:**
You have local commits not pushed. Push them:

```bash
git push -u origin claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

### Issue 3: "Your branch has diverged"

**Problem:**
```
Your branch and 'origin/...' have diverged
```

**Solution:**
This means remote and local have different commits. Check differences:

```bash
# View local commits
git log --oneline -5

# View remote commits
git log --oneline -5 origin/claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU

# Pull remote changes (may create merge commit)
git pull origin claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU

# Push merged result
git push -u origin claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

### Issue 4: "Cannot pull with uncommitted changes"

**Problem:**
```
error: Your local changes to 'file.txt' would be overwritten by merge
```

**Solution:**
Commit or stash your changes first:

```bash
# Option 1: Commit your changes
git add .
git commit -m "Your message here"

# Option 2: Stash your changes (save for later)
git stash

# Then pull
git pull origin claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

---

## Complete Synchronization Script

Copy and paste this entire script to do a complete synchronization:

```bash
#!/bin/bash
# Complete Git Synchronization Script

echo "🔄 Starting Git Synchronization..."
echo ""

# Step 1: Navigate to directory
cd /home/dpolonia/202511-Gravidas || exit 1
echo "✅ Navigated to: $(pwd)"
echo ""

# Step 2: Show current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "📍 Current Branch: $CURRENT_BRANCH"
echo ""

# Step 3: Fetch remote changes
echo "📥 Fetching remote changes..."
git fetch origin
echo "✅ Fetch complete"
echo ""

# Step 4: Check status
echo "📊 Checking status..."
git status
echo ""

# Step 5: Pull changes
echo "📥 Pulling changes..."
git pull origin "$CURRENT_BRANCH"
echo "✅ Pull complete"
echo ""

# Step 6: Push changes
echo "📤 Pushing changes..."
git push -u origin "$CURRENT_BRANCH"
echo "✅ Push complete"
echo ""

# Step 7: Final status
echo "✅ Synchronization Complete!"
echo ""
echo "📊 Final Status:"
git status
echo ""
echo "📝 Recent Commits:"
git log --oneline -5
echo ""
echo "✨ All synchronized! You're ready to go."
```

Save this as `sync.sh` and run it:

```bash
chmod +x sync.sh
./sync.sh
```

---

## Quick Reference Commands

### Daily Synchronization

```bash
cd /home/dpolonia/202511-Gravidas
git fetch origin && git pull && git push && git status
```

### Check if Synchronized

```bash
cd /home/dpolonia/202511-Gravidas
git status
```

### View Recent Changes

```bash
cd /home/dpolonia/202511-Gravidas
git log --oneline -10
```

### Compare Local vs Remote

```bash
cd /home/dpolonia/202511-Gravidas
git log --oneline -1
git log --oneline -1 origin/claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

---

## Best Practices

### 1. Always Fetch Before Working

```bash
git fetch origin
git status
```

### 2. Commit Before Syncing

If you have uncommitted changes:

```bash
git add .
git commit -m "Your descriptive message"
git push origin claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

### 3. Pull Before Starting New Work

```bash
git pull origin claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

### 4. Review Changes Before Pushing

```bash
git log --oneline -3 origin/claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

### 5. Keep Working Tree Clean

```bash
git status
# Should show: "nothing to commit, working tree clean"
```

---

## Command Summary Table

| Command | Purpose | Usage |
|---------|---------|-------|
| `git fetch origin` | Download remote changes | Before any work |
| `git status` | Check synchronization status | Frequently |
| `git pull origin <branch>` | Download and merge remote changes | When behind |
| `git push -u origin <branch>` | Upload local changes | After committing |
| `git log --oneline -5` | View recent commits | Check history |
| `git diff origin/<branch>` | Compare with remote | Review changes |

---

## Expected Workflow

### When You Start

```bash
cd /home/dpolonia/202511-Gravidas
git fetch origin
git status  # Should show: up to date
```

### When You Make Changes

```bash
# Make your changes...
git add .
git commit -m "Description of changes"
git push -u origin claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
```

### When You're Done

```bash
git status  # Should show: working tree clean
git log --oneline -1  # View your commit
```

---

## Emergency Sync (Nuclear Option)

If everything is messed up, use this to reset to remote state:

```bash
cd /home/dpolonia/202511-Gravidas
git fetch origin
git reset --hard origin/claude/explain-codebase-011CUuTW9o56zB9khSkLKjPU
git clean -fd
git status
```

**⚠️ WARNING:** This will discard all local uncommitted changes!

---

## Support

For more help:

```bash
# Git help
git help pull
git help push
git help fetch

# Check remote configuration
git remote -v

# Check current branch
git branch -vv

# Check git config
git config --list
```

---

**Last Updated:** 2025-11-12
**Status:** Ready to Use
**Repository:** `/home/dpolonia/202511-Gravidas`
