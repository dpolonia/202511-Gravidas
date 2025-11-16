#!/usr/bin/env python3
"""
Phase 4 Budget Approval Script

Calculates and displays global and per-model budgets for Phase 4 testing.
Requests user approval before proceeding with interview execution.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.cost_monitor import Colors
from utils.budget_tracker import BudgetTracker


def display_phase4_budget():
    """Display comprehensive Phase 4 budget breakdown."""

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  PHASE 4: GLOBAL BUDGET OVERVIEW{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═'*70}{Colors.RESET}\n")

    # Global budget
    global_budget_eur = 100.0
    print(f"{Colors.WHITE}Allocated Budget:{Colors.RESET}  €{global_budget_eur:.2f}")
    print(f"{Colors.WHITE}Currency Rate:{Colors.RESET}     1 USD = 0.92 EUR\n")

    # Provider information from API validation
    print(f"{Colors.BOLD}{Colors.MAGENTA}Available Providers (Validated):{Colors.RESET}\n")

    providers = [
        {
            'name': 'Anthropic Claude',
            'model': 'claude-haiku-4-5',
            'cost_per_interview_usd': 0.080,
            'cost_per_interview_eur': 0.074,
            'status': '✅ CHEAPEST - Primary provider',
            'recommended': True
        },
        {
            'name': 'OpenAI GPT',
            'model': 'gpt-4o-mini',
            'cost_per_interview_usd': 0.095,
            'cost_per_interview_eur': 0.087,
            'status': '✅ Available - Variance testing',
            'recommended': True
        },
        {
            'name': 'Google Gemini',
            'model': 'gemini-2.5-flash',
            'cost_per_interview_usd': 0.059,
            'cost_per_interview_eur': 0.054,
            'status': '❌ Quota exceeded',
            'recommended': False
        },
        {
            'name': 'xAI Grok',
            'model': 'grok-4-fast',
            'cost_per_interview_usd': 0.032,
            'cost_per_interview_eur': 0.029,
            'status': '❌ Model not found',
            'recommended': False
        }
    ]

    for provider in providers:
        if provider['recommended']:
            color = Colors.GREEN
        else:
            color = Colors.RED

        print(f"{color}{provider['name']} ({provider['model']}){Colors.RESET}")
        print(f"  Cost: €{provider['cost_per_interview_eur']:.4f}/interview")
        print(f"  Status: {provider['status']}\n")

    # Pilot testing budget (20 interviews)
    print(f"{Colors.BOLD}{Colors.YELLOW}{'─'*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}PILOT TESTING (20 interviews){Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{'─'*70}{Colors.RESET}\n")

    pilot_breakdown = [
        {
            'model': 'claude-haiku-4-5',
            'provider': 'Anthropic',
            'interviews': 16,
            'cost_per_interview': 0.074,
            'total_cost': 16 * 0.074
        },
        {
            'model': 'gpt-4o-mini',
            'provider': 'OpenAI',
            'interviews': 4,
            'cost_per_interview': 0.087,
            'total_cost': 4 * 0.087
        }
    ]

    pilot_total = 0
    for item in pilot_breakdown:
        print(f"{Colors.WHITE}{item['model']} ({item['provider']}){Colors.RESET}")
        print(f"  Interviews: {item['interviews']}")
        print(f"  Cost per interview: €{item['cost_per_interview']:.4f}")
        print(f"  Subtotal: €{item['total_cost']:.4f}\n")
        pilot_total += item['total_cost']

    print(f"{Colors.BOLD}{Colors.GREEN}Pilot Total:{Colors.RESET} €{pilot_total:.4f} ({pilot_total/global_budget_eur*100:.2f}% of budget)\n")

    # Full testing budget (80 interviews)
    print(f"{Colors.BOLD}{Colors.YELLOW}{'─'*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}FULL TESTING (80 interviews after pilot approval){Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{'─'*70}{Colors.RESET}\n")

    full_breakdown = [
        {
            'model': 'claude-haiku-4-5',
            'provider': 'Anthropic',
            'interviews': 64,
            'cost_per_interview': 0.074,
            'total_cost': 64 * 0.074
        },
        {
            'model': 'gpt-4o-mini',
            'provider': 'OpenAI',
            'interviews': 8,
            'cost_per_interview': 0.087,
            'total_cost': 8 * 0.087
        },
        {
            'model': 'claude-sonnet-4-5',
            'provider': 'Anthropic',
            'interviews': 8,
            'cost_per_interview': 0.110,
            'total_cost': 8 * 0.110
        }
    ]

    full_total = 0
    for item in full_breakdown:
        print(f"{Colors.WHITE}{item['model']} ({item['provider']}){Colors.RESET}")
        print(f"  Interviews: {item['interviews']}")
        print(f"  Cost per interview: €{item['cost_per_interview']:.4f}")
        print(f"  Subtotal: €{item['total_cost']:.4f}\n")
        full_total += item['total_cost']

    print(f"{Colors.BOLD}{Colors.GREEN}Full Testing Total:{Colors.RESET} €{full_total:.4f} ({full_total/global_budget_eur*100:.2f}% of budget)\n")

    # Grand total
    grand_total = pilot_total + full_total
    remaining = global_budget_eur - grand_total

    print(f"{Colors.BOLD}{Colors.CYAN}{'═'*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}TOTAL PHASE 4 COST ESTIMATE{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═'*70}{Colors.RESET}\n")

    print(f"{Colors.WHITE}Total Interviews:{Colors.RESET}     100")
    print(f"{Colors.WHITE}Total Estimated Cost:{Colors.RESET} €{grand_total:.2f}")
    print(f"{Colors.WHITE}Budget Allocated:{Colors.RESET}     €{global_budget_eur:.2f}")
    print(f"{Colors.GREEN}{Colors.BOLD}Remaining:{Colors.RESET}           €{remaining:.2f} ({remaining/global_budget_eur*100:.1f}%)\n")

    # Budget utilization bar
    utilization = grand_total / global_budget_eur * 100
    bar_width = 50
    filled = int(bar_width * utilization / 100)
    bar = '█' * filled + '░' * (bar_width - filled)

    print(f"{Colors.WHITE}Budget Utilization:{Colors.RESET}")
    print(f"{Colors.GREEN}{bar}{Colors.RESET} {utilization:.1f}%\n")

    # Cost breakdown by phase
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'─'*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}BREAKDOWN BY PHASE{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'─'*70}{Colors.RESET}\n")

    print(f"{Colors.WHITE}Pilot (20 interviews):{Colors.RESET}          €{pilot_total:.2f} ({pilot_total/grand_total*100:.1f}% of total)")
    print(f"{Colors.WHITE}Full Testing (80 interviews):{Colors.RESET}  €{full_total:.2f} ({full_total/grand_total*100:.1f}% of total)\n")

    # Cost monitoring features
    print(f"{Colors.BOLD}{Colors.CYAN}{'═'*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}COST MONITORING FEATURES{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═'*70}{Colors.RESET}\n")

    print(f"{Colors.GREEN}✅ Real-time cost tracking{Colors.RESET} - Per-interview cost display")
    print(f"{Colors.GREEN}✅ RED alerts every €5{Colors.RESET} - Terminal alerts when thresholds crossed")
    print(f"{Colors.GREEN}✅ Budget approval workflow{Colors.RESET} - Permission required for each batch")
    print(f"{Colors.GREEN}✅ Cost breakdown logging{Colors.RESET} - Detailed JSON logs for all costs")
    print(f"{Colors.GREEN}✅ Multi-provider tracking{Colors.RESET} - Separate budgets per model\n")

    print(f"{Colors.BOLD}{Colors.CYAN}{'═'*70}{Colors.RESET}\n")

    return pilot_total, full_total, grand_total


def request_global_approval():
    """Request user approval for Phase 4 global budget."""

    pilot_total, full_total, grand_total = display_phase4_budget()

    # Request approval
    print(f"{Colors.YELLOW}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.YELLOW}{Colors.BOLD}║  APPROVAL REQUIRED: Proceed with Phase 4 Testing?                ║{Colors.RESET}")
    print(f"{Colors.YELLOW}{Colors.BOLD}╚═══════════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

    print(f"{Colors.WHITE}Summary:{Colors.RESET}")
    print(f"  • 100 interviews total (20 pilot + 80 full)")
    print(f"  • Estimated cost: €{grand_total:.2f}")
    print(f"  • Budget: €100.00")
    print(f"  • Utilization: {grand_total/100*100:.1f}%")
    print(f"  • Cost monitoring: Real-time with alerts\n")

    print(f"{Colors.WHITE}This approval covers:{Colors.RESET}")
    print(f"  1. Pilot testing (20 interviews) - Will execute immediately")
    print(f"  2. Full testing (80 interviews) - Will require separate approval after pilot\n")

    print(f"{Colors.YELLOW}{Colors.BOLD}Do you approve this budget and want to proceed with Phase 4?{Colors.RESET}")
    print(f"{Colors.WHITE}Type 'yes' to approve and start pilot testing, or 'no' to cancel:{Colors.RESET} ", end='')

    response = input().strip().lower()

    if response in ['yes', 'y']:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ APPROVED!{Colors.RESET} Proceeding with Phase 4 pilot testing...\n")

        # Initialize budget tracker with approved budget
        tracker = BudgetTracker(global_budget_eur=100.0)

        # Set model budgets
        tracker.set_model_budget('claude-haiku-4-5', pilot_total)
        tracker.set_model_budget('gpt-4o-mini', 0.35)

        # Mark as approved
        tracker.approved_budgets.add('claude-haiku-4-5')
        tracker.approved_budgets.add('gpt-4o-mini')
        tracker._save_state()

        print(f"{Colors.CYAN}Budget tracker initialized and saved to outputs/budget_tracking.json{Colors.RESET}\n")

        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ CANCELLED{Colors.RESET} Phase 4 testing will not proceed.\n")
        return False


def main():
    """Main function."""
    approved = request_global_approval()

    if approved:
        print(f"{Colors.GREEN}Next steps:{Colors.RESET}")
        print(f"  1. Run pilot batch (16 interviews, Claude Haiku)")
        print(f"  2. Review pilot results")
        print(f"  3. Get approval for full testing")
        print(f"  4. Execute remaining 80 interviews\n")

        print(f"{Colors.CYAN}Commands to execute:{Colors.RESET}")
        print(f"{Colors.WHITE}# Pilot - 16 interviews on Claude Haiku{Colors.RESET}")
        print(f"python scripts/phase4_conduct_interviews.py \\")
        print(f"    --provider anthropic \\")
        print(f"    --model claude-haiku-4-5 \\")
        print(f"    --protocol data/interview_protocols.json \\")
        print(f"    --count 16\n")

        print(f"{Colors.WHITE}# Pilot - 4 interviews on OpenAI GPT{Colors.RESET}")
        print(f"python scripts/phase4_conduct_interviews.py \\")
        print(f"    --provider openai \\")
        print(f"    --model gpt-4o-mini \\")
        print(f"    --protocol data/interview_protocols.json \\")
        print(f"    --count 4\n")

        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
