---
title: CLI Reference
description: Complete command-line reference for ReDoctor. Check regex patterns for ReDoS vulnerabilities from the terminal.
---

# CLI Reference

ReDoctor provides a powerful command-line interface for checking regex patterns.

## Basic Usage

```bash
redoctor PATTERN [OPTIONS]
```

Check a regex pattern for ReDoS vulnerabilities:

```bash
redoctor '^(a+)+$'
```

Output:
```
VULNERABLE: ^(a+)+$
  Complexity: O(2^n)
  Attack: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!'
```

## Options

### Pattern Input

| Option | Description |
|:-------|:------------|
| `PATTERN` | The regex pattern to check (positional argument) |
| `--stdin` | Read patterns from standard input (one per line) |

### Regex Flags

| Option | Short | Description |
|:-------|:------|:------------|
| `--ignore-case` | `-i` | Case-insensitive matching |
| `--multiline` | `-m` | Multi-line mode (`^` and `$` match line boundaries) |
| `--dotall` | `-s` | Dot matches newline |

### Output Control

| Option | Short | Description |
|:-------|:------|:------------|
| `--verbose` | `-v` | Verbose output with full attack details |
| `--quiet` | `-q` | Quiet mode (exit code only) |

### Analysis Options

| Option | Default | Description |
|:-------|:--------|:------------|
| `--timeout SECONDS` | `10` | Maximum analysis time in seconds |

### Information

| Option | Description |
|:-------|:------------|
| `--version` | Show version and exit |
| `--help` | Show help message and exit |

## Exit Codes

| Code | Meaning |
|:-----|:--------|
| `0` | Pattern is safe |
| `1` | Pattern is vulnerable |
| `2` | Error occurred (parse error, timeout, etc.) |

## Examples

### Basic Check

```bash
redoctor '^[a-z]+$'
# SAFE: ^[a-z]+$
```

### Verbose Output

```bash
redoctor '^(a+)+$' --verbose
```

Output:
```
Pattern: ^(a+)+$
Status:  VULNERABLE
Complexity: O(2^n)
Attack pattern:
  Prefix: 'a'
  Pump:   'aaaaaaaaaaaa'
  Suffix: '!'
  Example: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!'
Hotspot: ^(a+)+$
```

### Quiet Mode (CI/CD)

Perfect for scripts and automation:

```bash
redoctor '^(a+)+$' --quiet
echo $?
# 1 (vulnerable)

redoctor '^[a-z]+$' --quiet
echo $?
# 0 (safe)
```

### With Flags

```bash
# Case-insensitive
redoctor '[A-Z]+' --ignore-case

# Multiline
redoctor '^pattern$' --multiline

# Multiple flags
redoctor 'pattern' -i -m -s
```

### Custom Timeout

```bash
# Quick check (1 second)
redoctor 'complex-pattern' --timeout 1

# Thorough check (60 seconds)
redoctor 'complex-pattern' --timeout 60
```

### Multiple Patterns from Stdin

```bash
# From echo
echo -e '^(a+)+$\n^[a-z]+$' | redoctor --stdin

# From file
cat patterns.txt | redoctor --stdin

# From heredoc
redoctor --stdin << 'EOF'
^(a+)+$
(a|a)*$
^[a-z]+$
EOF
```

### Filtering Patterns File

```bash
# patterns.txt - lines starting with # are ignored
^(a+)+$
# This is a comment
^[a-z]+$
(x+x+)+y

# Check all patterns
cat patterns.txt | redoctor --stdin
```

## Integration Examples

### Shell Script

```bash
#!/bin/bash

PATTERN="$1"

if redoctor "$PATTERN" --quiet; then
    echo "✓ Pattern is safe to use"
    exit 0
else
    echo "✗ Pattern is vulnerable!"
    redoctor "$PATTERN" --verbose
    exit 1
fi
```

### Git Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Find regex patterns in staged Python files
git diff --cached --name-only --diff-filter=ACM | grep '\.py$' | while read file; do
    # Extract patterns and check them (simplified example)
    grep -oP "re\.(compile|match|search)\(['\"]\\K[^'\"]+(?=['\"])" "$file" | while read pattern; do
        if ! redoctor "$pattern" --quiet 2>/dev/null; then
            echo "ReDoS vulnerability in $file: $pattern"
            exit 1
        fi
    done
done
```

### CI/CD Pipeline (GitHub Actions)

```yaml
name: ReDoS Check

on: [push, pull_request]

jobs:
  redoctor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install ReDoctor
        run: pip install redoctor

      - name: Check patterns
        run: |
          # Check known patterns
          redoctor '^[a-z0-9]+$' --quiet

          # Or use the Python source scanner
          python -c "
          from redoctor.integrations import scan_directory
          vulns = list(scan_directory('src/', recursive=True))
          for v in vulns:
              print(f'::error file={v.file},line={v.line}::{v.pattern}')
          exit(1 if vulns else 0)
          "
```

### Makefile Target

```makefile
.PHONY: check-regex

check-regex:
	@echo "Checking regex patterns for ReDoS vulnerabilities..."
	@python -c "from redoctor.integrations import scan_directory; \
		vulns = list(scan_directory('src/')); \
		[print(f'{v.file}:{v.line}: {v.pattern}') for v in vulns]; \
		exit(1 if vulns else 0)"
```

## Advanced Usage

### Batch Processing

```bash
# Process patterns and save results
while IFS= read -r pattern; do
    result=$(redoctor "$pattern" 2>&1)
    echo "$pattern|$result" >> results.txt
done < patterns.txt
```

### JSON Output (via Python)

```bash
python -c "
import json
from redoctor import check

result = check(r'^(a+)+\$')
print(json.dumps(result.to_dict(), indent=2))
"
```

Output:
```json
{
  "status": "vulnerable",
  "source": "^(a+)+$",
  "flags": "",
  "message": "ReDoS vulnerability detected with O(2^n) complexity.",
  "complexity": {
    "type": "exponential",
    "degree": null,
    "summary": "O(2^n)"
  },
  "attack": {
    "pattern": "'a' + 'aaaaaaaaaaaa' * n + '!'",
    "string": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!",
    "prefix": "a",
    "pump": "aaaaaaaaaaaa",
    "suffix": "!"
  }
}
```

## Tips

!!! tip "Use Quotes"
    Always quote your patterns to prevent shell expansion:
    ```bash
    # Good
    redoctor '^(a+)+$'

    # Bad - shell may interpret special characters
    redoctor ^(a+)+$
    ```

!!! tip "Escape Backslashes"
    In shell, use single quotes or double backslashes:
    ```bash
    # Single quotes (recommended)
    redoctor '^\d+$'

    # Double quotes with escaped backslashes
    redoctor "^\\d+$"
    ```

!!! tip "Quick CI Checks"
    Use `--quiet` with `--timeout 1` for fast CI checks:
    ```bash
    redoctor 'pattern' --quiet --timeout 1 || echo "Check failed"
    ```
