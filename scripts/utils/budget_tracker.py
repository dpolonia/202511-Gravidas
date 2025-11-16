#!/usr/bin/env python3
"""
Budget Tracker for Phase 4 Testing

Manages global and per-model budgets with approval workflow.
Tracks spending against budgets and warns when approaching limits.
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
from utils.cost_monitor import CostMonitor, Colors

class BudgetTracker:
    """Track and manage budgets for Phase 4 testing."""

    def __init__(self,
                 global_budget_eur: float = 100.0,
                 log_file: str = 'outputs/budget_tracking.json'):
        """
        Initialize budget tracker.

        Args:
            global_budget_eur: Total budget for Phase 4 in EUR
            log_file: Path to save budget tracking data
        """
        self.global_budget_eur = global_budget_eur
        self.log_file = log_file
        self.model_budgets = {}  # {model: budget_eur}
        self.approved_budgets = set()  # Set of approved model names
        self.cost_monitor = CostMonitor()

        # Ensure output directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Load existing data if available
        self._load_state()

    def _load_state(self):
        """Load existing budget state from file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.model_budgets = data.get('model_budgets', {})
                    self.approved_budgets = set(data.get('approved_budgets', []))
            except Exception:
                pass  # Start fresh if file is corrupted

    def _save_state(self):
        """Save budget state to file."""
        data = {
            'timestamp': datetime.now().isoformat(),
            'global_budget_eur': self.global_budget_eur,
            'model_budgets': self.model_budgets,
            'approved_budgets': list(self.approved_budgets),
            'total_allocated': sum(self.model_budgets.values()),
            'total_spent': self.cost_monitor.get_total_cost(in_eur=True),
            'remaining_budget': self.get_remaining_budget()
        }

        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)

    def set_model_budget(self, model: str, budget_eur: float):
        """
        Set budget for a specific model.

        Args:
            model: Model identifier
            budget_eur: Budget in EUR
        """
        self.model_budgets[model] = budget_eur
        self._save_state()

    def get_remaining_budget(self) -> float:
        """Get remaining global budget in EUR."""
        spent = self.cost_monitor.get_total_cost(in_eur=True)
        return self.global_budget_eur - spent

    def get_model_remaining_budget(self, model: str) -> float:
        """Get remaining budget for specific model in EUR."""
        budget = self.model_budgets.get(model, 0.0)
        spent = self.cost_monitor.get_model_cost(model, in_eur=True)
        return budget - spent

    def display_global_budget(self):
        """Display global budget overview."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}  GLOBAL BUDGET OVERVIEW{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

        total_allocated = sum(self.model_budgets.values())
        total_spent = self.cost_monitor.get_total_cost(in_eur=True)
        remaining = self.get_remaining_budget()

        print(f"{Colors.WHITE}Total Budget:{Colors.RESET}      €{self.global_budget_eur:.2f}")
        print(f"{Colors.YELLOW}Allocated:{Colors.RESET}        €{total_allocated:.2f} ({total_allocated/self.global_budget_eur*100:.1f}%)")
        print(f"{Colors.RED}Spent:{Colors.RESET}            €{total_spent:.4f} ({total_spent/self.global_budget_eur*100:.2f}%)")
        print(f"{Colors.GREEN}Remaining:{Colors.RESET}        €{remaining:.2f} ({remaining/self.global_budget_eur*100:.1f}%)")

        # Progress bar
        spent_pct = min(100, total_spent / self.global_budget_eur * 100)
        bar_width = 50
        filled = int(bar_width * spent_pct / 100)
        bar = '█' * filled + '░' * (bar_width - filled)

        if spent_pct < 50:
            color = Colors.GREEN
        elif spent_pct < 80:
            color = Colors.YELLOW
        else:
            color = Colors.RED

        print(f"\n{color}{bar}{Colors.RESET} {spent_pct:.2f}%")
        print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}\n")

    def display_model_budget(self, model: str,
                            interviews_planned: int,
                            cost_per_interview: float):
        """
        Display budget for a specific model batch.

        Args:
            model: Model identifier
            interviews_planned: Number of interviews planned
            cost_per_interview: Estimated cost per interview in EUR
        """
        budget = self.model_budgets.get(model, 0.0)
        spent = self.cost_monitor.get_model_cost(model, in_eur=True)
        estimated_cost = interviews_planned * cost_per_interview
        remaining_after = budget - spent - estimated_cost

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}  MODEL BUDGET: {model}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}\n")

        print(f"{Colors.WHITE}Interviews Planned:{Colors.RESET}   {interviews_planned}")
        print(f"{Colors.WHITE}Cost per Interview:{Colors.RESET}  €{cost_per_interview:.4f}")
        print(f"{Colors.YELLOW}Estimated Total:{Colors.RESET}      €{estimated_cost:.4f}")
        print()
        print(f"{Colors.WHITE}Model Budget:{Colors.RESET}         €{budget:.4f}")
        print(f"{Colors.RED}Already Spent:{Colors.RESET}       €{spent:.4f}")
        print(f"{Colors.CYAN}Remaining:{Colors.RESET}           €{(budget - spent):.4f}")
        print(f"{Colors.GREEN}After This Batch:{Colors.RESET}    €{remaining_after:.4f}")

        # Warning if over budget
        if remaining_after < 0:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  WARNING: This batch exceeds model budget by €{abs(remaining_after):.4f}{Colors.RESET}")

        # Show percentage
        if budget > 0:
            pct_used = (spent + estimated_cost) / budget * 100
            print(f"\n{Colors.WHITE}Budget Utilization:{Colors.RESET}  {pct_used:.1f}%")

        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}\n")

    def request_approval(self, model: str,
                        interviews_planned: int,
                        cost_per_interview: float) -> bool:
        """
        Request user approval for model budget.

        Args:
            model: Model identifier
            interviews_planned: Number of interviews planned
            cost_per_interview: Estimated cost per interview in EUR

        Returns:
            bool: True if approved
        """
        # Display budget
        self.display_model_budget(model, interviews_planned, cost_per_interview)

        # Request approval
        print(f"{Colors.YELLOW}{Colors.BOLD}Do you approve this budget and want to proceed?{Colors.RESET}")
        print(f"{Colors.WHITE}Type 'yes' to approve and continue, or 'no' to cancel:{Colors.RESET} ", end='')

        response = input().strip().lower()

        if response in ['yes', 'y']:
            self.approved_budgets.add(model)
            self._save_state()

            print(f"{Colors.GREEN}✅ Approved! Proceeding with {interviews_planned} interviews on {model}{Colors.RESET}\n")
            return True
        else:
            print(f"{Colors.RED}❌ Cancelled. Skipping {model} batch{Colors.RESET}\n")
            return False

    def check_budget_status(self, model: str) -> Tuple[bool, str]:
        """
        Check if model is within budget.

        Args:
            model: Model identifier

        Returns:
            (within_budget, message)
        """
        budget = self.model_budgets.get(model, 0.0)
        spent = self.cost_monitor.get_model_cost(model, in_eur=True)
        remaining = budget - spent

        if remaining <= 0:
            return False, f"Budget exhausted (€{abs(remaining):.4f} over)"
        elif remaining < budget * 0.1:
            return True, f"Warning: Only €{remaining:.4f} remaining (< 10%)"
        else:
            return True, f"OK: €{remaining:.4f} remaining"

    def generate_budget_report(self) -> Dict:
        """Generate comprehensive budget report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'global_budget': {
                'total_eur': self.global_budget_eur,
                'allocated_eur': sum(self.model_budgets.values()),
                'spent_eur': self.cost_monitor.get_total_cost(in_eur=True),
                'remaining_eur': self.get_remaining_budget(),
                'utilization_pct': (self.cost_monitor.get_total_cost(in_eur=True) /
                                   self.global_budget_eur * 100)
            },
            'model_budgets': {}
        }

        for model, budget in self.model_budgets.items():
            spent = self.cost_monitor.get_model_cost(model, in_eur=True)
            report['model_budgets'][model] = {
                'budget_eur': budget,
                'spent_eur': spent,
                'remaining_eur': budget - spent,
                'utilization_pct': (spent / budget * 100) if budget > 0 else 0,
                'approved': model in self.approved_budgets
            }

        return report


# Example usage
if __name__ == "__main__":
    tracker = BudgetTracker(global_budget_eur=100.0)

    # Set model budgets
    tracker.set_model_budget('claude-haiku-4-5', 1.28)
    tracker.set_model_budget('gpt-4o-mini', 0.38)

    # Display global budget
    tracker.display_global_budget()

    # Request approval for a batch
    approved = tracker.request_approval(
        model='claude-haiku-4-5',
        interviews_planned=16,
        cost_per_interview=0.08
    )

    if approved:
        print("Proceeding with interviews...")

    # Generate report
    report = tracker.generate_budget_report()
    print(json.dumps(report, indent=2))
