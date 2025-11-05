#!/bin/bash
# Fix script to ensure latest model IDs are being used

echo "=================================="
echo "  Fixing Model IDs Issue"
echo "=================================="
echo ""

# Step 1: Check current directory
echo "Step 1: Checking directory..."
pwd
echo ""

# Step 2: Check git status
echo "Step 2: Checking git status..."
git status
echo ""

# Step 3: Pull latest changes
echo "Step 3: Pulling latest changes..."
git pull origin claude/synthetic-gravidas-pipeline-011CUpt3YLnLffQE1REgHQoh
echo ""

# Step 4: Clear Python cache
echo "Step 4: Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✓ Cache cleared"
echo ""

# Step 5: Verify model IDs in the file
echo "Step 5: Verifying model IDs..."
echo "Anthropic models in interactive_interviews.py:"
grep "'claude-" scripts/interactive_interviews.py | head -5
echo ""

# Step 6: Verify API key
echo "Step 6: Checking API key..."
if [ -f .env ]; then
    if grep -q "ANTHROPIC_API_KEY" .env && ! grep -q "ANTHROPIC_API_KEY=your-" .env; then
        echo "✓ ANTHROPIC_API_KEY found in .env"
    else
        echo "⚠ ANTHROPIC_API_KEY not configured in .env"
        echo "Please add your API key to .env file"
    fi
else
    echo "⚠ .env file not found"
    echo "Please create .env and add ANTHROPIC_API_KEY=your-key"
fi
echo ""

echo "=================================="
echo "  Fix Complete!"
echo "=================================="
echo ""
echo "Now try running again:"
echo "  python scripts/interactive_interviews.py"
echo ""
