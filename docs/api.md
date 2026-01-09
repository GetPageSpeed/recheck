---
title: Python API Guide
description: Complete guide to using ReDoctor's Python API for ReDoS vulnerability detection in your applications.
---

# Python API Guide

ReDoctor provides a clean, intuitive Python API for integrating ReDoS detection into your applications.

## Quick Start

```python
from redoctor import check

result = check(r"^(a+)+$")

if result.is_vulnerable:
    print(f"Vulnerable! {result.complexity}")
    print(f"Attack: {result.attack}")
```

## Main API

### `check(pattern, flags=None, config=None)`

The primary function for checking regex patterns.

```python
from redoctor import check, Config
from redoctor.parser.flags import Flags

# Basic usage
result = check(r"^(a+)+$")

# With flags
flags = Flags(ignore_case=True)
result = check(r"[A-Z]+", flags=flags)

# With configuration
config = Config(timeout=30.0)
result = check(r"pattern", config=config)

# All together
result = check(r"pattern", flags=flags, config=config)
```

**Parameters:**

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `pattern` | `str` | The regex pattern to check |
| `flags` | `Flags` | Optional regex flags |
| `config` | `Config` | Optional configuration |

**Returns:** `Diagnostics` object

---

### `is_vulnerable(pattern, flags=None, config=None)`

Quick check if a pattern is vulnerable.

```python
from redoctor import is_vulnerable

if is_vulnerable(r"^(a+)+$"):
    print("Don't use this pattern!")
```

**Returns:** `bool`

---

### `is_safe(pattern, flags=None, config=None)`

Quick check if a pattern is safe.

```python
from redoctor import is_safe

if is_safe(r"^[a-z]+$"):
    print("This pattern is safe")
```

**Returns:** `bool`

---

### `check_pattern(pattern, config=None)`

Check a pre-parsed pattern object.

```python
from redoctor import check_pattern
from redoctor.parser.parser import parse

# Parse first
parsed = parse(r"^(a+)+$")

# Then check
result = check_pattern(parsed)
```

**Returns:** `Diagnostics` object

## Diagnostics Object

The `Diagnostics` object contains all analysis results.

### Properties

```python
from redoctor import check

result = check(r"^(a+)+$")

# Status (enum: SAFE, VULNERABLE, UNKNOWN, ERROR)
result.status          # Status.VULNERABLE

# Boolean helpers
result.is_vulnerable   # True
result.is_safe         # False

# The original pattern
result.source          # "^(a+)+$"

# Complexity analysis
result.complexity      # Complexity(exponential)
result.complexity.type # ComplexityType.EXPONENTIAL
result.complexity.summary  # "O(2^n)"

# Attack string (if vulnerable)
result.attack          # "aaaaaaaaaaaaaaaaaaaaaaaa!"

# Detailed attack pattern (if vulnerable)
result.attack_pattern  # AttackPattern object

# Hotspot (vulnerable portion)
result.hotspot         # Hotspot object

# Which checker was used
result.checker         # "automaton" or "fuzz"

# Human-readable message
result.message         # "ReDoS vulnerability detected with O(2^n) complexity."

# Error message (if status is ERROR)
result.error           # None or error string
```

### Methods

```python
# String representation
print(result)
# Pattern: ^(a+)+$
# Status: vulnerable
# Complexity: O(2^n)
# Attack: ...

# Convert to dictionary (for JSON serialization)
data = result.to_dict()
```

## AttackPattern Object

Represents the structure of an attack string.

```python
from redoctor import check

result = check(r"^(a+)+$")
attack = result.attack_pattern

# Components
attack.prefix   # "a" - String before the pump
attack.pump     # "aaaaaaaaaaaa" - Repeated portion
attack.suffix   # "!" - String after pump (causes backtracking)

# Build attack strings
short = attack.build(10)   # 10 pump repetitions
long = attack.build(100)   # 100 pump repetitions
default = attack.attack    # Default attack string

# Create variations
new_attack = attack.with_repeat(50)  # New pattern with 50 reps
```

## Complexity Object

Represents the time complexity of the pattern.

```python
from redoctor import check
from redoctor.diagnostics.complexity import ComplexityType

result = check(r"^(a+)+$")
complexity = result.complexity

# Type (enum)
complexity.type         # ComplexityType.EXPONENTIAL

# Properties
complexity.is_safe          # False
complexity.is_vulnerable    # True
complexity.is_polynomial    # False
complexity.is_exponential   # True

# For polynomial complexity
complexity.degree       # None for exponential, integer for polynomial

# Human-readable
complexity.summary      # "O(2^n)"
str(complexity)         # "O(2^n)"
```

### Complexity Types

