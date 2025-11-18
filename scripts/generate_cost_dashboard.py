#!/usr/bin/env python3
"""
Cost Dashboard Generator

Generates an interactive HTML dashboard for visualizing AI API costs
tracked during interview execution.

Features:
- Real-time cost monitoring across multiple providers
- Interactive charts using Chart.js
- Per-model cost breakdowns
- Token usage visualization
- Cost trends over time
- Multi-provider comparison

Usage:
    python scripts/generate_cost_dashboard.py
    python scripts/generate_cost_dashboard.py --input outputs/cost_monitor.json --output outputs/cost_dashboard.html
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


def load_cost_data(cost_file: str) -> Dict[str, Any]:
    """Load cost monitoring data from JSON file."""
    with open(cost_file, 'r') as f:
        return json.load(f)


def extract_model_provider(model_name: str) -> str:
    """Extract provider from model name."""
    if 'claude' in model_name.lower() or 'anthropic' in model_name.lower():
        return 'Anthropic'
    elif 'gpt' in model_name.lower() or 'openai' in model_name.lower():
        return 'OpenAI'
    elif 'gemini' in model_name.lower() or 'google' in model_name.lower():
        return 'Google'
    elif 'grok' in model_name.lower() or 'xai' in model_name.lower():
        return 'xAI'
    else:
        return 'Unknown'


def generate_html_dashboard(data: Dict[str, Any], output_file: str):
    """Generate interactive HTML dashboard."""

    # Extract data
    timestamp = data.get('timestamp', datetime.now().isoformat())
    model_costs = data.get('model_costs', {})
    model_tokens = data.get('model_tokens', {})
    cost_history = data.get('cost_history', [])
    total_cost_usd = data.get('total_cost_usd', 0)
    total_cost_eur = data.get('total_cost_eur', 0)
    total_input_tokens = data.get('total_input_tokens', 0)
    total_output_tokens = data.get('total_output_tokens', 0)
    total_tokens = data.get('total_tokens', 0)

    # Prepare model data for charts
    model_labels = list(model_costs.keys())
    model_cost_values_usd = [model_costs[m] for m in model_labels]
    model_cost_values_eur = [cost * 0.92 for cost in model_cost_values_usd]  # USD to EUR

    # Token data per model
    model_input_tokens = [model_tokens.get(m, {}).get('input', 0) for m in model_labels]
    model_output_tokens = [model_tokens.get(m, {}).get('output', 0) for m in model_labels]

    # Provider aggregation
    provider_costs = {}
    for model, cost in model_costs.items():
        provider = extract_model_provider(model)
        provider_costs[provider] = provider_costs.get(provider, 0) + cost

    provider_labels = list(provider_costs.keys())
    provider_values = [provider_costs[p] * 0.92 for p in provider_labels]  # EUR

    # Cost over time (last 100 events for clarity)
    recent_history = cost_history[-100:] if len(cost_history) > 100 else cost_history
    time_labels = [h['timestamp'][-8:-3] if len(h.get('timestamp', '')) > 8 else str(i)
                   for i, h in enumerate(recent_history)]

    # Cumulative cost over time per model
    model_cumulative_series = {}
    for event in recent_history:
        model = event.get('model', 'unknown')
        if model not in model_cumulative_series:
            model_cumulative_series[model] = []
        model_cumulative_series[model].append(event.get('cumulative_eur', 0))

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gravidas AI Cost Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}

        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}

        .timestamp {{
            color: #999;
            font-size: 0.9em;
            margin-top: 10px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}

        .stat-label {{
            color: #666;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .stat-sublabel {{
            color: #999;
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .chart-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }}

        .chart-wrapper {{
            position: relative;
            height: 300px;
        }}

        .full-width {{
            grid-column: 1 / -1;
        }}

        footer {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            color: #666;
        }}

        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💰 Gravidas AI Cost Dashboard</h1>
            <div class="subtitle">Real-time cost monitoring for synthetic interview generation</div>
            <div class="timestamp">Last Updated: {timestamp}</div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Cost</div>
                <div class="stat-value">€{total_cost_eur:.4f}</div>
                <div class="stat-sublabel">${total_cost_usd:.4f} USD</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Total Tokens</div>
                <div class="stat-value">{total_tokens:,}</div>
                <div class="stat-sublabel">{total_input_tokens:,} in / {total_output_tokens:,} out</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Models Used</div>
                <div class="stat-value">{len(model_costs)}</div>
                <div class="stat-sublabel">{len(provider_costs)} providers</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">API Calls</div>
                <div class="stat-value">{len(cost_history):,}</div>
                <div class="stat-sublabel">Total requests</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">Cost by Model (EUR)</div>
                <div class="chart-wrapper">
                    <canvas id="modelCostChart"></canvas>
                </div>
            </div>

            <div class="chart-container">
                <div class="chart-title">Cost by Provider (EUR)</div>
                <div class="chart-wrapper">
                    <canvas id="providerCostChart"></canvas>
                </div>
            </div>

            <div class="chart-container">
                <div class="chart-title">Token Usage by Model</div>
                <div class="chart-wrapper">
                    <canvas id="tokenChart"></canvas>
                </div>
            </div>

            <div class="chart-container">
                <div class="chart-title">Cost per 1M Tokens (EUR)</div>
                <div class="chart-wrapper">
                    <canvas id="efficiencyChart"></canvas>
                </div>
            </div>

            <div class="chart-container full-width">
                <div class="chart-title">Cumulative Cost Over Time (Last 100 API Calls)</div>
                <div class="chart-wrapper" style="height: 400px;">
                    <canvas id="timelineChart"></canvas>
                </div>
            </div>
        </div>

        <footer>
            <p>Generated by Gravidas Cost Dashboard Generator</p>
            <p>Synthetic Gravidas Research Project - v1.2.0</p>
        </footer>
    </div>

    <script>
        // Chart.js configuration
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

        const colors = [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(237, 100, 166, 0.8)',
            'rgba(255, 154, 158, 0.8)',
            'rgba(250, 208, 196, 0.8)',
            'rgba(165, 177, 194, 0.8)'
        ];

        // Model Cost Chart (Pie)
        new Chart(document.getElementById('modelCostChart'), {{
            type: 'pie',
            data: {{
                labels: {json.dumps(model_labels)},
                datasets: [{{
                    data: {json.dumps(model_cost_values_eur)},
                    backgroundColor: colors
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.label + ': €' + context.parsed.toFixed(4);
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Provider Cost Chart (Doughnut)
        new Chart(document.getElementById('providerCostChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(provider_labels)},
                datasets: [{{
                    data: {json.dumps(provider_values)},
                    backgroundColor: colors
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.label + ': €' + context.parsed.toFixed(4);
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Token Usage Chart (Bar)
        new Chart(document.getElementById('tokenChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(model_labels)},
                datasets: [
                    {{
                        label: 'Input Tokens',
                        data: {json.dumps(model_input_tokens)},
                        backgroundColor: 'rgba(102, 126, 234, 0.8)'
                    }},
                    {{
                        label: 'Output Tokens',
                        data: {json.dumps(model_output_tokens)},
                        backgroundColor: 'rgba(118, 75, 162, 0.8)'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        stacked: true
                    }},
                    y: {{
                        stacked: true,
                        ticks: {{
                            callback: function(value) {{
                                return (value / 1000).toFixed(0) + 'k';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});

        // Efficiency Chart (Cost per 1M tokens)
        const efficiencyData = {json.dumps(model_labels)}.map((model, i) => {{
            const tokens = {json.dumps(model_input_tokens)}[i] + {json.dumps(model_output_tokens)}[i];
            const cost = {json.dumps(model_cost_values_eur)}[i];
            return tokens > 0 ? (cost / tokens * 1000000) : 0;
        }});

        new Chart(document.getElementById('efficiencyChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(model_labels)},
                datasets: [{{
                    label: 'EUR per 1M Tokens',
                    data: efficiencyData,
                    backgroundColor: 'rgba(237, 100, 166, 0.8)'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return '€' + context.parsed.y.toFixed(2) + ' per 1M tokens';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        // Timeline Chart (Line)
        const timelineDatasets = [];
        const modelColors = {{}};
        {json.dumps(model_labels)}.forEach((model, i) => {{
            modelColors[model] = colors[i % colors.length];
        }});

        // Build datasets for each model
        const modelData = {json.dumps(model_cumulative_series)};
        Object.keys(modelData).forEach((model, i) => {{
            timelineDatasets.push({{
                label: model,
                data: modelData[model],
                borderColor: modelColors[model] || colors[i % colors.length],
                backgroundColor: 'transparent',
                tension: 0.1,
                borderWidth: 2
            }});
        }});

        new Chart(document.getElementById('timelineChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(time_labels)},
                datasets: timelineDatasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': €' + context.parsed.y.toFixed(4);
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return '€' + value.toFixed(4);
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    # Write HTML file
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"✅ Dashboard generated: {output_file}")
    print(f"📊 Total Cost: €{total_cost_eur:.4f} (${total_cost_usd:.4f} USD)")
    print(f"🔢 Total Tokens: {total_tokens:,}")
    print(f"📈 Models: {len(model_costs)}")
    print(f"📞 API Calls: {len(cost_history):,}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Generate cost monitoring dashboard')
    parser.add_argument('--input', type=str, default='outputs/cost_monitor.json',
                       help='Input cost monitor JSON file')
    parser.add_argument('--output', type=str, default='outputs/cost_dashboard.html',
                       help='Output HTML dashboard file')

    args = parser.parse_args()

    # Check if input file exists
    if not Path(args.input).exists():
        print(f"❌ Error: Cost monitor file not found: {args.input}")
        print(f"💡 Run interviews first to generate cost data")
        return 1

    # Load data
    print(f"📂 Loading cost data from {args.input}...")
    data = load_cost_data(args.input)

    # Generate dashboard
    print(f"🎨 Generating interactive dashboard...")
    generate_html_dashboard(data, args.output)

    print(f"\n🌐 Open {args.output} in your browser to view the dashboard")

    return 0


if __name__ == "__main__":
    exit(main())
