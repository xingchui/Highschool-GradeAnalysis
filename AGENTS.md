# AGENTS.md - 高中成绩分析系统 v3.0.0

> **Project Type**: Python Flask Web Application for High School Grade Analysis
> **License**: MIT
> **UI Language**: 中文 (Chinese)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app (entry point is run.py, NOT app.py)
python run.py
# Access at http://localhost:5000

# Alternative: run app.py directly (legacy single-file mode)
python app.py
```

## Build Commands

```bash
<<<<<<< HEAD
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
=======
# Build Windows executable (Windows only)
build.bat
# Output: dist\GradeAnalysisApp.exe

# Or manually:
pyinstaller --onefile --name GradeAnalysisApp ^
    --add-data "templates;templates" --add-data "config.json;." ^
    --hidden-import=app --hidden-import=app.core --hidden-import=app.routes ^
    run.py
```

## Architecture Overview

The project has **two entry points** with different architectures:

| Entry | Architecture | Status |
|-------|-------------|--------|
| `run.py` → `app/` | Application factory pattern (Blueprints, DataService, GradeService) | **Current/Primary** |
| `app.py` | Monolithic Flask app with global `loaded_files` dict | Legacy, still functional |

### Module Structure

```
E:\op\op8\
├── run.py                    # Primary entry point (uses app factory)
├── app.py                    # Legacy single-file Flask app
├── app/                      # Application factory package
│   ├── __init__.py          # create_app() factory
│   ├── config.py            # Config classes (Development/Production)
│   ├── extensions.py        # Flask extensions init
│   ├── core/
│   │   ├── data_service.py  # Session-bound data management
│   │   └── grade_service.py # Grade analysis service layer
│   └── routes/
│       ├── __init__.py      # Blueprint registration
│       ├── main.py          # Main page blueprints
│       └── api.py           # API endpoints
├── parser.py                 # Excel parsing (3 formats: new/liberal/old)
├── ranking.py                # Student ranking calculations
├── grade_statistics.py       # 985/211/一本 statistics (NOT statistics.py)
├── trend.py                  # Student progress tracking
├── charts.py                 # Plotly chart generation
├── config.json               # Score line thresholds + subject max scores
├── templates/                # Jinja2 HTML templates
└── data/                     # Uploaded Excel files (gitignored)
```

## Excel Parsing (parser.py) - Critical

### Column Name Convention
Parser converts **Chinese headers → English canonical names**. All downstream modules expect English column names:

| Chinese Header | Canonical Name |
|---------------|----------------|
| 班级 | class_id (string) |
| 姓名 | name |
| 学号 | student_id |
| 考号 | exam_id |
| 总分(原始分) | total_raw |
| 总分(赋分) | total_scaled |
| 语文 | chinese |
| 数学 | math |
| 英语 | english |
| 物理 | physics |
| 化学 | chemistry / chemistry_raw |
| 生物 | biology / biology_raw |
| 地理 | geography / geography_raw |
| 政治 | politics / politics_scaled |

### Format Detection
By column count: **≥60 = 新格式**, **50-59 = 文科**, **<50 = 旧格式**

### Key Functions
- `parse_excel(file_path, sheet_name=None)` - Parse single sheet
- `parse_all_sheets(file_path)` - Returns dict of sheet_name → DataFrame
- `get_student_by_id(df, student_id)` - Find student by ID
- `get_students_by_class(df, class_id)` - Filter by class

### Common Pitfalls
- **Multi-header Excel files**: `_parse_xlsx()` uses only the **first** detected header row. If headers span two rows, only the first is used.
- **class_id is string**: Never treat as int. Convert with `str(int(float(x)))` to strip `.0` suffix.
- **NaN ranks**: Use `pd.to_numeric(df[col], errors='coerce')` for safe conversion.
- **Duplicate column names**: Parser deduplicates via `target_assigned` set.
- **"Unnamed" columns**: Automatically dropped after parsing.

## Data Flow

1. User uploads Excel → saved to `data/` with UUID suffix
2. `parser.parse_all_sheets()` → dict of DataFrames → `pd.concat()` → single DataFrame
3. Stored in-memory (global `loaded_files` in app.py, `DataService` in app/ package)
4. All downstream modules (`ranking.py`, `grade_statistics.py`, `trend.py`) operate on the canonical DataFrame

## Important Notes

- **In-memory storage**: Data lost on server restart
- **config.json**: Score thresholds modifiable via `/config` UI. Contains both lines (985/211/yiben) and subject max scores.
- **Trend analysis**: Lazy-loads exam data via `trend.load_exam_data()` on first request
- **PyInstaller**: Bundled exe reads templates/config from `sys._MEIPASS`
- **No tests in requirements.txt**: pytest mentioned in README but not pinned
>>>>>>> e26772c (release: v3.0.0)

## Adding New Excel Format

<<<<<<< HEAD
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
=======
1. Update `detect_excel_format()` with new column count threshold
2. Create `_clean_xxx_format(df)` with column mapping
3. Add branch in `_clean_dataframe()` dispatcher
4. Define numeric columns list for type conversion
>>>>>>> e26772c (release: v3.0.0)
