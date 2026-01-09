---
title: Complexity Types Reference
description: Understanding time complexity classifications in ReDoctor. Learn about O(n), O(n²), and O(2^n) complexity.
---

# Complexity Types

ReDoctor classifies regex vulnerabilities by their algorithmic time complexity. This helps you understand the severity and potential impact of each vulnerability.

## Overview

| Complexity | Type | Risk | Description |
|:-----------|:-----|:-----|:------------|
| `O(n)` | Linear | ✅ Safe | Processing time grows linearly with input |
| `O(n²)` | Quadratic | ⚠️ Moderate | Processing time grows quadratically |
| `O(n³)` | Cubic | ⚠️ High | Processing time grows cubically |
| `O(2^n)` | Exponential | 🚨 Critical | Processing time doubles with each character |

## Linear - O(n)

**Status:** ✅ Safe

Processing time grows linearly with input length. Each additional character adds a constant amount of work.

### Characteristics

- Time scales proportionally with input
- No backtracking or minimal backtracking
- Safe for all input sizes

### Examples

```python
from redoctor import check

# Linear patterns
check(r"^[a-z]+$")        # O(n) - Simple class
check(r"^\d{1,10}$")      # O(n) - Bounded quantifier
check(r"^hello$")         # O(n) - Literal match
check(r"^[A-Z][a-z]*$")   # O(n) - No nesting
```

### Impact

| Input Length | Time (relative) |
|:-------------|:----------------|
| 10 | 10 |
| 100 | 100 |
| 1,000 | 1,000 |
| 10,000 | 10,000 |

## Polynomial - O(n^k)

**Status:** ⚠️ Moderate to High Risk

Processing time grows as a polynomial function of input length.

### Quadratic O(n²)

Time grows as the square of input length.

```python
# Quadratic patterns
check(r".*a.*a.*")         # O(n²)
check(r"^(\w*\s*)*$")      # O(n²) with certain inputs
```

### Cubic O(n³)

Time grows as the cube of input length.

```python
# Cubic patterns
check(r".*a.*a.*a.*")      # O(n³)
```

### Impact Comparison

| Input Length | O(n) | O(n²) | O(n³) |
|:-------------|:-----|:------|:------|
| 10 | 10 | 100 | 1,000 |
| 100 | 100 | 10,000 | 1,000,000 |
| 1,000 | 1,000 | 1,000,000 | 1,000,000,000 |

### Real-World Impact

A polynomial O(n²) pattern:

- With 100 chars: ~10,000 operations ✓ Acceptable
- With 1,000 chars: ~1,000,000 operations ⚠️ Slow
- With 10,000 chars: ~100,000,000 operations 🚨 Very slow

## Exponential - O(2^n)

**Status:** 🚨 Critical

Processing time doubles with each additional character. This is the most severe type of ReDoS vulnerability.

### Characteristics

- Each character potentially doubles processing time
- Can hang applications with as few as 25-30 characters
- Often caused by nested quantifiers or overlapping alternatives

### Examples

```python
# Exponential patterns
check(r"^(a+)+$")          # O(2^n) - Nested quantifiers
check(r"(a|a)*$")          # O(2^n) - Overlapping alternatives
check(r"([a-z]+)+$")       # O(2^n) - Nested + on class
```

### Impact

| Input Length | Operations |
|:-------------|:-----------|
| 10 | 1,024 |
| 20 | 1,048,576 |
| 25 | 33,554,432 |
| 30 | 1,073,741,824 |
| 40 | 1,099,511,627,776 |

### Real-World Impact

With exponential complexity:

- 20 characters: milliseconds
- 25 characters: seconds
- 30 characters: minutes
- 35 characters: hours
- 40 characters: years!

## Using Complexity in Code

```python
from redoctor import check
from redoctor.diagnostics.complexity import ComplexityType

result = check(r"^(a+)+$")
complexity = result.complexity

# Check complexity type
if complexity.type == ComplexityType.EXPONENTIAL:
    print("🚨 Critical: This pattern has exponential complexity!")
elif complexity.type == ComplexityType.POLYNOMIAL:
    print(f"⚠️ Warning: O(n^{complexity.degree}) complexity")
else:
    print("✅ Safe: Linear complexity")

# Compare complexities
print(complexity.is_safe)         # False
print(complexity.is_vulnerable)   # True
print(complexity.is_exponential)  # True
print(complexity.is_polynomial)   # False

# Get summary
print(complexity.summary)  # "O(2^n)"
print(str(complexity))     # "O(2^n)"
```

## Severity Matrix

| Complexity | Small Input (<100) | Medium (100-1K) | Large (>1K) |
|:-----------|:-------------------|:----------------|:------------|
| O(n) | ✅ Fast | ✅ Fast | ✅ Fast |
| O(n²) | ✅ Fast | ⚠️ Noticeable | 🚨 Slow |
| O(n³) | ✅ Fast | 🚨 Slow | ☠️ Very slow |
| O(2^n) | ⚠️ 20+ chars | ☠️ Hang | ☠️ Hang |

## Response Guidelines

### O(n) - Safe

```python
# ✅ OK to use
pattern = r"^[a-z]+$"
```

### O(n²) - Moderate Risk

```python
# ⚠️ Consider if:
# - Input is user-controlled
# - Input can be large
# Otherwise may be acceptable for small, controlled inputs
```

### O(n³) - High Risk

```python
# 🚨 Avoid unless:
# - Input is strictly bounded (< 100 chars)
# - Input is not user-controlled
```

### O(2^n) - Critical

```python
# ☠️ NEVER use in production
# - Rewrite the pattern
# - Use a different approach
# - No exceptions
```

## Next Steps

- [Vulnerable Patterns →](vulnerable-patterns.md)
- [Safe Patterns →](safe-patterns.md)
- [Understanding ReDoS →](redos-explained.md)
