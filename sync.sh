#!/bin/bash

################################################################################
# Git Synchronization Script for Gravidas Repository
# Usage: ./sync.sh
# Location: /home/dpolonia/202511-Gravidas
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️ ${NC} $1"
}

################################################################################
# Main Script
################################################################################

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║             Git Synchronization Script for Gravidas                   ║"
echo "║                        Repository: /home/dpolonia/202511-Gravidas      ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Navigate to repository
print_status "Step 1: Navigating to repository..."
cd /home/dpolonia/202511-Gravidas || {
    print_error "Failed to navigate to repository"
    exit 1
}
print_success "In directory: $(pwd)"
echo ""

# Step 2: Get current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ -z "$BRANCH" ]; then
    print_error "Not a git repository"
    exit 1
fi
print_status "Step 2: Current branch: $BRANCH"
echo ""

# Step 3: Check if working tree is clean
print_status "Step 3: Checking working tree..."
if ! git diff --quiet; then
    print_warning "Uncommitted changes detected"
    git status
    echo ""
    read -p "Continue with sync? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Sync cancelled"
        exit 1
    fi
fi
print_success "Working tree is clean"
echo ""

# Step 4: Fetch remote
print_status "Step 4: Fetching remote changes..."
if git fetch origin 2>/dev/null; then
    print_success "Fetch successful"
else
    print_error "Fetch failed"
    exit 1
fi
echo ""

# Step 5: Check status
print_status "Step 5: Checking synchronization status..."
STATUS=$(git status -porcelain)
BRANCH_STATUS=$(git status --porcelain --branch)

if git rev-parse --verify origin/$BRANCH >/dev/null 2>&1; then
    BEHIND=$(git rev-list --count origin/$BRANCH..HEAD 2>/dev/null || echo "0")
    AHEAD=$(git rev-list --count HEAD..origin/$BRANCH 2>/dev/null || echo "0")

    if [ "$BEHIND" -eq 0 ] && [ "$AHEAD" -eq 0 ]; then
        print_success "Branch is synchronized with remote"
    elif [ "$AHEAD" -gt 0 ] && [ "$BEHIND" -eq 0 ]; then
        print_warning "Local branch is ahead by $AHEAD commit(s)"
        echo "Will push changes..."
    elif [ "$BEHIND" -gt 0 ] && [ "$AHEAD" -eq 0 ]; then
        print_warning "Local branch is behind by $BEHIND commit(s)"
        echo "Will pull changes..."
    else
        print_error "Branches have diverged"
        echo "Local: $AHEAD commits ahead, $BEHIND commits behind"
    fi
else
    print_warning "Remote branch does not exist yet"
fi
echo ""

# Step 6: Pull if needed
print_status "Step 6: Pulling changes..."
if git pull origin $BRANCH 2>/dev/null; then
    print_success "Pull successful"
else
    print_warning "Nothing to pull or pull failed"
fi
echo ""

# Step 7: Push if needed
print_status "Step 7: Pushing changes..."
if git push -u origin $BRANCH 2>/dev/null; then
    print_success "Push successful"
else
    print_warning "Nothing to push or push failed"
fi
echo ""

# Step 8: Final status
print_status "Step 8: Verifying synchronization..."
echo ""
git status
echo ""

# Display recent commits
echo ""
print_status "Recent commits (5 most recent):"
echo ""
git log --oneline -5
echo ""

# Check if fully synchronized
FINAL_BEHIND=$(git rev-list --count origin/$BRANCH..HEAD 2>/dev/null || echo "0")
FINAL_AHEAD=$(git rev-list --count HEAD..origin/$BRANCH 2>/dev/null || echo "0")

echo "╔════════════════════════════════════════════════════════════════════════╗"
if [ "$FINAL_BEHIND" -eq 0 ] && [ "$FINAL_AHEAD" -eq 0 ]; then
    echo -e "║ ${GREEN}✅ SYNCHRONIZATION COMPLETE${NC}"
    echo "║ Your repository is fully synchronized with remote"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    exit 0
else
    echo -e "║ ${YELLOW}⚠️  SYNCHRONIZATION INCOMPLETE${NC}"
    echo "║ Please resolve the issues above and try again"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    exit 1
fi
