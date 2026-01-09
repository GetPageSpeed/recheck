---
title: API Reference
description: Complete Python API reference for ReDoctor. All classes, functions, and types documented.
---

# API Reference

Complete reference documentation for the ReDoctor Python API.

## Main Module

### `redoctor`

```python
import redoctor
```

#### Functions

##### `check(pattern, flags=None, config=None)`

Check a regex pattern for ReDoS vulnerabilities.

```python
from redoctor import check

result = check(r"^(a+)+$")
```

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `pattern` | `str` | *required* | Regex pattern to check |
| `flags` | `Flags` | `None` | Regex flags |
| `config` | `Config` | `None` | Configuration options |

**Returns:** `Diagnostics`

---

##### `check_pattern(pattern, config=None)`

Check a pre-parsed pattern for ReDoS vulnerabilities.

```python
from redoctor import check_pattern
from redoctor.parser.parser import parse

parsed = parse(r"^(a+)+$")
result = check_pattern(parsed)
```

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `pattern` | `Pattern` | *required* | Parsed pattern object |
| `config` | `Config` | `None` | Configuration options |

**Returns:** `Diagnostics`

---

##### `is_vulnerable(pattern, flags=None, config=None)`

Quick check if a pattern is vulnerable.

```python
from redoctor import is_vulnerable

if is_vulnerable(r"^(a+)+$"):
    print("Vulnerable!")
```

**Returns:** `bool`

---

##### `is_safe(pattern, flags=None, config=None)`

Quick check if a pattern is safe.

```python
from redoctor import is_safe

if is_safe(r"^[a-z]+$"):
    print("Safe to use")
```

**Returns:** `bool`

---

### Classes

#### `HybridChecker`

Main checker class combining automaton and fuzz analysis.

```python
from redoctor import HybridChecker, Config

checker = HybridChecker(Config.default())
result = checker.check(r"^(a+)+$")
```

##### `__init__(config=None)`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `config` | `Config` | `None` | Configuration options |

##### `check(pattern, flags=None)`

Check a regex pattern.

**Returns:** `Diagnostics`

##### `check_pattern(pattern)`

Check a parsed Pattern object.

**Returns:** `Diagnostics`

---

## Configuration

### `redoctor.Config`

Configuration options for analysis.

```python
from redoctor import Config

config = Config(timeout=30.0, skip_recall=True)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `checker` | `CheckerType` | `AUTO` | Checker to use |
| `timeout` | `float` | `10.0` | Analysis timeout (seconds) |
| `max_attack_length` | `int` | `4096` | Max attack string length |
| `attack_limit` | `int` | `10` | Number of attack strings |
| `random_seed` | `int\|None` | `None` | RNG seed for reproducibility |
| `acceleration` | `AccelerationMode` | `AUTO` | VM acceleration |
| `seeder` | `SeederType` | `STATIC` | Seed generation strategy |
| `max_iterations` | `int` | `100000` | Max fuzz iterations |
| `max_nfa_size` | `int` | `35000` | Max NFA states |
| `max_pattern_size` | `int` | `1500` | Max pattern length |
| `recall_limit` | `int` | `10` | Max validations |
| `recall_timeout` | `float` | `1.0` | Validation timeout |
| `skip_recall` | `bool` | `False` | Skip validation |

#### Class Methods

##### `Config.default()`

Standard configuration.

**Returns:** `Config`

##### `Config.quick()`

Fast analysis configuration.

**Returns:** `Config`

##### `Config.thorough()`

Comprehensive analysis configuration.

**Returns:** `Config`

---

### `redoctor.CheckerType`

Enum for checker selection.

```python
from redoctor import CheckerType

CheckerType.AUTO       # Automatic selection
CheckerType.AUTOMATON  # Static analysis
CheckerType.FUZZ       # Fuzzing
```

---

### `redoctor.AccelerationMode`

Enum for VM acceleration.

```python
from redoctor import AccelerationMode

AccelerationMode.AUTO  # Automatic
AccelerationMode.ON    # Enabled
AccelerationMode.OFF   # Disabled
```

---

### `redoctor.SeederType`

Enum for seed generation.

```python
from redoctor import SeederType

SeederType.STATIC   # Pattern-based seeds
SeederType.DYNAMIC  # Dynamic generation
```

---

## Diagnostics

### `redoctor.Diagnostics`

Analysis result object.

```python
from redoctor import check

result = check(r"^(a+)+$")
print(result.status)       # Status.VULNERABLE
print(result.is_vulnerable)  # True
print(result.complexity)   # O(2^n)
print(result.attack)       # "aaaaaaa...!"
```

#### Properties

| Property | Type | Description |
|:---------|:-----|:------------|
| `status` | `Status` | Analysis status |
| `source` | `str` | Original pattern |
| `flags` | `str` | Regex flags |
| `complexity` | `Complexity\|None` | Detected complexity |
| `attack_pattern` | `AttackPattern\|None` | Attack structure |
| `hotspot` | `Hotspot\|None` | Vulnerable portion |
| `checker` | `str` | Checker used |
| `message` | `str` | Human-readable message |
| `error` | `str\|None` | Error message |
| `is_vulnerable` | `bool` | True if vulnerable |
| `is_safe` | `bool` | True if safe |
| `attack` | `str\|None` | Generated attack string |

#### Methods

##### `to_dict()`

Convert to dictionary for JSON serialization.

**Returns:** `dict`

---

### `redoctor.Status`

Enum for analysis status.

```python
from redoctor import Status

Status.SAFE        # Pattern is safe
Status.VULNERABLE  # Pattern is vulnerable
Status.UNKNOWN     # Cannot determine
Status.ERROR       # Analysis failed
```

---

### `redoctor.Complexity`

Time complexity representation.

```python
from redoctor import Complexity

