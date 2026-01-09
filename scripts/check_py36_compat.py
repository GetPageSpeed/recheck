#!/usr/bin/env python
"""Check for Python 3.7+ patterns that break Python 3.6 compatibility."""

import os
import re
import sys

# Patterns that require Python 3.7+
# Format: (regex, message)
INCOMPATIBLE_PATTERNS = [
    # subprocess.run text=True requires 3.7+ (use universal_newlines=True)
    (
        r"subprocess\.run\([^)]*\btext\s*=\s*True",
        "Use universal_newlines=True instead of text=True (Python 3.7+)",
    ),
    # subprocess.Popen text=True requires 3.7+
    (
        r"subprocess\.Popen\([^)]*\btext\s*=\s*True",
        "Use universal_newlines=True instead of text=True (Python 3.7+)",
    ),
    # from __future__ import annotations requires 3.7+ (PEP 563)
    (
        r"^from __future__ import annotations",
        "from __future__ import annotations requires Python 3.7+",
    ),
    # := walrus operator requires 3.8+ (but not in strings/comments)
    (r"(?<!['\"]):\s*=(?!['\"])", "Walrus operator := requires Python 3.8+"),
    # positional-only params (/) require 3.8+
    (r"def \w+\([^)]*,\s*/", "Positional-only parameters (/) require Python 3.8+"),
    # Union type syntax with | requires 3.10+
    (r"\) -> \w+ \| \w+:", "Union type syntax with | requires Python 3.10+"),
    (r": \w+ \| \w+ =", "Union type syntax with | requires Python 3.10+"),
    # dict/list/set generic syntax requires 3.9+ without __future__.annotations
    (r": dict\[", "dict[] generic syntax requires Python 3.9+ (use Dict from typing)"),
    (r": list\[", "list[] generic syntax requires Python 3.9+ (use List from typing)"),
    (r": set\[", "set[] generic syntax requires Python 3.9+ (use Set from typing)"),
    (
        r": tuple\[",
        "tuple[] generic syntax requires Python 3.9+ (use Tuple from typing)",
    ),
    (r"-> dict\[", "dict[] generic syntax requires Python 3.9+ (use Dict from typing)"),
    (r"-> list\[", "list[] generic syntax requires Python 3.9+ (use List from typing)"),
    (r"-> set\[", "set[] generic syntax requires Python 3.9+ (use Set from typing)"),
    (
        r"-> tuple\[",
        "tuple[] generic syntax requires Python 3.9+ (use Tuple from typing)",
    ),
]

# Files to skip (this script itself uses patterns as string literals)
SKIP_FILES = {"check_py36_compat.py"}


def check_file(filepath):
    """Check a single file for Python 3.6 incompatibilities."""
    # Skip files that contain pattern definitions (like this script)
    if os.path.basename(filepath) in SKIP_FILES:
        return []

    issues = []
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.read().splitlines()

        for pattern, message in INCOMPATIBLE_PATTERNS:
            for i, line in enumerate(lines, 1):
                # Skip comments and string-only lines
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if re.search(pattern, line):
                    issues.append((filepath, i, message))
    except (OSError, UnicodeDecodeError):
        pass
    return issues


def main():
    """Check all provided files."""
    if len(sys.argv) < 2:
        return 0

    all_issues = []
    for filepath in sys.argv[1:]:
        all_issues.extend(check_file(filepath))

    for filepath, line, message in all_issues:
        print("{0}:{1}: {2}".format(filepath, line, message))

    return 1 if all_issues else 0


if __name__ == "__main__":
    sys.exit(main())
