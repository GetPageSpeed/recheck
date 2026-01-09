<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/GetPageSpeed/redoctor/main/docs/assets/logo-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/GetPageSpeed/redoctor/main/docs/assets/logo-light.svg">
  <img alt="ReDoctor Logo" src="https://raw.githubusercontent.com/GetPageSpeed/redoctor/main/docs/assets/logo-light.svg" width="400">
</picture>

# ReDoctor

**The Python ReDoS Vulnerability Scanner** — Protect your applications from Regular Expression Denial of Service attacks.

[![PyPI version](https://img.shields.io/pypi/v/redoctor.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/redoctor/)
[![Python versions](https://img.shields.io/pypi/pyversions/redoctor.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/redoctor/)
[![License](https://img.shields.io/badge/license-BSL--1.1-orange.svg?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/GetPageSpeed/redoctor/tests.yml?branch=main&style=flat-square&logo=github&label=tests)](https://github.com/GetPageSpeed/redoctor/actions)
[![codecov](https://img.shields.io/codecov/c/github/GetPageSpeed/redoctor?style=flat-square&logo=codecov)](https://codecov.io/gh/GetPageSpeed/redoctor)
[![Downloads](https://img.shields.io/pypi/dm/redoctor.svg?style=flat-square)](https://pypi.org/project/redoctor/)

> ⚠️ **License Notice**: ReDoctor is licensed under the [Business Source License 1.1](LICENSE) (BSL-1.1).
> **Non-commercial use is free.** Commercial production use requires a [paid license](https://www.getpagespeed.com/contact).
> The code will convert to MIT license on January 9, 2031.

---

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-documentation">Documentation</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 🚨 What is ReDoS?

**Regular Expression Denial of Service (ReDoS)** is a type of algorithmic complexity attack that exploits the worst-case behavior of regex engines. A vulnerable regex can cause your application to hang for minutes or hours when processing malicious input.

```python
# ⚠️ This innocent-looking regex is VULNERABLE!
import re
pattern = r"^(a+)+$"

# This will hang your application:
re.match(pattern, "a" * 30 + "!")  # Takes exponential time!
```

**ReDoctor** detects these vulnerabilities before they reach production.

## ⚡ Quick Start

```bash
# Install
pip install redoctor

# Check a pattern from command line
redoctor '^(a+)+$'
# Output: VULNERABLE: ^(a+)+$ - Complexity: O(2^n)

# Use in Python
from redoctor import check

result = check(r"^(a+)+$")
if result.is_vulnerable:
    print(f"🚨 Vulnerable! Complexity: {result.complexity}")
    print(f"   Attack string: {result.attack}")
```

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔬 Hybrid Analysis Engine
Combines **static automata-based analysis** with **intelligent fuzzing** for comprehensive detection. Catches vulnerabilities that single-approach tools miss.

### ⚡ Fast & Zero Dependencies
Pure Python with no external dependencies. Runs in milliseconds for most patterns. Compatible with Python 3.6+.

</td>
<td width="50%">

### 🎯 Accurate Results
Generates **proof-of-concept attack strings** with complexity analysis (`O(n²)`, `O(2ⁿ)`, etc.). Low false-positive rate through recall validation.

### 🛡️ Source Code Scanning
Scan your entire Python codebase for vulnerable regex patterns. Integrates with CI/CD pipelines.

</td>
</tr>
</table>

## 📦 Installation

```bash
pip install redoctor
```

**Requirements:** Python 3.6+
**Dependencies:** None (pure Python)

## 🔧 Usage

### Command Line Interface

```bash
# Check a single pattern
redoctor '^(a+)+$'

# Verbose output with attack details
redoctor '(a|a)*$' --verbose

# Check with flags
redoctor 'pattern' --ignore-case --multiline

# Read patterns from stdin
echo '^(a+)+$' | redoctor --stdin

# Set timeout
redoctor 'complex-pattern' --timeout 30
```

**Exit codes:**
- `0` - Pattern is safe
- `1` - Pattern is vulnerable
- `2` - Error occurred

### Python API

```python
from redoctor import check, is_vulnerable, Config

# Simple check
result = check(r"^(a+)+$")
print(result.status)        # Status.VULNERABLE
print(result.complexity)    # O(2^n)
print(result.attack)        # 'aaaaaaaaaaaaaaaaaaaaa!'

# Quick vulnerability check
if is_vulnerable(r"(x+x+)+y"):
    print("Don't use this pattern!")

# Access attack pattern details
if result.is_vulnerable:
    attack = result.attack_pattern
    print(f"Prefix: {attack.prefix!r}")
    print(f"Pump: {attack.pump!r}")
    print(f"Suffix: {attack.suffix!r}")

    # Generate attack strings of different lengths
    short_attack = attack.build(10)   # 10 pump repetitions
    long_attack = attack.build(100)   # 100 pump repetitions

# Custom configuration
config = Config(
    timeout=30.0,           # Analysis timeout in seconds
    max_attack_length=4096, # Max attack string length
)
result = check(r"complex-pattern", config=config)

# Quick mode for CI/CD
config = Config.quick()  # 1 second timeout
result = check(pattern, config=config)
```

### Source Code Scanning

Scan your Python codebase for vulnerable regex patterns:

```python
from redoctor.integrations import scan_file, scan_directory

# Scan a single file
vulnerabilities = scan_file("myapp/validators.py")
for vuln in vulnerabilities:
    print(f"{vuln.file}:{vuln.line} - {vuln.pattern}")
    print(f"  Complexity: {vuln.diagnostics.complexity}")

# Scan entire directory
for vuln in scan_directory("src/", recursive=True):
    if vuln.is_vulnerable:
        print(f"🚨 {vuln}")
```

## 📊 Complexity Types

ReDoctor classifies vulnerabilities by their time complexity:

| Complexity | Description | Risk Level |
|------------|-------------|------------|
| `O(n)` | Linear - Safe | ✅ Safe |
| `O(n²)` | Quadratic | ⚠️ Moderate |
| `O(n³)` | Cubic | ⚠️ High |
| `O(2ⁿ)` | Exponential | 🚨 Critical |

## 🔍 How It Works

ReDoctor uses a **hybrid approach** combining two detection methods:

```
┌─────────────────────────────────────────────────────────────┐
│                     ReDoctor Engine                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │   Automaton     │         │     Fuzz        │           │
│  │   Checker       │         │    Checker      │           │
│  │                 │         │                 │           │
│  │  • NFA analysis │         │  • VM execution │           │
│  │  • O(n) check   │         │  • Step counting│           │
│  │  • Witness gen  │         │  • Mutation     │           │
│  └────────┬────────┘         └────────┬────────┘           │
│           │                           │                     │
│           └───────────┬───────────────┘                     │
│                       │                                     │
│              ┌────────▼────────┐                            │
│              │ Recall Validator│                            │
│              │ (confirmation)  │                            │
│              └────────┬────────┘                            │
│                       │                                     │
│              ┌────────▼────────┐                            │
│              │   Diagnostics   │                            │
│              │  • Complexity   │                            │
│              │  • Attack string│                            │
│              │  • Hotspot      │                            │
│              └─────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

1. **Automaton Checker**: Builds an ε-NFA from the regex and analyzes for ambiguity patterns that cause backtracking.
2. **Fuzz Checker**: Executes patterns in a step-counting VM with evolved test strings to detect polynomial/exponential growth.
3. **Recall Validator**: Confirms detected vulnerabilities with real execution timing.

## 📚 Documentation

Full documentation is available at **[redoctor.getpagespeed.com](https://redoctor.getpagespeed.com)**

- [Getting Started](https://redoctor.getpagespeed.com/getting-started/)
- [CLI Reference](https://redoctor.getpagespeed.com/cli/)
- [Python API](https://redoctor.getpagespeed.com/api/)
- [Configuration](https://redoctor.getpagespeed.com/configuration/)
- [How ReDoS Works](https://redoctor.getpagespeed.com/redos-explained/)

## 🧪 Examples of Vulnerable Patterns

```python
from redoctor import check

# Classic nested quantifier - Exponential O(2^n)
check(r"^(a+)+$")           # VULNERABLE

# Overlapping alternatives - Exponential O(2^n)
check(r"(a|a)*$")           # VULNERABLE

# Polynomial O(n²)
check(r".*a.*a.*")          # VULNERABLE

# Email-like pattern - Often vulnerable
check(r"^([a-zA-Z0-9]+)*@") # VULNERABLE

# Safe patterns
check(r"^[a-z]+$")          # SAFE
check(r"^\d{1,10}$")        # SAFE
check(r"^[A-Z][a-z]*$")     # SAFE
```

## 🤝 Contributing

Contributions are welcome! See our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Clone the repo
git clone https://github.com/GetPageSpeed/redoctor.git
cd redoctor

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -x --tb=short

# Run with coverage
make tests
```

## 📄 License

ReDoctor is licensed under the [Business Source License 1.1](LICENSE) (BSL-1.1).

- ✅ **Free** for non-commercial and non-production use
- ✅ **Free** for personal projects, education, and research
- 💼 **Commercial production use** requires a [paid license](https://www.getpagespeed.com/contact)
- 🔓 Converts to [MIT License](LICENSE-MIT) on **January 9, 2031**

## 🙏 Acknowledgments

- Inspired by [recheck](https://makenowjust-labs.github.io/recheck/) and academic research on ReDoS detection
- Built with ❤️ by [GetPageSpeed](https://www.getpagespeed.com)

---

<p align="center">
  <strong>Protect your applications from ReDoS attacks.</strong><br>
  <a href="https://github.com/GetPageSpeed/redoctor">⭐ Star on GitHub</a> •
  <a href="https://pypi.org/project/redoctor/">📦 View on PyPI</a> •
  <a href="https://redoctor.getpagespeed.com">📚 Read the Docs</a>
</p>
