"""Analysis wrapper.

Imports the terminal app's functions so both the terminal and the
web API share the exact same logic. If the rules change in
terminal/main.py, the web API picks up the change automatically.
"""
import sys
from pathlib import Path

# Add the terminal folder to Python's search path so we can import main.py from there.
_terminal_dir = Path(__file__).resolve().parent.parent.parent / "terminal"
if str(_terminal_dir) not in sys.path:
    sys.path.insert(0, str(_terminal_dir))

# Import the analysis functions we need. The terminal's main.py defines all of these.
from main import (  # noqa: E402
    clean_and_split,
    count_genre_matches,
    calculate_percentages,
    find_errors,
    calculate_score,
    choose_comment,
    parse_scenes,
    detect_language,
    count_speeches,
    dialogue_ratio,
    estimate_length,
    explain_simply,
    find_props_and_costumes,
)