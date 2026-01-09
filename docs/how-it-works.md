---
title: How ReDoctor Works
description: Technical deep-dive into ReDoctor's hybrid analysis engine. Learn about automata-based detection and fuzzing.
---

# How ReDoctor Works

ReDoctor uses a **hybrid analysis approach** combining static automata-based analysis with intelligent fuzzing for comprehensive ReDoS detection.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ReDoctor Engine                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Input: Regex Pattern                                                │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                │
│  │     Parser      │  → AST (Abstract Syntax Tree)                  │
│  └────────┬────────┘                                                │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                │
│  │  Auto Selector  │  → Choose checker based on pattern features    │
│  └────────┬────────┘                                                │
│           │                                                          │
│     ┌─────┴─────┐                                                   │
│     ▼           ▼                                                   │
│  ┌──────────┐  ┌──────────┐                                        │
│  │ Automaton│  │   Fuzz   │                                        │
│  │ Checker  │  │  Checker │                                        │
│  └────┬─────┘  └────┬─────┘                                        │
│       │             │                                               │
│       └──────┬──────┘                                               │
│              ▼                                                      │
│  ┌─────────────────┐                                                │
│  │    Recall       │  → Validate with real execution                │
│  │   Validator     │                                                │
│  └────────┬────────┘                                                │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                │
│  │   Diagnostics   │  → Status, Complexity, Attack String           │
│  └─────────────────┘                                                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Parser

The parser converts regex patterns into an Abstract Syntax Tree (AST):

```python
from redoctor.parser.parser import parse

# Parse a pattern
pattern = parse(r"^(a+)+$")

# AST structure
# Pattern(
#     source="^(a+)+$",
#     node=Concat([
#         Anchor(START),
#         Repeat(Group(Repeat(Char('a'), 1, INF)), 1, INF),
#         Anchor(END),
#     ])
# )
```

**Supported features:**

- Character classes `[a-z]`
- Quantifiers `+`, `*`, `?`, `{n,m}`
- Groups `(...)`, `(?:...)`
- Anchors `^`, `$`, `\b`
- Alternation `a|b`
- Escape sequences `\d`, `\w`, `\s`
- Unicode categories `\p{L}`
- Backreferences `\1`
- Lookahead `(?=...)`, `(?!...)`
- Lookbehind `(?<=...)`, `(?<!...)`

### 2. Automaton Checker

Uses automata theory to detect vulnerabilities through static analysis.

#### ε-NFA Construction

Builds an ε-NFA (Non-deterministic Finite Automaton with epsilon transitions):

```
Pattern: (a|ab)+

ε-NFA:
    ┌───ε───┐
    │       ▼
→ (0) ─a─→ (1) ─ε─→ (4) ─ε─→ (5)
    │               ▲
    └─a─→ (2) ─b─→ (3) ─ε─┘
              │
              └────ε────┘
```

#### NFAwLA (NFA with Look-Ahead)

