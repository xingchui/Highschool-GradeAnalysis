# AGENTS.md - Grade Analysis Web Application

> **Project Type**: Python Flask Web Application for High School Grade Analysis

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access at http://localhost:5000
```

## Build/Test/Lint Commands

```bash
# Run the web server (with auto-reload in development)
python app.py

# Build Windows executable
build.bat
# OR manually:
pyinstaller --onefile --add-data "templates;templates" --add-data "config.json;." --name GradeAnalysisApp app.py

# Lint code (optional)
flake8 app.py parser.py ranking.py statistics.py trend.py charts.py
black --check .

# Format code
black .

# Run a single module test
python -c "import parser; print(parser.parse_excel('data/test.xlsx'))"
python -c "import trend; trend.load_exam_data('data/test.xlsx', 'test')"
```

## Code Style Guidelines

### Python Conventions
- **Indentation**: 4 spaces (no tabs)
- **Line length**: 100 characters max
- **Imports**: Standard lib → Third-party → Local modules (separated by blank lines)
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Type hints**: Use where appropriate (function signatures)
- **Docstrings**: Google-style with Args/Returns/Raises sections

### Import Pattern
```python
# Standard library
import os
import json

# Third-party
import pandas as pd
from flask import Flask, render_template, request

# Local modules
import parser
import ranking
import statistics as stats_module
import trend as trend_module
```

### Error Handling
- Use specific exceptions (FileNotFoundError, ValueError)
- Provide meaningful error messages in Chinese for user-facing errors
- Log errors with context for debugging

### Data Processing Patterns
- Use `pd.to_numeric(df[col], errors='coerce')` for safe numeric conversion
- Handle missing data with `df.dropna(subset=['name', 'class_id'])`
- Detect file format by column count: ≥60=新格式, 50-59=文科, <50=旧格式

### Flask Patterns
- Routes defined in `app.py`
- Templates in `templates/` with Bootstrap 5 styling
- Data stored in global `loaded_files` dict (in-memory)
- File uploads saved to `data/` with UUID suffix

## Project Structure

```
.
├── app.py              # Flask routes and main application
├── parser.py           # Excel file parsing (多种格式支持)
├── ranking.py          # Student ranking calculations
├── statistics.py       # 985/211/一本 statistics analysis
├── trend.py            # Trend analysis for student progress
├── charts.py           # Plotly chart generation
├── config.json         # Score line thresholds configuration
├── requirements.txt    # Python dependencies
├── build.bat           # Windows build script
├── templates/          # Jinja2 HTML templates
│   ├── index.html      # Upload page
│   ├── dashboard.html  # Overview dashboard
│   ├── rankings.html   # Student rankings
│   ├── statistics.html # Score line statistics
│   ├── trend.html      # Trend analysis
│   ├── config.html     # Settings page
│   └── student.html    # Individual student view
├── data/               # Uploaded Excel files (gitignored)
└── static/             # Static assets (CSS, JS)
```

## Key Module Responsibilities

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `parser.py` | Parse Excel files (3 formats) | `parse_excel()`, `parse_all_sheets()`, `detect_excel_format()` |
| `ranking.py` | Calculate rankings | `calculate_rankings()`, `get_top_students()` |
| `statistics.py` | 985/211/一本 statistics | `calculate_school_line_stats()`, `calculate_class_line_stats()` |
| `trend.py` | Student progress tracking | `compare_two_exams()`, `get_student_trend()` |

## Important Notes

- **Excel Format Detection**: Parser auto-detects format by column count and structure
- **In-Memory Storage**: Data not persisted across server restarts
- **Chinese UI**: All user-facing strings are in Chinese (中文)
- **Config**: Score thresholds in `config.json`, modifiable via web UI at `/config`
- **License**: MIT

## Adding New Excel Format Support

To support a new Excel structure:

1. Add format detection in `detect_excel_format()` based on column count
2. Create `_clean_xxx_format(df)` function with column mapping
3. Add branch in `_clean_dataframe()` to call the new function
4. Define numeric columns list for type conversion

## Common Pitfalls

- Don't forget to handle `NaN` values when comparing ranks
- Student IDs may be int or string - convert to string for comparison
- Class IDs should be converted to string for filtering
- Use `request.args.getlist()` for multi-select form fields
