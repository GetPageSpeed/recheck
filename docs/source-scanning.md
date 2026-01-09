---
title: Source Code Scanning
description: Automatically detect ReDoS vulnerabilities in your Python codebase. Scan files and directories for vulnerable regex patterns.
---

# Source Code Scanning

ReDoctor can automatically scan your Python source code to find regex patterns and check them for vulnerabilities.

## Quick Start

```python
from redoctor.integrations import scan_file, scan_directory

# Scan a single file
vulnerabilities = scan_file("myapp/validators.py")
for vuln in vulnerabilities:
    print(f"{vuln.file}:{vuln.line}: {vuln.pattern}")

# Scan entire project
for vuln in scan_directory("src/", recursive=True):
    if vuln.is_vulnerable:
        print(f"🚨 {vuln}")
```

## How It Works

The source scanner:

1. **Parses** Python source files using the `ast` module
2. **Finds** regex patterns in `re.compile()`, `re.match()`, `re.search()`, etc.
3. **Checks** each pattern for ReDoS vulnerabilities
4. **Reports** findings with file location and context

### Detected Patterns

The scanner finds patterns in these `re` module functions:

- `re.compile(pattern)`
- `re.match(pattern, string)`
- `re.search(pattern, string)`
- `re.fullmatch(pattern, string)`
- `re.findall(pattern, string)`
- `re.finditer(pattern, string)`
- `re.sub(pattern, repl, string)`
- `re.subn(pattern, repl, string)`
- `re.split(pattern, string)`

## API Reference

### `scan_file(filepath, config=None)`

Scan a single Python file for vulnerable patterns.

```python
from redoctor.integrations import scan_file
from redoctor import Config

# Basic usage
vulnerabilities = scan_file("path/to/file.py")

# With custom config
config = Config.quick()
vulnerabilities = scan_file("path/to/file.py", config=config)

# Process results
for vuln in vulnerabilities:
    print(f"Line {vuln.line}: {vuln.pattern}")
    print(f"  Complexity: {vuln.diagnostics.complexity}")
```

**Parameters:**

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `filepath` | `str` or `Path` | Path to Python file |
| `config` | `Config` | Optional configuration |

**Returns:** `List[SourceVulnerability]`

---

### `scan_directory(directory, recursive=True, config=None)`

Scan a directory for vulnerable patterns in Python files.

```python
from redoctor.integrations import scan_directory

# Scan recursively (default)
for vuln in scan_directory("src/"):
    print(vuln)

# Scan only top-level
for vuln in scan_directory("src/", recursive=False):
    print(vuln)
```

**Parameters:**

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `directory` | `str` or `Path` | Directory to scan |
| `recursive` | `bool` | Scan subdirectories (default: True) |
| `config` | `Config` | Optional configuration |

**Returns:** `Iterator[SourceVulnerability]`

---

### `scan_source(source, filename="<string>", config=None)`

Scan Python source code as a string.

```python
from redoctor.integrations import scan_source

code = '''
import re

EMAIL_PATTERN = re.compile(r"^([a-zA-Z0-9]+)*@example.com$")
'''

vulnerabilities = scan_source(code, filename="example.py")
```

**Parameters:**

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `source` | `str` | Python source code |
| `filename` | `str` | Filename for reporting |
| `config` | `Config` | Optional configuration |

**Returns:** `List[SourceVulnerability]`

## SourceVulnerability Object

Each vulnerability found includes:

```python
from redoctor.integrations import scan_file

for vuln in scan_file("myapp/validators.py"):
    # Location
    vuln.file       # "myapp/validators.py"
    vuln.line       # 42 (1-based line number)
    vuln.column     # 8 (0-based column)

    # Pattern
    vuln.pattern    # "^(a+)+$"
    vuln.context    # 'PATTERN = re.compile(r"^(a+)+$")'

    # Diagnostics (full analysis result)
    vuln.diagnostics.status      # Status.VULNERABLE
    vuln.diagnostics.complexity  # O(2^n)
    vuln.diagnostics.attack      # Attack string

    # Quick check
    vuln.is_vulnerable  # True
```

## Practical Examples

### CLI-Style Scanner