A key innovation from the [recheck](https://github.com/makenowjust-labo/recheck) project is the **NFAwLA** - an NFA augmented with look-ahead information to eliminate false positives.

```
┌─────────────────────────────────────────────────────────┐
│                    NFAwLA Construction                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Build OrderedNFA from ε-NFA                         │
│                                                          │
│  2. Reverse the NFA and convert to DFA                  │
│     (This DFA tells us what can follow each state)      │
│                                                          │
│  3. Product: NFA × Reversed-DFA                         │
│     States become pairs: (nfa_state, lookahead_state)   │
│                                                          │
│  4. Prune unreachable transitions                       │
│     (Transitions that can never lead to acceptance)     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

The look-ahead DFA eliminates "dead-end" ambiguity that would cause false positives.

#### SCC-Based Ambiguity Detection

Uses **Strongly Connected Components** to detect vulnerability patterns:

```python
# Ambiguity types detected:
#
# 1. EDA (Exponential Degree of Ambiguity)
#    - Multiple transitions on same character within an SCC
#    - Results in O(2^n) complexity
#
# 2. IDA (Polynomial Degree of Ambiguity)
#    - SCC chains with shared characters
#    - Results in O(n^k) complexity
```

The SCC checker uses Tarjan's algorithm to find cycles, then analyzes transitions within each SCC for ambiguity.

#### Exploitability Check

Not all ambiguous patterns are exploitable. The `_is_multi_trans_exploitable` check considers:

1. **Pattern anchoring**: Does the pattern have `$` or `\Z`?
2. **Continuation requirement**: Must something match after the ambiguous part?
3. **Match mode**: How will the regex be used (full vs partial match)?

```python
# Pattern: (a*)*
# - Without $ anchor: can match early → SAFE
# - With $ anchor: must match to end → EXPONENTIAL

# Pattern: ([^@]+)+@
# - The @ forces continuation → EXPONENTIAL
# - Even without $ anchor, backtracking is required
```

#### Witness Generation

When ambiguity is found, generates a **witness** (proof of vulnerability):

```python
# Witness for ^(a+)+$
# prefix = "a"
# pump = "a"
# suffix = "!"

# Attack string: prefix + pump * n + suffix
# As n grows, matching time grows exponentially
```

### 3. Fuzz Checker

Dynamic analysis using a step-counting VM:

#### VM Architecture

```
┌─────────────────────────────────────┐
│           Regex VM                   │
├─────────────────────────────────────┤
│  Program: Compiled instructions      │
│  ┌─────────────────────────────────┐│
│  │ 0: CHAR 'a'                     ││
│  │ 1: SPLIT 0, 2                   ││
│  │ 2: MATCH                        ││
│  └─────────────────────────────────┘│
│                                      │
│  Interpreter:                        │
│  - Track step count                  │
│  - Detect exponential growth         │
│  - Generate attack candidates        │
└─────────────────────────────────────┘
```

#### Fuzzing Process

```python
# 1. Generate seeds from pattern structure
seeds = seeder.generate(pattern)
# ["a", "aa", "aaa", "!", "a!"]

# 2. Mutate seeds
for seed in seeds:
    mutations = mutator.mutate(seed)
    # Repeat, insert, delete, swap characters

    # 3. Count steps for each mutation
    for mutation in mutations:
        steps = vm.count_steps(pattern, mutation)

        # 4. Check for vulnerability
        if steps > threshold:
            # Potential vulnerability found!
            pass
```

#### Step Counting

```python
# Linear pattern: steps ≈ n
# Polynomial O(n²): steps ≈ n²
# Exponential O(2^n): steps ≈ 2^n

# Detection thresholds:
LINEAR_THRESHOLD = 100      # Steps per character
POLYNOMIAL_THRESHOLD = 10000
EXPONENTIAL_THRESHOLD = 100000
```

### 4. Match Mode (False Positive Control)

The `match_mode` setting controls how patterns are analyzed:

```python
from redoctor.config import MatchMode

# AUTO (default): Infer from pattern anchors
# FULL: Assume full-string matching (conservative)
# PARTIAL: Assume partial matching (fewer false positives)
```

| Mode | Use Case | Behavior |
|:-----|:---------|:---------|
| AUTO | General use | Checks for `$` anchor and continuation |
| FULL | Security audits | All multi-transitions are exploitable |
| PARTIAL | Search-style | Only flagged if anchor/continuation exists |

See [Configuration Guide](configuration.md#match-mode-false-positive-control) for details.

### 5. Complexity Analyzer

Classifies vulnerability severity:

```python
from redoctor.diagnostics.complexity import Complexity, ComplexityType

# Classification based on step growth:
# - Linear: Safe
# - Polynomial (n², n³): Moderate/High risk
# - Exponential (2^n): Critical risk

# Measurement approach:
# Run with inputs of length 5, 10, 15, 20
# Compare step counts
# Fit to complexity curve
```

### 6. Recall Validator

Confirms vulnerabilities with real execution:

```python
# Generate attack string
attack = prefix + pump * n + suffix

# Measure actual execution time
# with increasing n values
for n in [10, 20, 30]:
    attack = build_attack(n)
    time = measure_match_time(pattern, attack)

    # If time grows as expected → CONFIRMED
    # If time is constant → FALSE POSITIVE
```

## Checker Selection

ReDoctor automatically selects the best checker:

```python
def select_checker(pattern: Pattern) -> Checker:
    # 1. Check for backreferences
    if has_backreferences(pattern):
        return FuzzChecker()  # Automaton can't handle backrefs

    # 2. Check NFA size
    nfa = build_nfa(pattern)
    if nfa.size > MAX_NFA_SIZE:
        return FuzzChecker()  # NFA too large

    # 3. Default to automaton
    return AutomatonChecker()
```

## Performance Characteristics

| Aspect | Automaton Checker | Fuzz Checker |
|:-------|:------------------|:-------------|
| Speed | Very fast (ms) | Slower (100ms-s) |
| Accuracy | High | Good |
| Backreferences | ❌ Not supported | ✅ Supported |
| Lookaround | Partial | ✅ Full |
| Deterministic | ✅ Yes | ❌ No (random seed) |

## Diagnostics Output

The final output includes:

```python
Diagnostics(
    status=Status.VULNERABLE,
    source="^(a+)+$",
    complexity=Complexity(EXPONENTIAL),  # O(2^n)
    attack_pattern=AttackPattern(
        prefix="a",
        pump="aaaaaaaaaaaa",
        suffix="!",
    ),
    hotspot=Hotspot(
        start=0,
        end=8,
        pattern="^(a+)+$",
    ),
    checker="automaton",
    message="ReDoS vulnerability detected with O(2^n) complexity.",
)
```

## Extending ReDoctor

### Custom Checkers

```python
from redoctor.diagnostics.diagnostics import Diagnostics

class CustomChecker:
    def check(self, pattern: str) -> Diagnostics:
        # Your custom detection logic
        pass
```

### Custom Seeders

```python
from redoctor.fuzz.seeder import Seeder

class CustomSeeder(Seeder):
    def generate(self, pattern) -> List[FString]:
        # Your custom seed generation
        pass
```

## Next Steps

- [Understanding ReDoS →](redos-explained.md)
- [Vulnerable Patterns →](vulnerable-patterns.md)
- [API Reference →](api-reference.md)
