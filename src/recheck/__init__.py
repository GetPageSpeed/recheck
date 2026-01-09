"""
recheck - A Python ReDoS (Regular Expression Denial of Service) vulnerability checker.

This library detects potential ReDoS vulnerabilities in regular expressions using
a hybrid approach combining static automata-based analysis with fuzzing.

Example usage:
    >>> from recheck import check
    >>> result = check(r"^(a+)+$")
    >>> if result.is_vulnerable:
    ...     print(f"Vulnerable! Attack: {result.attack}")

For more control:
    >>> from recheck import check, Config
    >>> result = check(r"^(a+)+$", config=Config(timeout=5.0))
"""

from recheck.checker import check, check_pattern, is_safe, is_vulnerable, HybridChecker
from recheck.config import Config, CheckerType, AccelerationMode, SeederType
from recheck.diagnostics.complexity import Complexity, ComplexityType
from recheck.diagnostics.diagnostics import Diagnostics, Status
from recheck.diagnostics.attack_pattern import AttackPattern
from recheck.diagnostics.hotspot import Hotspot
from recheck.parser.flags import Flags
from recheck.exceptions import RecheckError, ParseError, TimeoutError

__version__ = "0.1.0"

__all__ = [
    # Main API
    "check",
    "check_pattern",
    "is_safe",
    "is_vulnerable",
    "HybridChecker",
    # Configuration
    "Config",
    "CheckerType",
    "AccelerationMode",
    "SeederType",
    "Flags",
    # Diagnostics
    "Diagnostics",
    "Status",
    "Complexity",
    "ComplexityType",
    "AttackPattern",
    "Hotspot",
    # Exceptions
    "RecheckError",
    "ParseError",
    "TimeoutError",
    # Version
    "__version__",
]