# Create complexity objects
safe = Complexity.safe()          # O(n)
poly = Complexity.polynomial(2)   # O(n²)
exp = Complexity.exponential()    # O(2^n)
```

#### Properties

| Property | Type | Description |
|:---------|:-----|:------------|
| `type` | `ComplexityType` | Complexity type |
| `degree` | `int\|None` | Polynomial degree |
| `summary` | `str` | Human-readable (e.g., "O(n²)") |
| `is_safe` | `bool` | True if O(n) |
| `is_vulnerable` | `bool` | True if polynomial/exponential |
| `is_polynomial` | `bool` | True if polynomial |
| `is_exponential` | `bool` | True if exponential |

#### Class Methods

##### `Complexity.safe()`

Create O(n) complexity.

##### `Complexity.polynomial(degree)`

Create O(n^degree) complexity.

##### `Complexity.exponential()`

Create O(2^n) complexity.

---

### `redoctor.ComplexityType`

Enum for complexity types.

```python
from redoctor import ComplexityType

ComplexityType.SAFE         # O(n)
ComplexityType.POLYNOMIAL   # O(n^k)
ComplexityType.EXPONENTIAL  # O(2^n)
```

---

### `redoctor.AttackPattern`

Attack string structure.

```python
attack_pattern = result.attack_pattern

attack_pattern.prefix    # "a"
attack_pattern.pump      # "aaaa"
attack_pattern.suffix    # "!"

# Build attack strings
attack_pattern.build(10)   # 10 pump repetitions
attack_pattern.build(100)  # 100 repetitions
attack_pattern.attack      # Default attack
```

#### Properties

| Property | Type | Description |
|:---------|:-----|:------------|
| `prefix` | `str` | Attack prefix |
| `pump` | `str` | Repeated portion |
| `suffix` | `str` | Attack suffix |
| `base` | `int` | Base repetitions |
| `repeat` | `int` | Default repetitions |
| `attack` | `str` | Default attack string |

#### Methods

##### `build(n=None)`

Build attack string with n pump repetitions.

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `n` | `int\|None` | `self.repeat` | Pump count |

**Returns:** `str`

##### `with_repeat(n)`

Create copy with different repeat count.

**Returns:** `AttackPattern`

##### `simple(pump, suffix="!", repeat=20)` (classmethod)

Create simple pattern without prefix.

**Returns:** `AttackPattern`

---

### `redoctor.Hotspot`

Vulnerable portion of the pattern.

```python
hotspot = result.hotspot

hotspot.start    # 1
hotspot.end      # 6
hotspot.text     # "(a+)+"
```

#### Properties

| Property | Type | Description |
|:---------|:-----|:------------|
| `start` | `int` | Start position |
| `end` | `int` | End position |
| `pattern` | `str` | Full pattern |
| `text` | `str` | Hotspot text |

---

## Flags

### `redoctor.Flags`

Regex flags configuration.

```python
from redoctor import Flags

flags = Flags(
    ignore_case=True,
    multiline=True,
    dotall=False,
    unicode=True,
    global_match=False,
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `ignore_case` | `bool` | `False` | Case-insensitive |
| `multiline` | `bool` | `False` | Multi-line mode |
| `dotall` | `bool` | `False` | Dot matches newline |
| `unicode` | `bool` | `True` | Unicode mode |
| `global_match` | `bool` | `False` | Global matching |

---

## Exceptions

### `redoctor.RedoctorError`

Base exception for all ReDoctor errors.

```python
from redoctor import RedoctorError

try:
    result = check(pattern)
except RedoctorError as e:
    print(f"Error: {e}")
```

---

### `redoctor.ParseError`

Raised when a regex pattern cannot be parsed.

```python
from redoctor import ParseError

try:
    result = check("[invalid")
except ParseError as e:
    print(f"Parse error: {e}")
```

---

### `redoctor.TimeoutError`

Raised when analysis times out.

```python
from redoctor import TimeoutError

try:
    result = check(pattern, config=Config(timeout=0.1))
except TimeoutError as e:
    print(f"Timed out: {e}")
```

---

## Integrations

### `redoctor.integrations`

Source code scanning utilities.

```python
from redoctor.integrations import scan_file, scan_directory, scan_source
```

#### `scan_file(filepath, config=None)`

Scan a Python file for vulnerable patterns.

**Returns:** `List[SourceVulnerability]`

#### `scan_directory(directory, recursive=True, config=None)`

Scan a directory for vulnerable patterns.

**Returns:** `Iterator[SourceVulnerability]`

#### `scan_source(source, filename="<string>", config=None)`

Scan Python source code string.

**Returns:** `List[SourceVulnerability]`

---

### `SourceVulnerability`

Vulnerability found in source code.

| Property | Type | Description |
|:---------|:-----|:------------|
| `file` | `str` | Source file path |
| `line` | `int` | Line number (1-based) |
| `column` | `int` | Column (0-based) |
| `pattern` | `str` | Regex pattern |
| `diagnostics` | `Diagnostics` | Analysis result |
| `context` | `str` | Line of code |
| `is_vulnerable` | `bool` | True if vulnerable |

---

## Module Exports

All public symbols:

```python
from redoctor import (
    # Main API
    check,
    check_pattern,
    is_safe,
    is_vulnerable,
    HybridChecker,

    # Configuration
    Config,
    CheckerType,
    AccelerationMode,
    SeederType,
    Flags,

    # Diagnostics
    Diagnostics,
    Status,
    Complexity,
    ComplexityType,
    AttackPattern,
    Hotspot,

    # Exceptions
    RedoctorError,
    ParseError,
    TimeoutError,

    # Version
    __version__,
)
```
