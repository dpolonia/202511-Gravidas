#!/bin/bash
################################################################################
# NLP Dependencies Installation Script
# Installs optional ML libraries for enhanced NLP module performance
################################################################################

set -e  # Exit on error

echo "================================================================"
echo "     NLP Dependencies Installation for Enhanced Accuracy"
echo "================================================================"
echo ""
echo "This script will install optional ML dependencies for:"
echo "  - Medical Entity Recognition (scispaCy)"
echo "  - Multi-Emotion Detection (NRCLex)"
echo "  - Topic Modeling (BERTopic, Gensim)"
echo "  - BERT Sentiment (Transformers, PyTorch)"
echo "  - Semantic Similarity (Sentence-Transformers)"
echo "  - Advanced Analytics (SciPy, Ruptures)"
echo ""
echo "Installation may take 5-15 minutes depending on your system."
echo "================================================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Create requirements file
cat > /tmp/nlp_requirements.txt << 'EOF'
# Core NLP Libraries
nltk>=3.8
textstat>=0.7.3

# Text Processing
NRCLex>=3.0.0
text2emotion>=0.0.5

# Machine Learning & Transformers
torch>=2.0.0
transformers>=4.30.0
sentence-transformers>=2.2.0

# Topic Modeling
gensim>=4.3.0
bertopic>=0.15.0

# Scientific Computing
scipy>=1.10.0
scikit-learn>=1.3.0
numpy>=1.24.0

# Change Point Detection
ruptures>=1.1.9

# Medical NLP
spacy>=3.5.0
scispacy>=0.5.3

# Additional utilities
pandas>=2.0.0
EOF

echo "================================================================"
echo "STEP 1: Installing Core NLP Libraries"
echo "================================================================"
echo ""

pip install -q --upgrade pip
pip install -r /tmp/nlp_requirements.txt

echo ""
echo "✓ Core libraries installed"
echo ""

echo "================================================================"
echo "STEP 2: Downloading NLTK Data"
echo "================================================================"
echo ""

python3 << 'PYTHON_SCRIPT'
import nltk
import ssl

# Handle SSL certificate issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download required NLTK data
packages = ['punkt', 'stopwords', 'wordnet', 'vader_lexicon', 'averaged_perceptron_tagger']
for package in packages:
    try:
        nltk.download(package, quiet=True)
        print(f"✓ Downloaded: {package}")
    except Exception as e:
        print(f"✗ Error downloading {package}: {e}")
PYTHON_SCRIPT

echo ""
echo "✓ NLTK data downloaded"
echo ""

echo "================================================================"
echo "STEP 3: Installing spaCy Language Model"
echo "================================================================"
echo ""

python3 -m spacy download en_core_web_sm
echo "✓ spaCy base model installed"
echo ""

echo "================================================================"
echo "STEP 4: Installing Medical NLP Model (scispaCy)"
echo "================================================================"
echo ""

pip install https://s3-us-west-2.amazonaws.com/ai2-s3-scispacy/releases/v0.5.3/en_core_sci_md-0.5.3.tar.gz

echo ""
echo "✓ Medical NLP model installed"
echo ""

echo "================================================================"
echo "STEP 5: Verifying Installation"
echo "================================================================"
echo ""

python3 << 'PYTHON_SCRIPT'
import sys

def check_import(package_name, display_name=None):
    """Check if a package can be imported."""
    if display_name is None:
        display_name = package_name
    try:
        __import__(package_name)
        print(f"✓ {display_name}")
        return True
    except ImportError:
        print(f"✗ {display_name} - NOT INSTALLED")
        return False

print("Checking installations:")
print("-" * 50)

results = []
results.append(check_import('nltk', 'NLTK'))
results.append(check_import('textstat', 'TextStat'))
results.append(check_import('nrclex', 'NRCLex'))
results.append(check_import('torch', 'PyTorch'))
results.append(check_import('transformers', 'Transformers'))
results.append(check_import('sentence_transformers', 'Sentence-Transformers'))
results.append(check_import('gensim', 'Gensim'))
results.append(check_import('bertopic', 'BERTopic'))
results.append(check_import('scipy', 'SciPy'))
results.append(check_import('sklearn', 'Scikit-learn'))
results.append(check_import('ruptures', 'Ruptures'))
results.append(check_import('spacy', 'spaCy'))

# Check spaCy models
try:
    import spacy
    spacy.load("en_core_web_sm")
    print("✓ spaCy model: en_core_web_sm")
    results.append(True)
except:
    print("✗ spaCy model: en_core_web_sm - NOT LOADED")
    results.append(False)

# Check scispaCy
try:
    import scispacy
    import spacy
    spacy.load("en_core_sci_md")
    print("✓ Medical NLP model: en_core_sci_md")
    results.append(True)
except:
    print("✗ Medical NLP model: en_core_sci_md - NOT LOADED")
    results.append(False)

print("-" * 50)
success_rate = sum(results) / len(results) * 100
print(f"\nInstallation Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")

if success_rate == 100:
    print("\n🎉 ALL DEPENDENCIES INSTALLED SUCCESSFULLY!")
    sys.exit(0)
elif success_rate >= 80:
    print("\n⚠️  Most dependencies installed. Some optional features may not work.")
    sys.exit(0)
else:
    print("\n❌ Installation incomplete. Please check errors above.")
    sys.exit(1)
PYTHON_SCRIPT

installation_status=$?

echo ""
echo "================================================================"
echo "Installation Complete"
echo "================================================================"
echo ""

if [ $installation_status -eq 0 ]; then
    echo "✓ Enhanced NLP dependencies are ready!"
    echo ""
    echo "Next steps:"
    echo "  1. Test the installation:"
    echo "     python scripts/05_analyze_interviews_enhanced.py --sample 5"
    echo ""
    echo "  2. Run full analysis:"
    echo "     python scripts/05_analyze_interviews_enhanced.py --export-json"
    echo ""
else
    echo "⚠️  Some dependencies may not be fully installed."
    echo "   The NLP modules will still work with pattern-based fallbacks."
    echo ""
fi

# Cleanup
rm -f /tmp/nlp_requirements.txt

exit $installation_status