```python
from redoctor.diagnostics.complexity import Complexity, ComplexityType

# Safe (linear)
safe = Complexity.safe()  # O(n)

# Polynomial
poly2 = Complexity.polynomial(2)  # O(n²)
poly3 = Complexity.polynomial(3)  # O(n³)

# Exponential
exp = Complexity.exponential()  # O(2^n)
```

## Configuration

### Config Object

```python
from redoctor import Config

# Preset configurations
config = Config.default()    # Standard settings
config = Config.quick()      # Fast analysis
config = Config.thorough()   # Deep analysis

# Custom configuration
config = Config(
    # Checker selection
    checker=CheckerType.AUTO,  # AUTO, AUTOMATON, or FUZZ

    # Timeouts
    timeout=10.0,              # Analysis timeout (seconds)
    recall_timeout=1.0,        # Validation timeout

    # Attack generation
    max_attack_length=4096,    # Maximum attack string length
    attack_limit=10,           # Number of attack strings

    # Fuzzing
    max_iterations=100000,     # Maximum fuzz iterations
    random_seed=None,          # For reproducibility

    # Limits
    max_nfa_size=35000,        # Max NFA states
    max_pattern_size=1500,     # Max pattern length

    # Validation
    recall_limit=10,           # Max recall validations
    skip_recall=False,         # Skip validation step
)
```

### Preset Comparison

| Setting | `default()` | `quick()` | `thorough()` |
|:--------|:------------|:----------|:-------------|
| `timeout` | 10s | 1s | 30s |
| `max_attack_length` | 4096 | 256 | 8192 |
| `max_iterations` | 100K | 10K | 500K |
| `recall_timeout` | 1s | 0.1s | 5s |
| `skip_recall` | False | True | False |

## Flags

```python
from redoctor.parser.flags import Flags

# Create flags
flags = Flags(
    ignore_case=True,   # re.IGNORECASE
    multiline=True,     # re.MULTILINE
    dotall=False,       # re.DOTALL
    unicode=True,       # re.UNICODE (default True)
    global_match=False, # Global matching mode
)

# Use with check
from redoctor import check
result = check(r"[A-Z]+", flags=flags)
```

## HybridChecker Class

For more control over the checking process:

```python
from redoctor import HybridChecker, Config

# Create checker with configuration
checker = HybridChecker(Config.default())

# Check multiple patterns efficiently
patterns = [r"^(a+)+$", r"^[a-z]+$", r"(x+x+)+y"]

for pattern in patterns:
    result = checker.check(pattern)
    print(f"{pattern}: {result.status.value}")
```

## Error Handling

```python
from redoctor import check, RedoctorError, ParseError, TimeoutError

try:
    result = check(r"^(a+)+$")
except ParseError as e:
    print(f"Invalid regex: {e}")
except TimeoutError as e:
    print(f"Analysis timed out: {e}")
except RedoctorError as e:
    print(f"ReDoctor error: {e}")

# Or check the result status
result = check(r"[invalid")
if result.status.value == "error":
    print(f"Error: {result.error}")
```

## Complete Example

```python
#!/usr/bin/env python3
"""Example: Check user-submitted regex patterns."""

from redoctor import check, Config, is_vulnerable
from redoctor.diagnostics import Status
import json

def validate_regex(pattern: str) -> dict:
    """Validate a regex pattern for ReDoS vulnerabilities.

    Returns a dictionary with validation results.
    """
    config = Config(timeout=5.0, skip_recall=True)
    result = check(pattern, config=config)

    response = {
        "pattern": pattern,
        "safe": result.is_safe,
        "status": result.status.value,
        "message": result.message,
    }

    if result.is_vulnerable:
        response["complexity"] = result.complexity.summary
        response["attack_example"] = result.attack_pattern.build(10) if result.attack_pattern else None
        response["recommendation"] = "Do not use this pattern. Consider rewriting it."

    return response


# Example usage
if __name__ == "__main__":
    patterns = [
        r"^[a-z0-9]+$",      # Safe
        r"^(a+)+$",          # Vulnerable (exponential)
        r".*a.*a.*",         # Vulnerable (polynomial)
        r"^\d{1,10}$",       # Safe
    ]

    print("Regex Pattern Validation Results")
    print("=" * 50)

    for pattern in patterns:
        result = validate_regex(pattern)

        icon = "✓" if result["safe"] else "✗"
        print(f"\n{icon} Pattern: {pattern}")
        print(f"  Status: {result['status']}")

        if not result["safe"]:
            print(f"  Complexity: {result.get('complexity', 'N/A')}")
            if result.get("attack_example"):
                print(f"  Attack: {result['attack_example'][:50]}...")

    print("\n" + "=" * 50)
    print("Validation complete!")
```

## Next Steps

- [Configuration Guide →](configuration.md)
- [Source Code Scanning →](source-scanning.md)
- [Vulnerable Patterns →](vulnerable-patterns.md)
