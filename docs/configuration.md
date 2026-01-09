---
title: Configuration Guide
description: Configure ReDoctor for optimal ReDoS vulnerability detection. Learn about timeouts, checker types, and performance tuning.
---

# Configuration Guide

ReDoctor offers flexible configuration options to balance speed, thoroughness, and resource usage.

## Quick Configuration

Use preset configurations for common scenarios:

```python
from redoctor import check, Config

# Standard analysis (recommended for most cases)
result = check(pattern, config=Config.default())

# Fast checks (CI/CD, real-time validation)
result = check(pattern, config=Config.quick())

# Deep analysis (security audits)
result = check(pattern, config=Config.thorough())
```

## Configuration Options

### Full Options Reference

```python
from redoctor import Config
from redoctor.config import CheckerType, AccelerationMode, SeederType

config = Config(
    # === Checker Selection ===
    checker=CheckerType.AUTO,
    # AUTO: Automatically select best checker (default)
    # AUTOMATON: Use static analysis (fast, no backrefs)
    # FUZZ: Use fuzzing (slower, handles all patterns)

    # === Timeouts ===
    timeout=10.0,
    # Maximum time for entire analysis in seconds
    # Range: 0.1 to 300.0

    recall_timeout=1.0,
    # Timeout for each recall validation attempt
    # Range: 0.01 to 10.0

    # === Attack Generation ===
    max_attack_length=4096,
    # Maximum length of generated attack strings
    # Range: 64 to 65536

    attack_limit=10,
    # Number of attack strings to generate
    # Range: 1 to 100

    # === Fuzzing ===
    max_iterations=100000,
    # Maximum fuzzing iterations
    # Range: 1000 to 10000000

    random_seed=None,
    # Seed for reproducible fuzzing (None = random)
    # Type: int or None

    seeder=SeederType.STATIC,
    # STATIC: Generate seeds from pattern structure
    # DYNAMIC: Generate seeds dynamically

    acceleration=AccelerationMode.AUTO,
    # AUTO: Auto-detect acceleration mode
    # ON: Enable VM acceleration
    # OFF: Disable acceleration

    # === Limits ===
    max_nfa_size=35000,
    # Maximum NFA states before falling back to fuzzing
    # Range: 1000 to 1000000

    max_pattern_size=1500,
    # Maximum pattern length to analyze
    # Range: 10 to 10000

    # === Validation ===
    recall_limit=10,
    # Maximum recall validation attempts
    # Range: 1 to 100

    skip_recall=False,
    # Skip recall validation (faster but less accurate)
    # Type: bool
)
```

## Preset Configurations

### Default Configuration

Balanced settings for general use:

```python
Config.default()
```

| Setting | Value | Description |
|:--------|:------|:------------|
| `timeout` | 10s | Reasonable timeout for most patterns |
| `max_attack_length` | 4096 | Sufficient for demonstrating vulnerabilities |
| `max_iterations` | 100,000 | Good balance of speed and coverage |
| `skip_recall` | False | Validates findings for accuracy |

**Best for:** Development, testing, general security checks

### Quick Configuration

Fast settings for real-time checks:

```python
Config.quick()
```

| Setting | Value | Description |
|:--------|:------|:------------|
| `timeout` | 1s | Fast timeout |
| `max_attack_length` | 256 | Minimal attack strings |
| `max_iterations` | 10,000 | Quick fuzzing |
| `recall_timeout` | 0.1s | Fast validation |
| `skip_recall` | True | Skip validation for speed |

**Best for:** CI/CD pipelines, real-time form validation, quick scans

### Thorough Configuration

Comprehensive analysis for security audits:

```python
Config.thorough()
```

| Setting | Value | Description |
|:--------|:------|:------------|
| `timeout` | 30s | Extended analysis time |
| `max_attack_length` | 8192 | Longer attack strings |
| `max_iterations` | 500,000 | Deep fuzzing |
| `recall_timeout` | 5s | Thorough validation |

**Best for:** Security audits, pre-release checks, one-time scans

## Checker Types

