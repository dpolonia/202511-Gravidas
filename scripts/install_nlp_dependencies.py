#!/usr/bin/env python3
"""
NLP Dependencies Installation Script (Python Version)
======================================================

Installs optional ML libraries for enhanced NLP module performance.

Usage:
    python scripts/install_nlp_dependencies.py
    python scripts/install_nlp_dependencies.py --minimal  # Core only
    python scripts/install_nlp_dependencies.py --full     # Everything including medical models
"""

import sys
import subprocess
import argparse
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")


def print_section(text):
    """Print a section header."""
    print(f"\n{BLUE}{'-'*70}{RESET}")
    print(f"{BOLD}{text}{RESET}")
    print(f"{BLUE}{'-'*70}{RESET}\n")


def run_command(cmd, description=None, check=True):
    """Run a shell command and return success status."""
    if description:
        print(f"⚙️  {description}...", end=' ', flush=True)

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        if description:
            print(f"{GREEN}✓{RESET}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        if description:
            print(f"{RED}✗{RESET}")
        return False, e.stderr


def check_import(package_name, display_name=None):
    """Check if a package can be imported."""
    if display_name is None:
        display_name = package_name

    try:
        __import__(package_name)
        print(f"{GREEN}✓{RESET} {display_name}")
        return True
    except ImportError:
        print(f"{RED}✗{RESET} {display_name} - NOT INSTALLED")
        return False


def install_minimal_dependencies():
    """Install minimal core dependencies."""
    print_section("Installing Core Dependencies")

    packages = [
        'nltk>=3.8',
        'textstat>=0.7.3',
        'scipy>=1.10.0',
        'scikit-learn>=1.3.0',
        'numpy>=1.24.0',
        'pandas>=2.0.0',
    ]

    for package in packages:
        run_command(
            f"pip install -q '{package}'",
            f"Installing {package.split('>=')[0]}"
        )


def install_text_processing():
    """Install text processing libraries."""
    print_section("Installing Text Processing Libraries")

    packages = [
        ('NRCLex>=3.0.0', 'NRCLex'),
        ('text2emotion>=0.0.5', 'text2emotion'),
    ]

    for package, name in packages:
        run_command(
            f"pip install -q '{package}'",
            f"Installing {name}"
        )


def install_ml_transformers():
    """Install machine learning and transformer libraries."""
    print_section("Installing ML & Transformer Libraries")

    print("⚙️  Installing PyTorch (this may take a few minutes)...")
    success, _ = run_command(
        "pip install -q 'torch>=2.0.0'",
        check=False
    )
    if success:
        print(f"   {GREEN}✓{RESET} PyTorch installed")

    packages = [
        ('transformers>=4.30.0', 'Transformers'),
        ('sentence-transformers>=2.2.0', 'Sentence-Transformers'),
    ]

    for package, name in packages:
        run_command(
            f"pip install -q '{package}'",
            f"Installing {name}"
        )


def install_topic_modeling():
    """Install topic modeling libraries."""
    print_section("Installing Topic Modeling Libraries")

    packages = [
        ('gensim>=4.3.0', 'Gensim'),
        ('bertopic>=0.15.0', 'BERTopic'),
    ]

    for package, name in packages:
        run_command(
            f"pip install -q '{package}'",
            f"Installing {name}"
        )


def install_analytics():
    """Install advanced analytics libraries."""
    print_section("Installing Advanced Analytics")

    run_command(
        "pip install -q 'ruptures>=1.1.9'",
        "Installing Ruptures (change point detection)"
    )


def install_spacy_models():
    """Install spaCy and language models."""
    print_section("Installing spaCy & Language Models")

    run_command(
        "pip install -q 'spacy>=3.5.0'",
        "Installing spaCy"
    )

    run_command(
        "python -m spacy download en_core_web_sm",
        "Downloading spaCy base model"
    )


def install_medical_nlp():
    """Install medical NLP libraries."""
    print_section("Installing Medical NLP (scispaCy)")

    run_command(
        "pip install -q 'scispacy>=0.5.3'",
        "Installing scispaCy base"
    )

    print("⚙️  Downloading medical language model (this may take a few minutes)...")
    success, _ = run_command(
        "pip install -q https://s3-us-west-2.amazonaws.com/ai2-s3-scispacy/releases/v0.5.3/en_core_sci_md-0.5.3.tar.gz",
        check=False
    )
    if success:
        print(f"   {GREEN}✓{RESET} Medical model installed")
    else:
        print(f"   {YELLOW}⚠{RESET}  Medical model installation failed (optional)")


def download_nltk_data():
    """Download required NLTK data packages."""
    print_section("Downloading NLTK Data")

    packages = ['punkt', 'stopwords', 'wordnet', 'vader_lexicon', 'averaged_perceptron_tagger']

    import nltk
    for package in packages:
        try:
            nltk.download(package, quiet=True)
            print(f"{GREEN}✓{RESET} Downloaded: {package}")
        except Exception as e:
            print(f"{YELLOW}⚠{RESET}  Warning: {package} download failed")


def verify_installation():
    """Verify all installed packages."""
    print_section("Verifying Installation")

    checks = [
        ('nltk', 'NLTK'),
        ('textstat', 'TextStat'),
        ('nrclex', 'NRCLex'),
        ('torch', 'PyTorch'),
        ('transformers', 'Transformers'),
        ('sentence_transformers', 'Sentence-Transformers'),
        ('gensim', 'Gensim'),
        ('bertopic', 'BERTopic'),
        ('scipy', 'SciPy'),
        ('sklearn', 'Scikit-learn'),
        ('ruptures', 'Ruptures'),
        ('spacy', 'spaCy'),
    ]

    results = []
    for package, name in checks:
        results.append(check_import(package, name))

    # Check spaCy models
    try:
        import spacy
        spacy.load("en_core_web_sm")
        print(f"{GREEN}✓{RESET} spaCy model: en_core_web_sm")
        results.append(True)
    except:
        print(f"{RED}✗{RESET} spaCy model: en_core_web_sm")
        results.append(False)

    # Check scispaCy
    try:
        import spacy
        spacy.load("en_core_sci_md")
        print(f"{GREEN}✓{RESET} Medical model: en_core_sci_md")
        results.append(True)
    except:
        print(f"{YELLOW}⚠{RESET}  Medical model: en_core_sci_md (optional)")
        results.append(False)

    return results


def main():
    """Main installation entry point."""
    parser = argparse.ArgumentParser(
        description='Install NLP dependencies for enhanced accuracy'
    )
    parser.add_argument(
        '--minimal',
        action='store_true',
        help='Install only core dependencies'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Install everything including medical models'
    )

    args = parser.parse_args()

    print_header("NLP Dependencies Installation")

    print("This will install optional ML libraries for enhanced NLP accuracy:")
    print("  • Medical Entity Recognition (scispaCy)")
    print("  • Multi-Emotion Detection (NRCLex)")
    print("  • Topic Modeling (BERTopic, Gensim)")
    print("  • BERT Sentiment (Transformers, PyTorch)")
    print("  • Semantic Similarity (Sentence-Transformers)")
    print("  • Advanced Analytics (SciPy, Ruptures)")
    print("\nInstallation may take 5-15 minutes depending on your system.\n")

    # Upgrade pip
    run_command("pip install -q --upgrade pip", "Upgrading pip")

    # Always install minimal dependencies
    install_minimal_dependencies()
    download_nltk_data()

    if not args.minimal:
        install_text_processing()
        install_ml_transformers()
        install_topic_modeling()
        install_analytics()
        install_spacy_models()

        if args.full:
            install_medical_nlp()

    # Verify installation
    results = verify_installation()

    # Print summary
    print_header("Installation Summary")

    success_count = sum(results)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100

    print(f"Success Rate: {success_rate:.1f}% ({success_count}/{total_count})")

    if success_rate == 100:
        print(f"\n{GREEN}🎉 ALL DEPENDENCIES INSTALLED SUCCESSFULLY!{RESET}\n")
        print("Next steps:")
        print("  1. Test the installation:")
        print(f"     {BLUE}python scripts/05_analyze_interviews_enhanced.py --sample 5{RESET}")
        print("")
        print("  2. Run full analysis:")
        print(f"     {BLUE}python scripts/05_analyze_interviews_enhanced.py --export-json{RESET}")
        return 0

    elif success_rate >= 80:
        print(f"\n{YELLOW}⚠️  Most dependencies installed. Some optional features may not work.{RESET}\n")
        print("The NLP modules will use pattern-based fallbacks for missing dependencies.")
        return 0

    else:
        print(f"\n{RED}❌ Installation incomplete. Please check errors above.{RESET}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
