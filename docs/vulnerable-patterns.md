---
title: Vulnerable Pattern Examples
description: Common ReDoS-vulnerable regex patterns and how to fix them. Learn to recognize and avoid dangerous patterns.
---

# Vulnerable Patterns

This guide shows common vulnerable regex patterns, explains why they're dangerous, and provides safe alternatives.

## Pattern Categories

### 1. Nested Quantifiers

The most common source of exponential complexity.

!!! danger "Vulnerable"
    ```python
    r"^(a+)+$"      # Exponential O(2^n)
    r"^(a*)*$"      # Exponential O(2^n)
    r"^(a+)*$"      # Exponential O(2^n)
    r"^([a-z]+)+$"  # Exponential O(2^n)
    ```

!!! success "Safe Alternative"
    ```python
    r"^a+$"         # Linear O(n)
    r"^[a-z]+$"     # Linear O(n)
    ```

**Why it's dangerous:** The inner quantifier creates ambiguity about how to distribute characters among repetitions.

```python
from redoctor import check

result = check(r"^(a+)+$")
print(result.complexity)  # O(2^n)
print(result.attack)      # 'aaaaaaaaaaaaaaaaaaa!'
```

---

### 2. Overlapping Alternatives

Alternatives that can match the same input.

!!! danger "Vulnerable"
    ```python
    r"(a|a)+$"      # Same character
    r"(a|ab)+$"     # Overlapping
    r"(.*|a)+$"     # Wildcard overlap
    r"(\w+|\d+)+$"  # \d is subset of \w
    ```

!!! success "Safe Alternative"
    ```python
    r"a+$"          # Remove redundancy
    r"(ab?)+$"      # Combine alternatives
    ```

**Why it's dangerous:** Multiple paths can match the same input, causing backtracking.

---

### 3. Greedy Wildcards

Multiple `.+` or `.*` patterns.

!!! danger "Vulnerable"
    ```python
    r".*a.*a.*"     # O(n²)
    r".*a.*a.*a.*"  # O(n³)
    r".+x.+x.+$"    # O(n³)
    ```

!!! success "Safe Alternative"
    ```python
    r"[^a]*a[^a]*a.*"  # Use negated class
    r".*?a.*?a.*"      # Lazy quantifiers (still risky)
    ```

**Why it's dangerous:** Each `.*` can consume varying amounts, creating combinatorial explosion.

---

### 4. Email Patterns

Email validation is a common source of ReDoS.

!!! danger "Vulnerable"
    ```python
    r"^([a-zA-Z0-9]+)*@"
    r"^[\w.]+@[\w.]+$"
    r"^([a-zA-Z0-9_.+-]+)+@"
    ```

!!! success "Safe Alternative"
    ```python
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    # Or use a proper email validation library
    ```

---

### 5. URL Patterns

URL parsing with regex is tricky.

!!! danger "Vulnerable"
    ```python
    r"^(https?://)?([a-z0-9]+\.)+[a-z]{2,}/?$"
    r".*\.(com|org|net).*"
    ```

!!! success "Safe Alternative"
    ```python
    # Use urllib.parse instead
    from urllib.parse import urlparse
    parsed = urlparse(url)
    ```

---

### 6. HTML/XML Patterns

Don't parse HTML with regex!

!!! danger "Vulnerable"
    ```python
    r"<(.+)>.*</\1>"
    r"<[^>]+>[^<]*</[^>]+>"
    ```

!!! success "Safe Alternative"
    ```python
    # Use a proper HTML parser
    from html.parser import HTMLParser
    # Or use BeautifulSoup, lxml, etc.
    ```

---

### 7. Whitespace Handling

Trimming and normalizing whitespace.

!!! danger "Vulnerable"
    ```python
    r"^\s*(.+?)\s*$"
    r"(\s+)+"
    ```

!!! success "Safe Alternative"
    ```python
    # Use string methods
    text.strip()
    " ".join(text.split())
    ```

---

## Complexity Reference

| Pattern | Complexity | Risk |
|:--------|:-----------|:-----|
| `^(a+)+$` | O(2^n) | 🚨 Critical |
| `(a\|a)+` | O(2^n) | 🚨 Critical |
| `.*a.*a.*` | O(n²) | ⚠️ High |
| `(a+)+b` | O(2^n) | 🚨 Critical |
| `^[a-z]+$` | O(n) | ✅ Safe |
| `^\d{1,10}$` | O(n) | ✅ Safe |

## Test with ReDoctor

```python
from redoctor import check

patterns = [
    r"^(a+)+$",
    r"(a|a)*$",
    r".*a.*a.*",
    r"^[a-z]+$",
]

for pattern in patterns:
    result = check(pattern)
    status = "🚨 VULN" if result.is_vulnerable else "✅ SAFE"
    complexity = result.complexity.summary if result.complexity else "N/A"
    print(f"{status} {complexity:8} {pattern}")
```

Output:
```
🚨 VULN O(2^n)   ^(a+)+$
🚨 VULN O(2^n)   (a|a)*$
🚨 VULN O(n^2)   .*a.*a.*
✅ SAFE O(n)     ^[a-z]+$
```

## Quick Reference Card

### Avoid These Patterns

| Pattern | Problem |
|:--------|:--------|
| `(x+)+` | Nested quantifiers |
| `(x\|x)+` | Overlapping alternatives |
| `.*x.*x.*` | Multiple wildcards |
| `(x*)*` | Star within star |
| `(x+x+)+` | Overlapping within group |

### Safe Alternatives

| Instead of | Use |
|:-----------|:----|
| `(a+)+` | `a+` |
| `(a\|ab)+` | `(ab?)+` |
| `.*a.*` | `[^a]*a.*` |
| `(\w+\s+)+` | `(\w+\s)+` or validate differently |

## Next Steps

- [Safe Patterns →](safe-patterns.md)
- [Understanding ReDoS →](redos-explained.md)
- [How ReDoctor Works →](how-it-works.md)
