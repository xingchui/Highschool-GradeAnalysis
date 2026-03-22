# Grade Analysis Web Application

A web application for high school grade analysis that parses Excel files containing student exam scores, calculates rankings and statistics, and generates trend charts for individual students.

## Features

- Excel file upload and parsing (.xls and .xlsx formats)
- Student ranking (school and class level)
- 985/211/一本 line statistics analysis per class
- Single subject score line configuration (for Chinese, Math, English at 150 points)
- Individual student trend analysis (scores and rankings)
- Interactive charts using Plotly
- MIT License (open source)
- PEP 8 compliant code

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Running the Web Application

```bash
python run.py
```

Then open http://localhost:5000 in your browser.

### Running Tests

```bash
python -m pytest tests/ -v
```

### Building the .exe (Windows)

To build the executable:

```bash
pyinstaller --onefile --add-data "templates;templates" --add-data "config.json;." ^
    --hidden-import=flask --hidden-import=werkzeug --hidden-import=pandas ^
    --hidden-import=openpyxl --hidden-import=xlrd --hidden-import=plotly ^
    --name GradeAnalysisApp app.py
```

Or use the build script:

```bash
build.bat
```

## Project Structure

```
.
├── app.py                    # Flask main application
├── parser.py                 # Excel parser module
├── ranking.py                # Ranking engine
├── statistics.py             # Statistics analyzer
├── trend.py                 # Trend analysis module
├── charts.py                # Chart generation
├── config.json              # Configuration file (分数线设置)
├── requirements.txt          # Python dependencies
├── templates/               # HTML templates
├── static/                  # Static files
├── data/                    # Data files (uploaded Excel)
├── LICENSE                  # MIT License
├── CODE_STYLE.md           # Code style guidelines
├── build.bat               # Build script for .exe
└── app.spec               # PyInstaller spec file
```

## Configuration

The file `config.json` contains score line thresholds:

```json
{
  "lines": {
    "total": {"985": 580, "211": 540, "一本": 500},
    "chinese": {"985": 135.0, "211": 120.0, "一本": 105.0},
    "math": {"985": 135.0, "211": 120.0, "一本": 105.0},
    "english": {"985": 135.0, "211": 120.0, "一本": 105.0}
  }
}
```

You can modify these values in the web interface at `/config` or edit the JSON file directly.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Project Structure

```
.
├── run.py                    # Application entry point
├── app/                      # Application package
│   ├── __init__.py          # App factory (create_app)
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Flask extensions
│   ├── core/                # Core services
│   │   ├── data_service.py  # Session-bound data management
│   │   └── grade_service.py # Grade analysis service layer
│   └── routes/              # Blueprint routes
│       ├── main.py          # Main page routes
│       └── api.py           # API endpoints
├── parser.py                 # Excel parser module
├── ranking.py                # Ranking engine
├── statistics.py             # Statistics analyzer
├── trend.py                  # Trend analysis module
├── charts.py                 # Chart generation
├── config.json              # Configuration file (分数线设置)
├── requirements.txt         # Python dependencies
├── templates/               # HTML templates (Jinja2)
│   ├── base.html            # Base template
│   ├── index.html           # Upload page
│   ├── dashboard.html       # Overview dashboard
│   ├── rankings.html        # Student rankings
│   ├── statistics.html      # Statistics analysis
│   ├── trend.html           # Trend analysis
│   ├── config.html          # Settings page
│   ├── student.html         # Individual student view
│   └── about.html           # About page
├── tests/                    # Unit tests
│   ├── conftest.py          # pytest fixtures
│   └── test_data_service.py # Data service tests
├── data/                     # Uploaded Excel files
├── static/                   # Static assets
├── LICENSE                   # MIT License
└── README.md                # This file
```