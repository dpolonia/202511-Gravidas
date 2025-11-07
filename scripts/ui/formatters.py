"""
UI formatting utilities for consistent terminal output.

This module provides standardized formatting for:
- Headers and section dividers
- Tables and lists
- Success/warning/error messages
- Progress indicators
- Cost and time estimates
"""

from typing import List, Dict, Any, Optional
import sys


# Terminal colors (ANSI escape codes)
class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @staticmethod
    def is_terminal():
        """Check if output is to a terminal (supports colors)."""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def format_header(text: str, width: int = 80, char: str = '=') -> str:
    """
    Format a centered header with decorative borders.

    Args:
        text: Header text
        width: Total width of the header
        char: Character to use for borders

    Returns:
        Formatted header string

    Example:
        >>> print(format_header("Interview Pipeline"))
        ================================================================================
                                    Interview Pipeline
        ================================================================================
    """
    border = char * width
    padding = (width - len(text)) // 2
    centered = ' ' * padding + text
    return f"{border}\n{centered}\n{border}"


def format_section(title: str, width: int = 80) -> str:
    """
    Format a section header.

    Args:
        title: Section title
        width: Total width

    Returns:
        Formatted section header

    Example:
        >>> print(format_section("Model Selection"))
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          Model Selection
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    border = '━' * width
    return f"\n{border}\n  {title}\n{border}"


def format_subsection(title: str, width: int = 80) -> str:
    """
    Format a subsection header (lighter than section).

    Args:
        title: Subsection title
        width: Total width

    Returns:
        Formatted subsection header

    Example:
        >>> print(format_subsection("Configuration"))
        ────────────────────────────────────────────────────────────────────────────────
          Configuration
        ────────────────────────────────────────────────────────────────────────────────
    """
    border = '─' * width
    return f"\n{border}\n  {title}\n{border}"


def format_success(message: str) -> str:
    """Format a success message with green checkmark."""
    if Colors.is_terminal():
        return f"{Colors.GREEN}✅ {message}{Colors.END}"
    return f"✅ {message}"


def format_warning(message: str) -> str:
    """Format a warning message with yellow icon."""
    if Colors.is_terminal():
        return f"{Colors.YELLOW}⚠️  {message}{Colors.END}"
    return f"⚠️  {message}"


def format_error(message: str) -> str:
    """Format an error message with red cross."""
    if Colors.is_terminal():
        return f"{Colors.RED}❌ {message}{Colors.END}"
    return f"❌ {message}"


def format_info(message: str) -> str:
    """Format an info message with blue icon."""
    if Colors.is_terminal():
        return f"{Colors.CYAN}ℹ️  {message}{Colors.END}"
    return f"ℹ️  {message}"


def format_progress(message: str) -> str:
    """Format a progress message with spinner."""
    if Colors.is_terminal():
        return f"{Colors.BLUE}⏳ {message}{Colors.END}"
    return f"⏳ {message}"


def format_cost(amount: float, currency: str = '$') -> str:
    """
    Format a cost amount with appropriate precision.

    Args:
        amount: Cost amount
        currency: Currency symbol

    Returns:
        Formatted cost string

    Example:
        >>> format_cost(12.50)
        '$12.50'
        >>> format_cost(0.0025)
        '$0.0025'
    """
    if amount < 0.01:
        return f"{currency}{amount:.4f}"
    return f"{currency}{amount:.2f}"


def format_number(num: int) -> str:
    """
    Format a number with thousands separators.

    Args:
        num: Number to format

    Returns:
        Formatted number string

    Example:
        >>> format_number(1000000)
        '1,000,000'
    """
    return f"{num:,}"


def format_percentage(value: float) -> str:
    """
    Format a percentage value.

    Args:
        value: Percentage (0-100)

    Returns:
        Formatted percentage string

    Example:
        >>> format_percentage(85.7)
        '85.7%'
    """
    if value >= 10:
        return f"{value:.1f}%"
    return f"{value:.2f}%"


def format_table(headers: List[str], rows: List[List[str]],
                 col_widths: Optional[List[int]] = None) -> str:
    """
    Format data as a simple text table.

    Args:
        headers: Column headers
        rows: Data rows
        col_widths: Optional column widths (auto-calculated if None)

    Returns:
        Formatted table string

    Example:
        >>> headers = ['Name', 'Age', 'City']
        >>> rows = [['Alice', '30', 'NYC'], ['Bob', '25', 'LA']]
        >>> print(format_table(headers, rows))
    """
    # Auto-calculate column widths if not provided
    if col_widths is None:
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Format header
    header_line = '  '.join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = '  '.join('-' * w for w in col_widths)

    # Format rows
    formatted_rows = []
    for row in rows:
        formatted_row = '  '.join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        formatted_rows.append(formatted_row)

    return '\n'.join([header_line, separator] + formatted_rows)


def format_bullet_list(items: List[str], indent: int = 2) -> str:
    """
    Format items as a bullet list.

    Args:
        items: List items
        indent: Indentation level (spaces)

    Returns:
        Formatted bullet list

    Example:
        >>> items = ['First item', 'Second item', 'Third item']
        >>> print(format_bullet_list(items))
          • First item
          • Second item
          • Third item
    """
    indent_str = ' ' * indent
    return '\n'.join(f"{indent_str}• {item}" for item in items)


def format_numbered_list(items: List[str], indent: int = 2, start: int = 1) -> str:
    """
    Format items as a numbered list.

    Args:
        items: List items
        indent: Indentation level (spaces)
        start: Starting number

    Returns:
        Formatted numbered list

    Example:
        >>> items = ['First step', 'Second step', 'Third step']
        >>> print(format_numbered_list(items))
          1. First step
          2. Second step
          3. Third step
    """
    indent_str = ' ' * indent
    return '\n'.join(f"{indent_str}{i+start}. {item}" for i, item in enumerate(items))


def format_key_value(key: str, value: str, width: int = 30, separator: str = ': ') -> str:
    """
    Format a key-value pair with aligned values.

    Args:
        key: Key name
        value: Value
        width: Width for key column
        separator: Separator between key and value

    Returns:
        Formatted key-value string

    Example:
        >>> print(format_key_value('Model', 'Claude Sonnet 4.5'))
        Model                        : Claude Sonnet 4.5
    """
    return f"{key.ljust(width)}{separator}{value}"


def format_box(text: str, width: int = 80, padding: int = 2) -> str:
    """
    Format text in a box with borders.

    Args:
        text: Text to display (can be multi-line)
        width: Total box width
        padding: Padding inside box

    Returns:
        Formatted box

    Example:
        >>> print(format_box("Important Message"))
        ╔════════════════════════════════════════════════════════════════════════════╗
        ║  Important Message                                                         ║
        ╚════════════════════════════════════════════════════════════════════════════╗
    """
    inner_width = width - 2 * (padding + 1)
    top = '╔' + '═' * (width - 2) + '╗'
    bottom = '╚' + '═' * (width - 2) + '╝'

    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        padded = (' ' * padding) + line.ljust(inner_width) + (' ' * padding)
        formatted_lines.append(f"║{padded}║")

    return '\n'.join([top] + formatted_lines + [bottom])


def format_progress_bar(current: int, total: int, width: int = 40,
                       show_percentage: bool = True, show_numbers: bool = True) -> str:
    """
    Format a text-based progress bar.

    Args:
        current: Current progress value
        total: Total value
        width: Width of the progress bar
        show_percentage: Show percentage
        show_numbers: Show numeric progress

    Returns:
        Formatted progress bar

    Example:
        >>> print(format_progress_bar(75, 100))
        [████████████████████████████░░░░░░░░░░░░] 75/100 (75%)
    """
    if total == 0:
        percentage = 0
    else:
        percentage = (current / total) * 100

    filled = int((current / total) * width) if total > 0 else 0
    bar = '█' * filled + '░' * (width - filled)

    parts = [f"[{bar}]"]
    if show_numbers:
        parts.append(f"{current}/{total}")
    if show_percentage:
        parts.append(f"({percentage:.0f}%)")

    return ' '.join(parts)


def format_time_estimate(seconds: float) -> str:
    """
    Format a time duration in human-readable form.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string

    Example:
        >>> format_time_estimate(125)
        '2m 5s'
        >>> format_time_estimate(3665)
        '1h 1m 5s'
    """
    if seconds < 60:
        return f"{int(seconds)}s"

    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)

    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    return f"{hours}h {remaining_minutes}m {remaining_seconds}s"


def clear_line():
    """Clear the current line (for updating progress in place)."""
    if Colors.is_terminal():
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        sys.stdout.flush()


def format_status_dashboard(stats: Dict[str, Any], width: int = 80) -> str:
    """
    Format a status dashboard with statistics.

    Args:
        stats: Dictionary of statistics to display
        width: Total width of dashboard

    Returns:
        Formatted dashboard

    Example:
        >>> stats = {'processed': 80, 'total': 100, 'cost': 12.50, 'eta': '5m'}
        >>> print(format_status_dashboard(stats))
    """
    lines = []

    top = '╔' + '═' * (width - 2) + '╗'
    bottom = '╚' + '═' * (width - 2) + '╝'

    lines.append(top)

    for key, value in stats.items():
        # Format the key nicely
        formatted_key = key.replace('_', ' ').title()
        line_content = f"  {formatted_key}: {value}"
        padding = ' ' * (width - len(line_content) - 2)
        lines.append(f"║{line_content}{padding}║")

    lines.append(bottom)

    return '\n'.join(lines)


# Export public API
__all__ = [
    'Colors',
    'format_header',
    'format_section',
    'format_subsection',
    'format_success',
    'format_warning',
    'format_error',
    'format_info',
    'format_progress',
    'format_cost',
    'format_number',
    'format_percentage',
    'format_table',
    'format_bullet_list',
    'format_numbered_list',
    'format_key_value',
    'format_box',
    'format_progress_bar',
    'format_time_estimate',
    'clear_line',
    'format_status_dashboard',
]
