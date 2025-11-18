#!/usr/bin/env python3
"""
Real-Time Cost Monitor with Alerts

Tracks AI API costs during execution and displays RED terminal alerts
when spending crosses €5 thresholds per model.

Features:
- Per-model cost tracking
- RED ANSI terminal alerts every €5
- Cumulative cost tracking
- Cost history logging
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional

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
    BG_RED = '\033[41m'
    RESET = '\033[0m'

class CostMonitor:
    """Monitor and track AI API costs with threshold alerts."""

    # Alert threshold in EUR
    ALERT_THRESHOLD_EUR = 5.0

    # USD to EUR conversion (approximate, update as needed)
    USD_TO_EUR = 0.92

    def __init__(self, log_file: str = 'outputs/cost_monitor.json'):
        """
        Initialize cost monitor.

        Args:
            log_file: Path to save cost tracking log
        """
        self.log_file = log_file
        self.model_costs = {}  # {model_name: total_cost_usd}
        self.model_alerts = {}  # {model_name: last_alert_threshold}
        self.model_tokens = {}  # {model_name: {input: X, output: Y, total: Z}}
        self.cost_history = []  # List of cost events

        # Ensure output directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Load existing data if available
        self._load_state()

    def _load_state(self):
        """Load existing cost tracking state from file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.model_costs = data.get('model_costs', {})
                    self.model_alerts = data.get('model_alerts', {})
                    self.model_tokens = data.get('model_tokens', {})
                    self.cost_history = data.get('cost_history', [])
            except Exception:
                pass  # Start fresh if file is corrupted

    def _save_state(self):
        """Save cost tracking state to file."""
        # Calculate total tokens across all models
        total_input = sum(tokens.get('input', 0) for tokens in self.model_tokens.values())
        total_output = sum(tokens.get('output', 0) for tokens in self.model_tokens.values())

        data = {
            'timestamp': datetime.now().isoformat(),
            'model_costs': self.model_costs,
            'model_alerts': self.model_alerts,
            'model_tokens': self.model_tokens,
            'cost_history': self.cost_history,
            'total_cost_usd': sum(self.model_costs.values()),
            'total_cost_eur': sum(self.model_costs.values()) * self.USD_TO_EUR,
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'total_tokens': total_input + total_output
        }

        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_cost(self, model: str, cost_usd: float, metadata: Optional[Dict] = None):
        """
        Add cost for a model and check if alert threshold crossed.

        Args:
            model: Model identifier (e.g., 'claude-haiku-4-5')
            cost_usd: Cost in USD
            metadata: Optional metadata (interview_id, tokens, etc.)
                     Should include 'input_tokens' and 'output_tokens' for exact tracking

        Returns:
            bool: True if alert threshold was crossed
        """
        # Initialize model if not seen before
        if model not in self.model_costs:
            self.model_costs[model] = 0.0
            self.model_alerts[model] = 0
            self.model_tokens[model] = {'input': 0, 'output': 0, 'total': 0}

        # Add cost
        old_cost = self.model_costs[model]
        self.model_costs[model] += cost_usd
        new_cost = self.model_costs[model]

        # Track token usage from metadata
        if metadata:
            input_tokens = metadata.get('input_tokens', 0)
            output_tokens = metadata.get('output_tokens', 0)

            self.model_tokens[model]['input'] += input_tokens
            self.model_tokens[model]['output'] += output_tokens
            self.model_tokens[model]['total'] += input_tokens + output_tokens

        # Convert to EUR
        old_cost_eur = old_cost * self.USD_TO_EUR
        new_cost_eur = new_cost * self.USD_TO_EUR

        # Log event (include token counts if available)
        event = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'cost_usd': cost_usd,
            'cost_eur': cost_usd * self.USD_TO_EUR,
            'cumulative_usd': new_cost,
            'cumulative_eur': new_cost_eur,
            'metadata': metadata or {}
        }

        # Add token counts to event if available
        if metadata:
            event['input_tokens'] = metadata.get('input_tokens', 0)
            event['output_tokens'] = metadata.get('output_tokens', 0)
            event['total_tokens'] = event['input_tokens'] + event['output_tokens']

        self.cost_history.append(event)

        # Check if we crossed a threshold
        old_threshold = int(old_cost_eur / self.ALERT_THRESHOLD_EUR)
        new_threshold = int(new_cost_eur / self.ALERT_THRESHOLD_EUR)

        alert_triggered = False
        if new_threshold > old_threshold:
            # Crossed a €5 threshold!
            threshold_amount = new_threshold * self.ALERT_THRESHOLD_EUR
            self._display_alert(model, new_cost_eur, threshold_amount)
            self.model_alerts[model] = new_threshold
            alert_triggered = True

        # Save state
        self._save_state()

        return alert_triggered

    def _display_alert(self, model: str, cumulative_eur: float, threshold: float):
        """Display RED terminal alert."""

        # Create dramatic alert
        alert_bar = f"{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}{'!'*70}{Colors.RESET}"

        print(f"\n{alert_bar}")
        print(f"{Colors.RED}{Colors.BOLD}🚨 COST ALERT: €{threshold:.0f} THRESHOLD CROSSED 🚨{Colors.RESET}")
        print(f"{Colors.RED}{Colors.BOLD}Model: {model}{Colors.RESET}")
        print(f"{Colors.RED}{Colors.BOLD}Cumulative Cost: €{cumulative_eur:.2f}{Colors.RESET}")
        print(f"{alert_bar}\n")

    def display_status(self, model: Optional[str] = None):
        """
        Display current cost status.

        Args:
            model: If specified, show only this model. Otherwise show all.
        """
        if model and model in self.model_costs:
            cost_usd = self.model_costs[model]
            cost_eur = cost_usd * self.USD_TO_EUR
            tokens = self.model_tokens.get(model, {'input': 0, 'output': 0, 'total': 0})

            print(f"\n{Colors.CYAN}Cost Status for {model}:{Colors.RESET}")
            print(f"  ${cost_usd:.4f} USD / €{cost_eur:.4f} EUR")
            print(f"  {Colors.WHITE}Tokens: {tokens['input']:,} input + {tokens['output']:,} output = {tokens['total']:,} total{Colors.RESET}")

            # Show progress to next threshold
            next_threshold = (int(cost_eur / self.ALERT_THRESHOLD_EUR) + 1) * self.ALERT_THRESHOLD_EUR
            remaining = next_threshold - cost_eur

            if remaining > 0:
                print(f"  {Colors.YELLOW}€{remaining:.2f} until next €{next_threshold:.0f} alert{Colors.RESET}")

        else:
            print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.BOLD}  Cost Monitoring Status{Colors.RESET}")
            print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")

            total_usd = sum(self.model_costs.values())
            total_eur = total_usd * self.USD_TO_EUR

            # Calculate total tokens
            total_input = sum(tokens.get('input', 0) for tokens in self.model_tokens.values())
            total_output = sum(tokens.get('output', 0) for tokens in self.model_tokens.values())
            total_tokens = total_input + total_output

            for model_name, cost_usd in sorted(self.model_costs.items()):
                cost_eur = cost_usd * self.USD_TO_EUR
                alerts = self.model_alerts.get(model_name, 0)
                tokens = self.model_tokens.get(model_name, {'input': 0, 'output': 0, 'total': 0})

                alert_str = f" ({alerts} alerts)" if alerts > 0 else ""

                print(f"{Colors.WHITE}{model_name}:{Colors.RESET}")
                print(f"  ${cost_usd:.4f} USD / €{cost_eur:.4f} EUR{Colors.RED}{alert_str}{Colors.RESET}")
                print(f"  Tokens: {tokens['input']:,} in / {tokens['output']:,} out / {tokens['total']:,} total")

            print(f"\n{Colors.BOLD}Total Cost: ${total_usd:.4f} USD / €{total_eur:.4f} EUR{Colors.RESET}")
            print(f"{Colors.BOLD}Total Tokens: {total_input:,} in / {total_output:,} out / {total_tokens:,} total{Colors.RESET}")
            print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")

    def get_total_cost(self, in_eur: bool = True) -> float:
        """
        Get total cost across all models.

        Args:
            in_eur: If True, return EUR. Otherwise USD.

        Returns:
            Total cost
        """
        total_usd = sum(self.model_costs.values())
        return total_usd * self.USD_TO_EUR if in_eur else total_usd

    def get_model_cost(self, model: str, in_eur: bool = True) -> float:
        """
        Get cost for a specific model.

        Args:
            model: Model identifier
            in_eur: If True, return EUR. Otherwise USD.

        Returns:
            Model cost
        """
        cost_usd = self.model_costs.get(model, 0.0)
        return cost_usd * self.USD_TO_EUR if in_eur else cost_usd

    def reset(self):
        """Reset all cost tracking."""
        self.model_costs = {}
        self.model_alerts = {}
        self.model_tokens = {}
        self.cost_history = []
        self._save_state()

        print(f"{Colors.YELLOW}Cost monitor reset{Colors.RESET}")


# Global instance for easy access
_global_monitor = None

def get_monitor() -> CostMonitor:
    """Get global cost monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = CostMonitor()
    return _global_monitor


# Example usage
if __name__ == "__main__":
    monitor = CostMonitor('test_cost_monitor.json')

    # Simulate costs
    print("Simulating cost accumulation with alerts...\n")

    # Add costs gradually
    for i in range(100):
        cost = 0.08  # $0.08 per interview (Claude Haiku)
        monitor.add_cost('claude-haiku-4-5', cost, {
            'interview_id': f'INT_{i:03d}',
            'tokens': 10000
        })

        if (i + 1) % 20 == 0:
            monitor.display_status('claude-haiku-4-5')

    # Final status
    monitor.display_status()