ReDoctor supports two checking strategies:

### Automaton Checker

Static analysis using automata theory:

```python
from redoctor.config import CheckerType

config = Config(checker=CheckerType.AUTOMATON)
```

**Advantages:**

- :zap: Very fast
- :dart: Deterministic results
- :chart_with_upwards_trend: Accurate complexity classification

**Limitations:**

- :x: Cannot handle backreferences (`\1`, `\2`)
- :x: Limited lookaround support

### Fuzz Checker

Dynamic analysis using fuzzing:

```python
config = Config(checker=CheckerType.FUZZ)
```

**Advantages:**

- :white_check_mark: Handles all regex features
- :white_check_mark: Catches edge cases
- :white_check_mark: Works with backreferences

**Limitations:**

- :hourglass: Slower than automaton
- :game_die: Non-deterministic (use `random_seed` for reproducibility)

### Auto Selection (Default)

Automatically selects the best checker:

```python
config = Config(checker=CheckerType.AUTO)
```

- Uses **automaton** for simple patterns
- Falls back to **fuzz** for complex patterns (backreferences, etc.)

## Performance Tuning

### For Speed

```python
config = Config(
    timeout=1.0,
    max_iterations=5000,
    max_attack_length=256,
    skip_recall=True,
    checker=CheckerType.AUTOMATON,  # Faster for simple patterns
)
```

### For Accuracy

```python
config = Config(
    timeout=60.0,
    max_iterations=1000000,
    max_attack_length=16384,
    skip_recall=False,
    recall_limit=20,
    checker=CheckerType.AUTO,
)
```

### For Reproducibility

```python
config = Config(
    random_seed=42,  # Fixed seed
    checker=CheckerType.FUZZ,
)
```

## Use Cases

### CI/CD Pipeline

Fast checks with clear pass/fail:

```python
from redoctor import is_vulnerable, Config

config = Config.quick()

# Check critical patterns
patterns = get_patterns_from_codebase()
vulnerable = [p for p in patterns if is_vulnerable(p, config=config)]

if vulnerable:
    print("FAILED: Vulnerable patterns found!")
    for p in vulnerable:
        print(f"  - {p}")
    sys.exit(1)
```

### User Input Validation

Real-time validation of user-submitted patterns:

```python
from redoctor import check, Config

config = Config(
    timeout=0.5,          # Very fast
    skip_recall=True,     # Skip validation
    max_iterations=1000,  # Minimal fuzzing
)

def validate_user_regex(pattern: str) -> bool:
    """Validate a user-submitted regex pattern."""
    result = check(pattern, config=config)
    return result.is_safe
```

### Security Audit

Comprehensive analysis for security review:

```python
from redoctor import check, Config
from redoctor.integrations import scan_directory

config = Config.thorough()

# Scan entire codebase
for vuln in scan_directory("src/", config=config):
    print(f"[{vuln.diagnostics.complexity}] {vuln.file}:{vuln.line}")
    print(f"  Pattern: {vuln.pattern}")
    print(f"  Attack: {vuln.diagnostics.attack[:100]}...")
    print()
```

### Batch Processing

Process many patterns efficiently:

```python
from redoctor import HybridChecker, Config

# Create checker once
config = Config.default()
checker = HybridChecker(config)

# Check many patterns
patterns = load_patterns()
results = [(p, checker.check(p)) for p in patterns]

# Report
vulnerable = [(p, r) for p, r in results if r.is_vulnerable]
print(f"Found {len(vulnerable)} vulnerable patterns out of {len(patterns)}")
```

## Environment Variables

ReDoctor doesn't use environment variables by default, but you can implement your own:

```python
import os
from redoctor import Config

config = Config(
    timeout=float(os.getenv("REDOCTOR_TIMEOUT", "10")),
    skip_recall=os.getenv("REDOCTOR_SKIP_RECALL", "false").lower() == "true",
)
```

## Next Steps

- [Python API →](api.md)
- [Source Scanning →](source-scanning.md)
- [CLI Reference →](cli.md)
