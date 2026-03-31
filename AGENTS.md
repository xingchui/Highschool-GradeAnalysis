# AGENTS.md - Grade Analysis Web Application

> **Project Type**: Python Flask Web Application for High School Grade Analysis  
> **Version**: 2.0.0 (Application Factory Architecture)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with new architecture (recommended)
python run.py

# Run with legacy architecture (still supported)
python app.py

# Access at http://localhost:5000
```

## Build/Test/Lint Commands

```bash
# Run the web server
python run.py                           # New architecture
python app.py                           # Legacy architecture

# Run all tests
python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/test_data_service.py -v

# Run a single test
python -m pytest tests/test_data_service.py::TestDataService::test_load_file -v

# Lint code
flake8 app/ parser.py ranking.py statistics.py trend.py charts.py
black --check .

# Format code
black .

# Build Windows executable
build.bat
```

## Architecture Overview

### New Architecture (v2.0) — Recommended

```
app/
├── __init__.py          # create_app() factory
├── config.py            # Configuration classes
├── extensions.py        # Flask extensions init
├── core/
│   ├── data_service.py  # Session-bound data management
│   └── grade_service.py # Business logic (ranking/stats/trend)
├── routes/
│   ├── main.py          # Main page routes
│   └── api.py           # API endpoints
└── templates/
    ├── base.html        # Base template (inherit from this)
    └── ...
```

### Legacy Architecture (still functional)

```
app.py                   # Single-file Flask app
parser.py                # Excel parsing
ranking.py               # Ranking calculations
statistics.py            # Statistics analysis
trend.py                 # Trend analysis
charts.py                # Plotly charts
```

### Key Entry Points

| Command | Description |
|---------|-------------|
| `python run.py` | Start with new architecture (app factory + blueprints) |
| `python app.py` | Start with legacy architecture |
| `python -m pytest tests/ -v` | Run test suite |

## Code Style Guidelines

### Python Conventions
- **Indentation**: 4 spaces (no tabs)
- **Line length**: 100 characters max
- **Imports**: Standard lib → Third-party → Local (separated by blank lines)
- **Naming**: `snake_case` functions/vars, `PascalCase` classes
- **Type hints**: Required for public functions
- **Docstrings**: Google-style with Args/Returns/Raises

### Import Pattern
```python
# Standard library
import os
import json
from typing import Optional, Dict, List

# Third-party
import pandas as pd
from flask import Flask, render_template, request, jsonify

# Local modules
from app.core.data_service import DataService
from app.core.grade_service import GradeService
```

### Error Handling
- Use specific exceptions (FileNotFoundError, ValueError)
- Provide meaningful error messages in Chinese for user-facing errors
- Log errors with context using `app.logger`

### Data Processing Patterns
- Safe numeric conversion: `pd.to_numeric(df[col], errors='coerce')`
- Handle missing data: `df.dropna(subset=['name', 'class_id'])`
- Excel format detection by column count: ≥60=新格式, 50-59=文科, <50=旧格式

### Flask Patterns (New Architecture)
- Use application factory: `create_app()` in `app/__init__.py`
- Routes in Blueprints: `app/routes/main.py`, `app/routes/api.py`
- Session-bound data via `app.data_service` (not globals!)
- Configuration classes: `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`

### HTML Template Patterns
- **Always inherit from base.html**: `{% extends "base.html" %}`
- **Use tojson for JS data injection**: `var data = {{ value|tojson|safe }};`
- **Bootstrap 5 classes**: Use consistent card, row, col-* structure
- **XSS Prevention**: Never directly embed `{{ var }}` in `<script>` tags

## Module Responsibilities

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `app/core/data_service.py` | Session data management | `load_file()`, `get_current_data()`, `set_current_file()` |
| `app/core/grade_service.py` | Business logic | `calculate_rankings()`, `get_statistics()`, `compare_exams()` |
| `parser.py` | Excel parsing (3 formats) | `parse_excel()`, `parse_all_sheets()`, `detect_excel_format()` |
| `ranking.py` | Student rankings | `calculate_rankings()`, `get_top_students()` |
| `statistics.py` | 985/211/一本 analysis | `calculate_school_line_stats()`, `calculate_class_line_stats()` |
| `trend.py` | Progress tracking | `compare_two_exams()`, `get_student_trend()` |
| `charts.py` | Plotly visualization | `create_trend_chart()`, `create_distribution_chart()` |

## Important Notes

- **Session Isolation**: New architecture uses session-bound data (no cross-user contamination)
- **Chinese UI**: All user-facing strings are in Chinese (中文)
- **Excel Formats**: Parser auto-detects format by column count
- **Config**: Score thresholds in `config.json`, modifiable at `/config`
- **PyInstaller**: Use `build.bat` for Windows executable
- **License**: MIT

## Adding New Excel Format Support

```python
# In parser.py:
def detect_excel_format(df: pd.DataFrame) -> str:
    col_count = len(df.columns)
    if col_count >= 60:
        return 'new'      # 理科 (Science)
    elif col_count >= 50:
        return 'liberal'  # 文科 (Liberal Arts)
    elif col_count >= 40:  # ← Add new format here
        return 'custom'   # New format
    return 'old'          # 旧格式 (Legacy)
```

## Common Pitfalls

- Handle `NaN` values when comparing ranks
- Convert student IDs to string for comparison: `df['student_id'].astype(str)`
- Convert class IDs to string for filtering: `df['class_id'] == str(class_id)`
- Use `request.args.getlist()` for multi-select form fields
- **Never use globals** — use `app.data_service` in new architecture
- **Always use `tojson`** when passing data to JavaScript

## Testing

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run with coverage (if pytest-cov installed)
python -m pytest tests/ --cov=app --cov-report=term-missing

# Run specific test class
python -m pytest tests/test_data_service.py::TestDataService -v
```

### Test Fixtures (in tests/conftest.py)
- `app`: Flask application configured for testing
- `client`: Flask test client
- `sample_dataframe`: Sample student data DataFrame
- `data_service`: DataService with sample data loaded
