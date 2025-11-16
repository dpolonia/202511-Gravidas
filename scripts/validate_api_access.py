#!/usr/bin/env python3
"""
API Access Validation Script

Tests connectivity to all configured AI providers before Phase 4 execution.
Verifies API keys are valid and provides specific error messages and fixes.

Usage:
    python scripts/validate_api_access.py
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def test_anthropic_access(api_key: str) -> Tuple[bool, str, Dict]:
    """Test Anthropic API access."""
    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        # Minimal test request (very cheap)
        response = client.messages.create(
            model="claude-haiku-4-5",  # Cheapest model
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )

        usage = {
            'input_tokens': response.usage.input_tokens,
            'output_tokens': response.usage.output_tokens
        }

        return True, "✅ Connected successfully", usage

    except Exception as e:
        error_msg = str(e)

        if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
            return False, f"❌ Authentication failed: Invalid API key", {}
        elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
            return False, f"❌ Rate limit or quota exceeded", {}
        elif "not found" in error_msg.lower():
            return False, f"❌ Model not found or access denied", {}
        else:
            return False, f"❌ Connection failed: {error_msg[:100]}", {}

def test_openai_access(api_key: str) -> Tuple[bool, str, Dict]:
    """Test OpenAI API access."""
    try:
        import openai

        client = openai.OpenAI(api_key=api_key)

        # Minimal test request
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheapest model
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )

        usage = {
            'input_tokens': response.usage.prompt_tokens,
            'output_tokens': response.usage.completion_tokens
        }

        return True, "✅ Connected successfully", usage

    except Exception as e:
        error_msg = str(e)

        if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
            return False, f"❌ Authentication failed: Invalid API key", {}
        elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
            return False, f"❌ Rate limit or quota exceeded", {}
        elif "billing" in error_msg.lower():
            return False, f"❌ Billing issue: Please add payment method", {}
        else:
            return False, f"❌ Connection failed: {error_msg[:100]}", {}

def test_google_access(api_key: str) -> Tuple[bool, str, Dict]:
    """Test Google Gemini API access."""
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        # Minimal test request
        model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Free tier model
        response = model.generate_content(
            "Hi",
            generation_config={'max_output_tokens': 10}
        )

        # Google doesn't always return token counts in free tier
        usage = {
            'input_tokens': 1,  # Approximate
            'output_tokens': len(response.text.split())
        }

        return True, "✅ Connected successfully", usage

    except Exception as e:
        error_msg = str(e)

        if "api_key" in error_msg.lower() or "invalid" in error_msg.lower():
            return False, f"❌ Authentication failed: Invalid API key", {}
        elif "quota" in error_msg.lower():
            return False, f"❌ Quota exceeded", {}
        elif "permission" in error_msg.lower():
            return False, f"❌ Permission denied: Enable Gemini API in Google Cloud Console", {}
        else:
            return False, f"❌ Connection failed: {error_msg[:100]}", {}

def test_xai_access(api_key: str) -> Tuple[bool, str, Dict]:
    """Test xAI Grok API access."""
    try:
        import openai

        # xAI uses OpenAI-compatible API
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )

        # Minimal test request - try different model names
        model_names = ["grok-2-latest", "grok-beta", "grok-2"]
        last_error = None

        for model_name in model_names:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                # If successful, break and continue with this model
                break
            except Exception as e:
                last_error = e
                continue
        else:
            # None of the models worked
            raise last_error if last_error else Exception("No valid model found")

        usage = {
            'input_tokens': response.usage.prompt_tokens,
            'output_tokens': response.usage.completion_tokens
        }

        return True, "✅ Connected successfully", usage

    except Exception as e:
        error_msg = str(e)

        if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
            return False, f"❌ Authentication failed: Invalid API key", {}
        elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
            return False, f"❌ Rate limit or quota exceeded", {}
        else:
            return False, f"❌ Connection failed: {error_msg[:100]}", {}

def get_fix_suggestion(provider: str, error_msg: str) -> str:
    """Provide specific fix suggestions based on error."""

    fixes = {
        'anthropic': {
            'default': f"""
{Colors.YELLOW}Fix Suggestions:{Colors.RESET}
1. Get API key from: https://console.anthropic.com
2. Set in .env file: ANTHROPIC_API_KEY=sk-ant-...
3. Ensure you have credits in your account
            """,
            'Invalid API key': f"""
{Colors.YELLOW}Fix Suggestions:{Colors.RESET}
1. Verify your API key at: https://console.anthropic.com
2. Update .env file with correct key: ANTHROPIC_API_KEY=sk-ant-...
3. Make sure the key starts with 'sk-ant-'
            """,
            'quota exceeded': f"""
{Colors.YELLOW}Fix Suggestions:{Colors.RESET}
1. Check your usage at: https://console.anthropic.com
2. Add credits to your account
3. Wait for rate limit to reset (usually 1 minute)
            """
        },
        'openai': {
            'default': f"""
{Colors.YELLOW}Fix Suggestions:{Colors.RESET}
1. Get API key from: https://platform.openai.com/api-keys
2. Set in .env file: OPENAI_API_KEY=sk-...
3. Ensure billing is set up
            """,
            'Invalid API key': f"""
{Colors.YELLOW}Fix Suggestions:{Colors.RESET}
1. Verify your API key at: https://platform.openai.com/api-keys
2. Update .env file with correct key: OPENAI_API_KEY=sk-...
3. Make sure the key starts with 'sk-'
            """,
            'Billing issue': f"""
{Colors.YELLOW}Fix Suggestions:{Colors.RESET}
1. Add payment method at: https://platform.openai.com/account/billing
2. Ensure you have sufficient credits
3. Verify your payment method is valid
            """
        },
        'google': {
            'default': f"""
{Colors.YELLOW}Fix Suggestions:{Colors.RESET}
1. Get API key from: https://makersuite.google.com/app/apikey
2. Set in .env file: GOOGLE_API_KEY=...
3. Enable Gemini API in Google Cloud Console
            """,
            'Invalid API key': f"""
{Colors.YELLOW}Fix Suggestions:{Colors.RESET}
1. Verify your API key at: https://makersuite.google.com/app/apikey
2. Update .env file with correct key: GOOGLE_API_KEY=...
3. Ensure the API key has Gemini API enabled
            """,
            'Permission denied': f"""
{Colors.YELLOW}Fix Suggestions:{Colors.RESET}
1. Enable Generative Language API at: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
2. Ensure your API key has access to Gemini models
3. Check quota limits in Google Cloud Console
            """
        },
        'xai': {
            'default': f"""
{Colors.YELLOW}Fix Suggestions:{Colors.RESET}
1. Get API key from: https://console.x.ai
2. Set in .env file: XAI_API_KEY=...
3. Ensure you have access to Grok API (may require waitlist approval)
            """,
            'Invalid API key': f"""
{Colors.YELLOW}Fix Suggestions:{Colors.RESET}
1. Verify your API key at: https://console.x.ai
2. Update .env file with correct key: XAI_API_KEY=...
3. Ensure you're approved for API access
            """
        }
    }

    provider_fixes = fixes.get(provider, {})

    # Try to match specific error
    for key, fix in provider_fixes.items():
        if key in error_msg:
            return fix

    return provider_fixes.get('default', 'No specific fix available')

def main():
    """Main validation function."""

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  Phase 4 Pre-Flight Check: API Access Validation{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

    print(f"{Colors.WHITE}Testing connectivity to all configured AI providers...{Colors.RESET}\n")

    # Define providers to test
    providers = [
        {
            'name': 'Anthropic (Claude)',
            'key': 'anthropic',
            'env_var': 'ANTHROPIC_API_KEY',
            'test_func': test_anthropic_access,
            'cheapest_model': 'claude-haiku-4-5',
            'cost_per_interview': '$0.080'
        },
        {
            'name': 'Google (Gemini)',
            'key': 'google',
            'env_var': 'GOOGLE_API_KEY',
            'test_func': test_google_access,
            'cheapest_model': 'gemini-2.5-flash',
            'cost_per_interview': '$0.059'
        },
        {
            'name': 'xAI (Grok)',
            'key': 'xai',
            'env_var': 'XAI_API_KEY',
            'test_func': test_xai_access,
            'cheapest_model': 'grok-4-fast',
            'cost_per_interview': '$0.032'
        },
        {
            'name': 'OpenAI (GPT)',
            'key': 'openai',
            'env_var': 'OPENAI_API_KEY',
            'test_func': test_openai_access,
            'cheapest_model': 'gpt-4o-mini',
            'cost_per_interview': '$0.095'
        }
    ]

    results = []
    all_passed = True

    for provider in providers:
        print(f"{Colors.BOLD}Testing {provider['name']}...{Colors.RESET}")

        # Check if API key exists
        api_key = os.getenv(provider['env_var'])

        if not api_key or api_key.startswith('your-'):
            print(f"  {Colors.RED}❌ API key not configured{Colors.RESET}")
            print(f"  {Colors.YELLOW}Set {provider['env_var']} in .env file{Colors.RESET}")
            print(get_fix_suggestion(provider['key'], 'default'))

            results.append({
                'provider': provider['name'],
                'status': 'NOT_CONFIGURED',
                'error': 'API key not set',
                'cheapest_model': provider['cheapest_model'],
                'cost_per_interview': provider['cost_per_interview']
            })
            all_passed = False
            print()
            continue

        # Test access
        success, message, usage = provider['test_func'](api_key)

        if success:
            print(f"  {Colors.GREEN}{message}{Colors.RESET}")
            print(f"  {Colors.CYAN}Test tokens: {usage.get('input_tokens', 0)} input, {usage.get('output_tokens', 0)} output{Colors.RESET}")
            print(f"  {Colors.MAGENTA}Cheapest model: {provider['cheapest_model']} ({provider['cost_per_interview']}/interview){Colors.RESET}")

            results.append({
                'provider': provider['name'],
                'status': 'OK',
                'cheapest_model': provider['cheapest_model'],
                'cost_per_interview': provider['cost_per_interview'],
                'test_usage': usage
            })
        else:
            print(f"  {Colors.RED}{message}{Colors.RESET}")
            print(get_fix_suggestion(provider['key'], message))

            results.append({
                'provider': provider['name'],
                'status': 'FAILED',
                'error': message,
                'cheapest_model': provider['cheapest_model'],
                'cost_per_interview': provider['cost_per_interview']
            })
            all_passed = False

        print()

    # Summary
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  Validation Summary{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

    working_providers = [r for r in results if r['status'] == 'OK']
    failed_providers = [r for r in results if r['status'] != 'OK']

    print(f"{Colors.GREEN}✅ Working Providers: {len(working_providers)}/4{Colors.RESET}")
    for provider in working_providers:
        print(f"   • {provider['provider']} - {provider['cheapest_model']} ({provider['cost_per_interview']}/interview)")

    if failed_providers:
        print(f"\n{Colors.RED}❌ Failed Providers: {len(failed_providers)}/4{Colors.RESET}")
        for provider in failed_providers:
            print(f"   • {provider['provider']} - {provider.get('error', 'Not configured')}")

    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_providers': len(providers),
        'working_providers': len(working_providers),
        'failed_providers': len(failed_providers),
        'results': results,
        'all_passed': all_passed
    }

    os.makedirs('outputs', exist_ok=True)
    report_path = 'outputs/api_validation_report.json'

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n{Colors.CYAN}📄 Detailed report saved to: {report_path}{Colors.RESET}")

    # Final verdict
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    if all_passed:
        print(f"{Colors.BOLD}{Colors.GREEN}✅ ALL PROVIDERS READY - Phase 4 can proceed{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.BOLD}{Colors.RED}⚠️  SOME PROVIDERS FAILED - Fix issues before Phase 4{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

        # Suggest minimum viable configuration
        if len(working_providers) >= 1:
            print(f"{Colors.YELLOW}Note: Phase 4 can proceed with at least 1 working provider,{Colors.RESET}")
            print(f"{Colors.YELLOW}but multi-provider testing requires at least 2 providers.{Colors.RESET}\n")

        return 1

if __name__ == "__main__":
    sys.exit(main())
