---
title: Contributing to ReDoctor
description: Guidelines for contributing to ReDoctor. Learn how to set up development environment and submit changes.
---

# Contributing

Thank you for your interest in contributing to ReDoctor! This guide will help you get started.

## Ways to Contribute

- 🐛 **Report bugs** - Open an issue describing the problem
- 💡 **Suggest features** - Share ideas for improvements
- 📖 **Improve docs** - Fix typos, add examples, clarify explanations
- 🔧 **Submit fixes** - Fix bugs or implement features
- ⭐ **Star the repo** - Show your support

## Development Setup

### Prerequisites

- Python 3.6 or higher
- Git
- Make (optional, for convenience)

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/GetPageSpeed/redoctor.git
cd redoctor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install in development mode
pip install -e ".[dev]"

# Verify installation
redoctor --version
python -c "import redoctor; print(redoctor.__version__)"
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/redoctor --cov-report=html

# Run specific test file
pytest tests/test_checker.py

# Run specific test
pytest tests/test_checker.py::test_exponential_pattern

# Run in parallel (faster)
pytest tests/ -n auto
```

### Code Quality

```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/

# Type checking (if mypy is installed)
mypy src/redoctor
```

## Code Style

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Maximum line length: 88 characters (Black default)
- Use type hints

### Example

```python
from typing import Optional, List

def check_pattern(
    pattern: str,
    flags: Optional[Flags] = None,
    config: Optional[Config] = None,
) -> Diagnostics:
    """Check a regex pattern for ReDoS vulnerabilities.

    Args:
        pattern: The regex pattern to check.
        flags: Optional regex flags.
        config: Optional configuration.

    Returns:
        Diagnostics object with analysis results.

    Raises:
        ParseError: If the pattern cannot be parsed.

    Example:
        >>> result = check_pattern(r"^(a+)+$")
        >>> print(result.is_vulnerable)
        True
    """
    # Implementation
    pass
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

feat(parser): add support for atomic groups
fix(checker): handle empty character classes
docs(readme): update installation instructions
test(vm): add tests for step counting
refactor(nfa): simplify epsilon elimination
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write code
- Add tests for new features
- Update documentation if needed
- Ensure all tests pass

### 3. Commit

```bash
git add .
git commit -m "feat(scope): add new feature"
```

### 4. Push

```bash
git push origin feature/my-feature
```

### 5. Open Pull Request

- Go to GitHub
- Click "New Pull Request"
- Fill in the template
- Request review

### PR Checklist

- [ ] Tests pass locally
- [ ] New code has tests
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow conventions
- [ ] No linting errors

## Project Structure

```
redoctor/
├── src/
│   └── redoctor/
│       ├── __init__.py       # Public API
│       ├── checker.py        # Main HybridChecker
│       ├── cli.py            # CLI entry point
│       ├── config.py         # Configuration
│       ├── exceptions.py     # Custom exceptions
│       ├── automaton/        # Automaton-based checker
│       │   ├── checker.py
│       │   ├── eps_nfa.py
│       │   ├── eps_nfa_builder.py
│       │   ├── complexity_analyzer.py
│       │   └── witness.py
│       ├── fuzz/             # Fuzz-based checker
│       │   ├── checker.py
│       │   ├── fstring.py
│       │   ├── seeder.py
│       │   └── mutators.py
│       ├── parser/           # Regex parser
│       │   ├── parser.py
│       │   ├── ast.py
│       │   └── flags.py
│       ├── vm/               # Regex VM
│       │   ├── builder.py
│       │   ├── interpreter.py
│       │   ├── inst.py
│       │   └── program.py
│       ├── diagnostics/      # Results
│       │   ├── diagnostics.py
│       │   ├── complexity.py
│       │   ├── attack_pattern.py
│       │   └── hotspot.py
│       ├── recall/           # Validation
│       │   └── validator.py
│       ├── unicode/          # Unicode support
│       └── integrations/     # Source scanning
│           └── source_scanner.py
├── tests/                    # Test suite
├── docs/                     # Documentation
└── pyproject.toml
```

## Testing Guidelines

### Test File Naming

```
tests/
├── test_checker.py
├── test_parser.py
├── test_automaton.py
├── test_fuzz.py
├── test_vm.py
└── ...
```

### Test Structure

```python
import pytest
from redoctor import check, Config

class TestChecker:
    """Tests for the main checker."""

    def test_safe_pattern(self):
        """Safe patterns should return is_safe=True."""
        result = check(r"^[a-z]+$")
        assert result.is_safe
        assert not result.is_vulnerable

    def test_vulnerable_pattern(self):
        """Vulnerable patterns should be detected."""
        result = check(r"^(a+)+$")
        assert result.is_vulnerable
        assert result.complexity.is_exponential

    @pytest.mark.parametrize("pattern,expected_safe", [
        (r"^a+$", True),
        (r"^(a+)+$", False),
        (r"^[0-9]+$", True),
    ])
    def test_multiple_patterns(self, pattern, expected_safe):
        """Test multiple patterns with parameterization."""
        result = check(pattern)
        assert result.is_safe == expected_safe
```

### Coverage

Aim for >80% code coverage. Check with:

```bash
pytest tests/ --cov=src/redoctor --cov-report=html
open htmlcov/index.html
```

## Documentation

### Building Docs

```bash
# Install mkdocs
pip install mkdocs-material mkdocs-minify-plugin

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

### Adding Pages

1. Create markdown file in `docs/`
2. Add to navigation in `mkdocs.yml`
3. Include front matter for SEO

```markdown
---
title: Page Title
description: SEO-friendly description of the page content.
---

# Page Title

Content here...
```

## Questions?

- Open an [issue](https://github.com/GetPageSpeed/redoctor/issues)
- Start a [discussion](https://github.com/GetPageSpeed/redoctor/discussions)

## License

By contributing, you agree that your contributions will be licensed under the [Business Source License 1.1](https://github.com/GetPageSpeed/redoctor/blob/main/LICENSE) (BSL-1.1), the same license as the project. The code will convert to MIT license on January 9, 2031.

---

Thank you for contributing! 🙏
