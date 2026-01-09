---
title: Safe Regex Patterns
description: Guidelines for writing ReDoS-safe regular expressions. Best practices and examples of secure patterns.
---

# Safe Patterns

This guide provides best practices for writing regex patterns that are safe from ReDoS attacks.

## Golden Rules

!!! success "Safe Regex Guidelines"

    1. **Avoid nested quantifiers** - Never nest `+`, `*`, or `{n,m}` inside each other
    2. **Avoid overlapping alternatives** - Each alternative should match distinct input
    3. **Use specific character classes** - Prefer `[a-z]` over `.`
    4. **Bound your quantifiers** - Use `{1,100}` instead of `+`
    5. **Test with ReDoctor** - Always validate before deployment

## Safe Pattern Examples

### Simple Character Classes

Linear time complexity - each character matched once:

```python
# ✅ Safe patterns
r"^[a-zA-Z]+$"          # Letters only
r"^[0-9]+$"             # Digits only
r"^[a-zA-Z0-9_]+$"      # Alphanumeric with underscore
r"^[\w]+$"              # Word characters
```

### Bounded Quantifiers

Limit repetition to prevent excessive backtracking:

```python
# ✅ Safe patterns
r"^\d{1,10}$"           # 1-10 digits
r"^[a-z]{2,50}$"        # 2-50 lowercase letters
r"^.{1,1000}$"          # Limited length
```

### Specific Patterns

Well-defined patterns without ambiguity:

```python
# ✅ Safe patterns
r"^\d{4}-\d{2}-\d{2}$"  # Date: YYYY-MM-DD
r"^\d{3}-\d{3}-\d{4}$"  # Phone: XXX-XXX-XXXX
r"^[A-Z]{2}\d{6}$"      # ID: XX000000
```

### Non-overlapping Alternatives

Each alternative matches distinct input:

```python
# ✅ Safe patterns
r"^(cat|dog|bird)$"     # Distinct words
r"^(yes|no|maybe)$"     # No overlap
r"^(\d+|[a-z]+)$"       # Numbers OR letters (not mixed)
```

### Anchored Patterns

Start and end anchors reduce backtracking:

```python
# ✅ Safe patterns
r"^exact$"              # Exact match
r"^prefix.*"            # Anchored start
r".*suffix$"            # Anchored end (careful with .*)
```

## Pattern Transformations

### From Dangerous to Safe

| Vulnerable | Safe | Change |
|:-----------|:-----|:-------|
| `(a+)+` | `a+` | Remove nesting |
| `(a\|a)*` | `a*` | Remove overlap |
| `.*a.*` | `[^a]*a.*` | Use negated class |
| `(a+)+b` | `a+b` | Flatten |
| `(\d+\.)+` | `(\d+\.)*\d+` | Be explicit |

### Email Validation

```python
# ❌ Dangerous
r"^([a-zA-Z0-9]+)*@"

# ✅ Safe
r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

# ✅ Better: Use a library
import email.utils
email.utils.parseaddr(email_string)
```

### URL Validation

```python
# ❌ Dangerous - multiple .*
r"^https?://.*\..*\..*$"

# ✅ Safe - specific structure
r"^https?://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+(/.*)?$"

# ✅ Better: Use urllib
from urllib.parse import urlparse
result = urlparse(url)
```

### Number Validation

```python
# ❌ Potentially dangerous with edge cases
r"^-?\d*\.?\d*$"

# ✅ Safe and clear
r"^-?\d+(\.\d+)?$"

# ✅ Better: Use Python
try:
    float(value)
except ValueError:
    pass
```

## Validation Checklist

Before using any regex in production:

```python
from redoctor import check, is_safe

def validate_regex(pattern: str) -> bool:
    """Validate a regex pattern is safe to use."""
    result = check(pattern)

    if result.is_vulnerable:
        print(f"❌ Vulnerable: {pattern}")
        print(f"   Complexity: {result.complexity}")
        return False

    if result.status.value == "unknown":
        print(f"⚠️ Unknown: {pattern}")
        print(f"   Consider manual review")
        return True  # Proceed with caution

    print(f"✅ Safe: {pattern}")
    return True

# Use it
patterns = [
    r"^[a-z]+$",
    r"^(a+)+$",
    r"^\d{1,10}$",
]

for p in patterns:
    validate_regex(p)
```

## Safe Pattern Templates

### Identifier (username, variable name)

```python
# Username: 3-20 alphanumeric characters
r"^[a-zA-Z][a-zA-Z0-9_]{2,19}$"
```

### UUID

```python
# UUID v4 format
r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
```

### ISO Date

```python
# YYYY-MM-DD
r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
```

### IP Address (v4)

```python
# IPv4 (simplified, use ipaddress module for production)
r"^(\d{1,3}\.){3}\d{1,3}$"
```

### Hex Color

```python
# #RGB or #RRGGBB
r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"
```

### Semantic Version

```python
# semver: MAJOR.MINOR.PATCH
r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
```

## When to Avoid Regex

Sometimes regex isn't the right tool:

### Parsing HTML/XML

```python
# ❌ Don't do this
html_pattern = r"<(\w+)[^>]*>.*?</\1>"

# ✅ Use a parser
from html.parser import HTMLParser
from bs4 import BeautifulSoup
```

### Complex Validation

```python
# ❌ Complex regex for email
# ✅ Use email-validator library
from email_validator import validate_email
```

### JSON/YAML/TOML

```python
# ❌ Parsing structured data with regex
# ✅ Use proper parsers
import json
import yaml
import tomllib
```

### Mathematical Expressions

```python
# ❌ Regex for math
# ✅ Use ast or a proper parser
import ast
ast.literal_eval(expression)
```

## Testing Your Patterns

Always test with edge cases:

```python
from redoctor import check

def test_pattern(pattern: str, test_cases: list):
    """Test a pattern for safety and correctness."""
    import re

    # Check safety
    result = check(pattern)
    print(f"Pattern: {pattern}")
    print(f"Safety: {'✅ Safe' if result.is_safe else '❌ Vulnerable'}")

    # Test functionality
    regex = re.compile(pattern)
    for test_input, should_match in test_cases:
        matches = bool(regex.match(test_input))
        status = "✓" if matches == should_match else "✗"
        print(f"  {status} {test_input!r}: {matches}")

# Example
test_pattern(r"^[a-z]{3,10}$", [
    ("hello", True),
    ("Hi", False),      # Capital letter
    ("ab", False),      # Too short
    ("", False),        # Empty
    ("verylongword", False),  # Too long
])
```

## Next Steps

- [Vulnerable Patterns →](vulnerable-patterns.md)
- [Understanding ReDoS →](redos-explained.md)
- [Configuration Guide →](configuration.md)
