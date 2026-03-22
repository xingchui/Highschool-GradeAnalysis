# Code Style Guidelines

This document outlines the coding standards for the Grade Analysis Web Application.

## Python Code Style

This project follows PEP 8 style guide for Python code.

### Code Formatting

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use blank lines to separate functions and classes
- Use meaningful variable and function names

### Naming Conventions

- **Functions**: `snake_case` (e.g., `calculate_rankings`)
- **Classes**: `PascalCase` (e.g., `GradeParser`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_SCORE`)
- **Variables**: `snake_case` (e.g., `student_data`)

### Imports

```python
# Standard library imports
import os
import json

# Third-party imports
import pandas as pd
from flask import Flask

# Local imports
from .parser import parse_excel
```

### Type Hints

Use type hints where appropriate:

```python
def calculate_rankings(scores: list[int]) -> list[int]:
    """Calculate rankings for a list of scores."""
    return sorted(scores, reverse=True)
```

### Docstrings

Use Google-style docstrings:

```python
def parse_excel(file_path: str) -> pd.DataFrame:
    """Parse an Excel file and return a DataFrame.
    
    Args:
        file_path: Path to the Excel file.
        
    Returns:
        DataFrame containing student data.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    pass
```

### Comments

- Use comments to explain complex logic
- Keep comments up to date with code changes
- Use TODO comments for incomplete code: `# TODO: Add feature X`

## HTML/CSS Style

- Use semantic HTML5 elements
- Use Bootstrap or similar CSS framework for styling
- Keep CSS in separate files or use inline styles for simple pages

## JavaScript Style

- Use ES6+ features (const, let, arrow functions)
- Use meaningful variable names
- Add comments for complex logic

## Linting Tools

This project uses:
- **flake8**: For code style checking
- **black**: For code formatting (optional)

```bash
# Install linting tools
pip install flake8 black

# Run flake8
flake8 app.py

# Format code with black
black app.py
```

## Git Commit Messages

- Use imperative mood: "Add feature" not "Added feature"
- Keep first line under 72 characters
- Add detailed description in body if needed

## File Organization

```
project/
├── app.py              # Main application
├── modules/           # Python modules
│   ├── parser.py
│   ├── ranking.py
│   └── statistics.py
├── templates/         # HTML templates
├── static/           # CSS, JS, images
└── tests/           # Test files (optional)
```

## Error Handling

- Use specific exception types
- Provide meaningful error messages
- Log errors for debugging

```python
try:
    result = parse_excel(file_path)
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    raise
except Exception as e:
    logger.error(f"Error parsing Excel: {e}")
    raise
```

## Testing

- Write unit tests for critical functions
- Test edge cases
- Ensure tests are self-contained

## Security

- Never commit sensitive data (API keys, passwords)
- Use environment variables for configuration
- Sanitize user input