```python
#!/usr/bin/env python3
"""Scan codebase for ReDoS vulnerabilities."""

import sys
from pathlib import Path
from redoctor.integrations import scan_directory
from redoctor import Config

def main():
    # Get directory from args or use current
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

    # Use quick config for speed
    config = Config.quick()

    # Scan and collect results
    vulnerabilities = list(scan_directory(directory, config=config))

    if not vulnerabilities:
        print("✓ No ReDoS vulnerabilities found!")
        return 0

    # Report findings
    print(f"Found {len(vulnerabilities)} potential issues:\n")

    for vuln in vulnerabilities:
        status = "VULNERABLE" if vuln.is_vulnerable else "UNKNOWN"
        complexity = vuln.diagnostics.complexity or "N/A"

        print(f"[{status}] {vuln.file}:{vuln.line}")
        print(f"  Pattern: {vuln.pattern}")
        print(f"  Complexity: {complexity}")
        print(f"  Context: {vuln.context}")
        print()

    return 1 if any(v.is_vulnerable for v in vulnerabilities) else 0

if __name__ == "__main__":
    sys.exit(main())
```

### Pre-commit Hook

```python
#!/usr/bin/env python3
"""Pre-commit hook for ReDoS scanning."""

import subprocess
import sys
from redoctor.integrations import scan_file
from redoctor import Config

def get_staged_python_files():
    """Get list of staged Python files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
    )
    return [f for f in result.stdout.strip().split("\n") if f.endswith(".py")]

def main():
    files = get_staged_python_files()
    if not files:
        return 0

    config = Config.quick()
    has_vulnerabilities = False

    for filepath in files:
        vulnerabilities = scan_file(filepath, config=config)

        for vuln in vulnerabilities:
            if vuln.is_vulnerable:
                has_vulnerabilities = True
                print(f"ReDoS vulnerability: {vuln.file}:{vuln.line}")
                print(f"  Pattern: {vuln.pattern}")
                print(f"  Complexity: {vuln.diagnostics.complexity}")
                print()

    if has_vulnerabilities:
        print("Commit blocked due to ReDoS vulnerabilities.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### GitHub Actions Workflow

```yaml
name: ReDoS Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  redoctor-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install ReDoctor
        run: pip install redoctor

      - name: Scan for ReDoS vulnerabilities
        run: |
          python << 'EOF'
          import sys
          from redoctor.integrations import scan_directory
          from redoctor import Config

          config = Config.quick()
          vulnerabilities = list(scan_directory("src/", config=config))

          for vuln in vulnerabilities:
              # GitHub Actions annotation format
              level = "error" if vuln.is_vulnerable else "warning"
              print(f"::{level} file={vuln.file},line={vuln.line}::{vuln.pattern}")

          if any(v.is_vulnerable for v in vulnerabilities):
              print("::error::ReDoS vulnerabilities detected!")
              sys.exit(1)

          print("No ReDoS vulnerabilities found.")
          EOF
```

### JSON Report Generator

```python
#!/usr/bin/env python3
"""Generate JSON report of ReDoS vulnerabilities."""

import json
from datetime import datetime
from pathlib import Path
from redoctor.integrations import scan_directory
from redoctor import Config

def generate_report(directory: str, output_file: str = "redoctor-report.json"):
    """Generate a JSON report of vulnerabilities."""
    config = Config.default()

    findings = []
    for vuln in scan_directory(directory, config=config):
        findings.append({
            "file": vuln.file,
            "line": vuln.line,
            "column": vuln.column,
            "pattern": vuln.pattern,
            "context": vuln.context,
            "status": vuln.diagnostics.status.value,
            "complexity": str(vuln.diagnostics.complexity) if vuln.diagnostics.complexity else None,
            "attack": vuln.diagnostics.attack,
            "message": vuln.diagnostics.message,
        })

    report = {
        "tool": "redoctor",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "directory": str(Path(directory).absolute()),
        "total_findings": len(findings),
        "vulnerable_count": sum(1 for f in findings if f["status"] == "vulnerable"),
        "findings": findings,
    }

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Report saved to {output_file}")
    return report

if __name__ == "__main__":
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_report(directory)
```

## Limitations

!!! warning "Current Limitations"

    - **Only static patterns**: F-strings and dynamically constructed patterns cannot be analyzed
    - **Only `re` module**: Patterns used with third-party regex libraries are not detected
    - **String literals only**: Patterns passed as variables are not tracked

### What's Detected

```python
# ✓ Detected
re.compile(r"^(a+)+$")
re.match(r"pattern", text)
pattern = re.compile(r"[a-z]+")

# ✗ Not detected
pattern = f"^{user_input}$"  # f-string
regex.compile(r"pattern")    # Not `re` module
re.compile(get_pattern())    # Function call
```

## Next Steps

- [CLI Reference →](cli.md)
- [Python API →](api.md)
- [Vulnerable Patterns →](vulnerable-patterns.md)
