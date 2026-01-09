---
title: Understanding ReDoS Attacks
description: Learn how Regular Expression Denial of Service (ReDoS) attacks work and why they're dangerous to your applications.
---

# Understanding ReDoS

Regular Expression Denial of Service (ReDoS) is a type of algorithmic complexity attack that exploits the worst-case behavior of regex engines. This guide explains how ReDoS works and why it's a serious security concern.

## What is ReDoS?

Most regex engines use **backtracking** to match patterns. While this approach is flexible, it can lead to **exponential or polynomial time complexity** for certain patterns and inputs.

!!! danger "The Impact"
    A single malicious input to a vulnerable regex can:

    - Hang your application for **minutes or hours**
    - Consume 100% CPU
    - Block other requests
    - Cause complete service denial

## How Backtracking Works

Consider the regex `^(a+)+$` matching against `"aaaaX"`:

1. Engine tries to match `a+` as many times as possible
2. Outer `+` tries to repeat the group
3. When `X` is reached, no match
4. Engine **backtracks** to try different combinations

For `n` characters, the engine may try **2^n** combinations!

```
Input: "aaaaX" (4 a's + X)

Attempt 1: (aaaa) - fails at X
Attempt 2: (aaa)(a) - fails at X
Attempt 3: (aa)(aa) - fails at X
Attempt 4: (aa)(a)(a) - fails at X
Attempt 5: (a)(aaa) - fails at X
... and so on for 2^4 = 16 combinations
```

With 30 characters, that's **over 1 billion** combinations!

## Time Complexity Classes

### Linear O(n) - Safe ✅

Each character is processed once:

```python
# Safe patterns
r"^[a-z]+$"       # Simple character class
r"^\d{1,10}$"     # Bounded quantifier
r"^[A-Z][a-z]*$"  # No nested quantifiers
```

### Polynomial O(n²) or O(n³) - Dangerous ⚠️

Processing time grows polynomially with input length:

```python
# Polynomial patterns
r".*a.*a.*"       # O(n²) - Multiple .*
r".*a.*a.*a.*"    # O(n³) - Even more .*
```

### Exponential O(2^n) - Critical 🚨

Processing time doubles with each additional character:

```python
# Exponential patterns
r"^(a+)+$"        # Nested quantifiers
r"(a|a)*$"        # Overlapping alternatives
r"([a-z]+)+$"     # Nested + quantifiers
```

## Real-World Examples

### CVE-2016-1000232 - Swagger UI

Pattern: `^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

While this specific pattern isn't vulnerable, similar email/domain validators often are:

```python
# Vulnerable email pattern (simplified)
r"^([a-zA-Z0-9]+)*@"

# Attack: "a" * 50 + "!"
```

### Node.js Regular Expression Bug

The `ms` package had a vulnerable pattern that could hang with crafted input:

```python
# Simplified vulnerable pattern
r"^(\d+)?\s*(.*?)$"
```

### Stack Overflow Outage (2016)

A regex in the post formatting caused a 34-minute outage:

```python
# Simplified vulnerable pattern
r"^[\s\u200c]+|[\s\u200c]+$"
```

## Attack Anatomy

A ReDoS attack string typically has three parts:

```
Prefix + Pump × n + Suffix
```

| Component | Purpose |
|:----------|:--------|
| **Prefix** | Sets up the vulnerable state |
| **Pump** | Repeated to increase backtracking |
| **Suffix** | Forces the backtrack (usually fails to match) |

### Example

Pattern: `^(a+)+$`

| Component | Value | Purpose |
|:----------|:------|:--------|
| Prefix | `""` or `"a"` | Initial match |
| Pump | `"a"` | Repeated many times |
| Suffix | `"!"` | Causes match failure |

Attack string: `"a" × 30 + "!"` = `"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!"`

## Detection Methods

### Static Analysis (Automaton-based)

Builds a finite automaton from the regex and detects **ambiguity**:

```
NFA → Check for ambiguous states → Vulnerability detected
```

**Pros:** Fast, deterministic
**Cons:** Can't handle backreferences

### Dynamic Analysis (Fuzzing)

Executes patterns with crafted inputs and measures step count:

```
Pattern → VM → Count steps → Detect growth pattern
```

**Pros:** Handles all regex features
**Cons:** Slower, may miss edge cases

### ReDoctor's Hybrid Approach

ReDoctor combines both methods:

1. **Automaton checker** for patterns without backreferences
2. **Fuzz checker** for complex patterns
3. **Recall validation** to confirm findings

## Mitigation Strategies

### 1. Use Safe Patterns

Avoid nested quantifiers and overlapping alternatives:

```python
# Instead of this (vulnerable)
r"^(a+)+$"

# Use this (safe)
r"^a+$"
```

### 2. Use Atomic Groups

If your regex engine supports them:

```python
# Atomic group prevents backtracking
r"^(?>a+)+$"  # Not in Python's re module
```

### 3. Use Possessive Quantifiers

```python
# Possessive quantifier (not in Python re)
r"^a++$"
```

### 4. Set Timeouts

Python 3.11+ supports regex timeouts:

```python
import re

try:
    re.match(pattern, string, timeout=1.0)
except re.error:
    print("Match timed out")
```

### 5. Use ReDoctor!

Check patterns before deployment:

```python
from redoctor import check

result = check(pattern)
if result.is_vulnerable:
    raise ValueError(f"Vulnerable pattern: {result.complexity}")
```

## Prevention Checklist

!!! check "Before Using a Regex"

    - [ ] Run through ReDoctor
    - [ ] Avoid nested quantifiers (`(a+)+`)
    - [ ] Avoid overlapping alternatives (`(a|a)`)
    - [ ] Prefer specific character classes over `.`
    - [ ] Use bounded quantifiers when possible (`{1,10}` vs `+`)
    - [ ] Test with edge cases
    - [ ] Set timeouts for user-supplied patterns

## Further Reading

- [OWASP ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)
- [Cloudflare ReDoS Incident](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/)
- [ReDoS Explained (Wikipedia)](https://en.wikipedia.org/wiki/ReDoS)

## Next Steps

- [Vulnerable Patterns →](vulnerable-patterns.md)
- [Safe Patterns →](safe-patterns.md)
- [How ReDoctor Works →](how-it-works.md)
