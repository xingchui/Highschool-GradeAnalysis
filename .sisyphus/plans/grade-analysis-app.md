# 高中学生成绩分析网页应用 - 工作计划

## TL;DR

> **Quick Summary**: Build a web application for high school grade analysis that parses Excel files containing student exam scores, calculates rankings and statistics, and generates trend charts for individual students. Code follows MIT License, includes code规范, and can be packaged as .exe for deployment.

> **Deliverables**:
> - Flask web application with file upload and Excel parsing
> - Student ranking system (school and class level)
> - 985/211/一本 line statistics analysis per class
> - Individual student trend analysis (scores and rankings)
> - Interactive charts using Plotly
> - MIT License (open source)
> - Code规范 (PEP 8, style guide)
> - .exe packaging for Windows deployment

> **Estimated Effort**: Large
> **Parallel Execution**: YES - Multiple waves
> **Critical Path**: Excel Parser → Ranking Engine → Web UI → Trend Analysis → Packaging

---

## Context

### Original Request
Generate a high school student grade analysis web application. Handle 40 classes per grade, ~4000 students per grade. Features include:
1. Student ranking (school and class) for total scores and individual subjects
2. 985/211/一本 line statistics per class
3. Multiple exam upload and individual student trend analysis
4. Code follows MIT License (open source)
5.配套代码规范 (code style guidelines)
6. Package application as executable (.exe) for deployment on other computers

### Interview Summary
**Key Discussions**:
- Excel file structure with 2 sheets (26, 27), each containing student data for a class
- Column structure: 32 columns including student info, total scores, individual subject scores, and rankings
- Subjects: Chinese, Math, English (150 points each), Physics (100 points), Chemistry/Biology (100 points each, raw + scaled)

**Research Findings**:
- Excel file: `高二期末赋分.xls` with 2 sheets, 32 columns, student data for classes 2726 and 2727
- No existing web infrastructure
- Python packages available: Flask, FastAPI, Streamlit, pandas, plotly

### Metis Review
**Identified Gaps** (addressed):
- Excel file structure fully mapped
- Web framework decision pending (Flask vs Streamlit)
- Subject choice logic (Physics vs History, 4-subject choice) not fully addressed in Excel data

### 可复用资源 (Reusable Resources)

**开源项目借鉴**:
- **lvah/StudentScoreAnalyze** (GitHub, 24 stars): 基于Flask的学生成绩分析系统
  - 可借鉴: 项目结构、文件上传处理、成绩分析逻辑
  - 地址: https://github.com/lvah/StudentScoreAnalyze
- **ECJTU_AI**: 华东交通大学成绩查询与分析系统
  - 可借鉴: 成绩趋势分析、可视化展示
  - 地址: https://github.com/bestxiangest/ECJTU_AI

**Excel处理库**:
- **OpenPyXL**: 功能强大的Excel读写库（支持.xlsx格式）
  - 安装: `pip install openpyxl`
  - 用途: 读取和写入Excel文件
- **pandas**: 数据处理标准库
  - 安装: `pip install pandas`
  - 用途: 数据清洗、分析、排名计算
- **xlrd**: 老版本Excel (.xls) 读取库
  - 安装: `pip install xlrd`
  - 用途: 读取.xls格式文件

**打包方案对比**:

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **PyInstaller** (推荐) | 简单易用、打包体积小(50-100MB)、启动快、Python原生 | 跨平台需单独打包、代码可能被反编译 | ⭐⭐⭐⭐⭐ |
| **Electron** | 跨平台统一、Web技术栈、原生体验好 | 打包体积大(120-200MB)、内存占用高、开发复杂 | ⭐⭐⭐ |

**推荐理由**:
- 项目已是Flask Web应用，PyInstaller打包最直接
- 目标用户是学校教师，不需要复杂UI体验
- 打包体积小，分发方便
- 开发和维护成本低

**PyInstaller打包最佳实践**:
- Flask项目打包成单个exe文件
- 处理静态资源和模板文件: `--add-data="templates;templates"`
- 解决常见打包问题: 隐藏导入、资源文件缺失
- 参考文章: Flask项目一键打包实战（博客园）

---

## Work Objectives

### Core Objective
Build a web application that can parse Excel files containing student exam scores, calculate rankings and statistics, and generate trend charts for individual students.

### Concrete Deliverables
1. Flask web application with file upload interface
2. Excel parser module (handles .xls format)
3. Ranking engine (school and class level)
4. Statistics analyzer (985/211/一本 line calculations with 单科分数线)
5. Trend analysis module (student performance over time)
6. Interactive charts using Plotly
7. MIT License (LICENSE file)
8. Code规范文档 (CODE_STYLE.md)
9. PyInstaller configuration for .exe packaging
10. User guide for running the .exe

### 单科分数线设置
- **语数外**: 总分150分，可能出现小数分（小数点后一位）
- **三科三条线**: 985线、211线、一本线（可配置）
- **配置方式**: 通过配置文件或Web界面设置
- **默认值**: 
  - 985线: 135分（90%）
  - 211线: 120分（80%）
  - 一本线: 105分（70%）

### Definition of Done
- [ ] Web application runs on localhost:5000
- [ ] Excel file upload works correctly
- [ ] Student rankings calculated correctly
- [ ] Statistics analysis shows correct line counts and rates
- [ ] Trend charts display correctly for individual students
- [ ] MIT License file created
- [ ] Code规范文档 created
- [ ] .exe file generated and tested on another computer
- [ ] User guide created for .exe usage

### Must Have
- Excel file upload and parsing
- Student ranking (school and class)
- 985/211/一本 line statistics per class
- Individual student trend analysis
- Interactive charts
- MIT License (open source)
- Code规范 (PEP 8 compliance)
- .exe packaging for Windows deployment

### Must NOT Have (Guardrails)
- No user authentication (simple access)
- No database persistence (in-memory processing only)
- No support for Physics vs History choice (Excel only shows Physics)
- No support for 4-subject choice beyond Chemistry/Biology (Excel only shows these)

---

## Verification Strategy

> **UNIVERSAL RULE: ZERO HUMAN INTERVENTION**
>
> ALL tasks in this plan MUST be verifiable WITHOUT any human action.

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: NO (focus on agent-executed QA scenarios)
- **Framework**: Python (Flask/Streamlit) + pandas + plotly

### Agent-Executed QA Scenarios (MANDATORY — ALL tasks)

**Verification Tool by Deliverable Type**:
- **Frontend/UI**: Playwright (navigate, interact, assert DOM, screenshot)
- **API/Backend**: Bash (curl/httpie for API requests)
- **Data Processing**: Bash (Python scripts to verify calculations)

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: Set up project structure and dependencies
├── Task 2: Create Excel parser module
└── Task 9: Create MIT License and code规范文档

Wave 2 (After Wave 1):
├── Task 3: Implement ranking engine
├── Task 4: Implement statistics analyzer (with 单科分数线设置)
└── Task 5: Create web application framework (with 配置文件系统)

Wave 3 (After Wave 2):
├── Task 6: Implement trend analysis module
├── Task 7: Create interactive charts with Plotly
└── Task 8: Integration and testing

Wave 4 (After Wave 3):
├── Task 10: Configure PyInstaller for .exe packaging
├── Task 11: Build and test .exe file
└── Task 12: Create user guide for .exe usage
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 (Setup) | None | 2, 3, 4, 5 | 9 |
| 2 (Parser) | 1 | 3, 4, 5, 6 | 9 |
| 3 (Ranking) | 2 | 8 | 4, 5 |
| 4 (Statistics) | 2 | 8 | 3, 5 |
| 5 (Web UI) | 2 | 6, 7, 8 | 3, 4 |
| 6 (Trend) | 5 | 8 | 7 |
| 7 (Charts) | 5 | 8 | 6 |
| 8 (Integration) | 3, 4, 5, 6, 7 | 10, 11, 12 | None |
| 9 (License/规范) | None | None | 1, 2 |
| 10 (PyInstaller) | 8 | 11 | None |
| 11 (Build exe) | 10 | 12 | None |
| 12 (User guide) | 11 | None | None |

---

## TODOs

### Task 9: Create MIT License and code规范文档 (Parallel with Task 1)

**What to do**:
- Create LICENSE file with MIT License text
- Create CODE_STYLE.md with code规范 guidelines
- Configure linting tools (flake8, black for Python)

**Must NOT do**:
- No proprietary licenses
- No complex code规范 (keep it simple and practical)

**Recommended Agent Profile**:
- **Category**: `writing`
  - Reason: Documentation and license creation task
- **Skills**: [`documentation`, `python`]
  - `documentation`: For writing license and style guide
  - `python`: For linting configuration

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1 (with Tasks 1, 2)
- **Blocks**: None
- **Blocked By**: None (can start immediately)

**References**:
- MIT License template: https://opensource.org/licenses/MIT
- PEP 8: https://www.python.org/dev/peps/pep-0008/

**Acceptance Criteria**:
- [ ] LICENSE file created with MIT License text
- [ ] CODE_STYLE.md created with code规范 guidelines
- [ ] flake8 and black configured in project

**Agent-Executed QA Scenarios**:

```
Scenario: Verify LICENSE file exists and contains MIT text
  Tool: Bash (cat)
  Steps:
    1. Run: cat LICENSE
    2. Verify: Contains "MIT License" and permission text
  Expected Result: LICENSE file with correct MIT License
  Evidence: File content output

Scenario: Verify CODE_STYLE.md exists
  Tool: Bash (ls)
  Steps:
    1. Run: ls -la CODE_STYLE.md
    2. Verify: File exists and is readable
  Expected Result: Code规范文档 exists
  Evidence: Directory listing
```

---

### Task 1: Set up project structure and dependencies

**What to do**:
- Create project directory structure
- Install required Python packages (Flask, pandas, openpyxl, xlrd, plotly, pyinstaller)
- Create basic Flask application structure
-借鉴 lvah/StudentScoreAnalyze 项目结构

**Must NOT do**:
- No complex setup or configuration
- No database setup (use in-memory only)

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: Simple project setup task
- **Skills**: [`python`, `flask`]
  - `python`: For package installation and environment setup
  - `flask`: For basic Flask application structure

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 1 (Sequential)
- **Blocks**: Tasks 2, 3, 4, 5
- **Blocked By**: None (can start immediately)

**References**:
- Python package installation: Use `pip install flask pandas openpyxl xlrd plotly pyinstaller`
- Flask basic structure: `app.py` with routes for upload and analysis
-借鉴 lvah/StudentScoreAnalyze 项目结构: https://github.com/lvah/StudentScoreAnalyze

**Acceptance Criteria**:
- [ ] Project directory created with subdirectories: `templates/`, `static/`, `data/`
- [ ] Required packages installed successfully
- [ ] Basic Flask app runs on localhost:5000
- [ ]借鉴开源项目结构合理

**Agent-Executed QA Scenarios**:

```
Scenario: Verify Flask app starts successfully
  Tool: Bash (Python)
  Preconditions: All packages installed
  Steps:
    1. Run: python app.py
    2. Wait for "Running on http://localhost:5000"
    3. Check process is running
  Expected Result: Flask app starts without errors
  Evidence: Terminal output captured

Scenario: Verify directory structure exists
  Tool: Bash (ls)
  Steps:
    1. Run: ls -la
    2. Verify: templates/, static/, data/ directories exist
  Expected Result: All required directories present
  Evidence: Directory listing output
```

---

### Task 2: Create Excel parser module

**What to do**:
- Create `parser.py` module to read Excel files
- Handle .xls format using xlrd/openpyxl
- Extract student data, scores, and rankings
- Parse column structure based on identified format

**Must NOT do**:
- No modification of original Excel files
- No support for other Excel formats (only .xls)

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Data processing task requiring understanding of Excel structure
- **Skills**: [`python`, `pandas`]
  - `python`: For Python module creation
  - `pandas`: For Excel data processing

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 1 (Sequential)
- **Blocks**: Tasks 3, 4, 5, 6
- **Blocked By**: Task 1

**References**:
- Excel structure from draft file: `.sisyphus/drafts/grade-analysis-app.md`
- Column mapping: 32 columns with student info, scores, rankings

**Acceptance Criteria**:
- [ ] `parser.py` module created
- [ ] Can read `高二期末赋分.xls` successfully
- [ ] Returns structured data (DataFrame with student records)
- [ ] Handles both sheets (26, 27)

**Agent-Executed QA Scenarios**:

```
Scenario: Parse Excel file successfully
  Tool: Bash (Python)
  Preconditions: Excel file exists at E:\op\op8\高二期末赋分.xls
  Steps:
    1. Run: python -c "from parser import parse_excel; df = parse_excel('E:/op/op8/高二期末赋分.xls'); print(len(df))"
    2. Verify: Output shows row count > 0
    3. Verify: DataFrame has expected columns
  Expected Result: Excel parsed successfully with student data
  Evidence: Python output showing row count and column names
```

---

### Task 3: Implement ranking engine

**What to do**:
- Create `ranking.py` module
- Calculate school-level rankings for total scores and individual subjects
- Calculate class-level rankings for total scores and individual subjects
- Return ranking data structure

**Must NOT do**:
- No database storage (use in-memory calculations)
- No complex ranking algorithms (use pandas rank() function)

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Data processing task requiring ranking calculations
- **Skills**: [`python`, `pandas`]
  - `python`: For Python module creation
  - `pandas`: For ranking calculations

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 2 (with Tasks 4, 5)
- **Blocks**: Task 8
- **Blocked By**: Task 2

**References**:
- Excel structure: Total scores, individual subject scores with existing rankings
- Ranking calculation: Use pandas `groupby()` and `rank()` functions

**Acceptance Criteria**:
- [ ] `ranking.py` module created
- [ ] School rankings calculated correctly
- [ ] Class rankings calculated correctly
- [ ] Rankings match existing Excel rankings

**Agent-Executed QA Scenarios**:

```
Scenario: Verify ranking calculations
  Tool: Bash (Python)
  Preconditions: parser.py module exists, Excel file parsed
  Steps:
    1. Run: python -c "from parser import parse_excel; from ranking import calculate_rankings; df = parse_excel('E:/op/op8/高二期末赋分.xls'); rankings = calculate_rankings(df); print(rankings.head())"
    2. Verify: Rankings calculated for each student
    3. Compare: Rankings match Excel file values
  Expected Result: Rankings calculated correctly
  Evidence: Python output showing ranking data
```

---

### Task 4: Implement statistics analyzer

**What to do**:
- Create `statistics.py` module
- Calculate 985/211/一本 line statistics per class
- Calculate line counts and上线 rates
- **Implement 单科分数线设置功能**:
  - 语数外: 总分150分，可能出现小数分（小数点后一位）
  - 三科三条线: 985线、211线、一本线（可配置）
  - 配置方式: 通过配置文件或Web界面设置
  - 默认值: 985线135分、211线120分、一本线105分
- Return statistics data structure

**Must NOT do**:
- No hardcoded line thresholds (use configurable values)
- No complex statistical calculations (simple counts and rates)

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Data processing task requiring statistics calculations
- **Skills**: [`python`, `pandas`]
  - `python`: For Python module creation
  - `pandas`: For statistics calculations

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 2 (with Tasks 3, 5)
- **Blocks**: Task 8
- **Blocked By**: Task 2

**References**:
- Excel structure: Total scores (raw and scaled)
- Line thresholds: Configurable (985, 211, 一本)
- 单科分数线: 语数外150分制，支持小数点后一位

**Acceptance Criteria**:
- [ ] `statistics.py` module created
- [ ] 985/211/一本 line counts calculated correctly
- [ ] 上线 rates calculated correctly
- [ ] Statistics can be grouped by class
- [ ] 单科分数线设置功能实现
- [ ] 配置文件或Web界面支持分数线修改

**Agent-Executed QA Scenarios**:

```
Scenario: Verify statistics calculations
  Tool: Bash (Python)
  Preconditions: parser.py module exists, Excel file parsed
  Steps:
    1. Run: python -c "from parser import parse_excel; from statistics import calculate_statistics; df = parse_excel('E:/op/op8/高二期末赋分.xls'); stats = calculate_statistics(df); print(stats)"
    2. Verify: Statistics calculated for each class
    3. Verify: Line counts and rates are reasonable
  Expected Result: Statistics calculated correctly
  Evidence: Python output showing statistics data

Scenario: Verify 单科分数线设置功能
  Tool: Bash (Python)
  Preconditions: statistics.py module exists with 配置功能
  Steps:
    1. Run: python -c "from statistics import load_config, save_config; config = load_config(); print(config['lines'])"
    2. Verify: Default lines are 985:135, 211:120, 一本:105
    3. Modify config and verify changes
  Expected Result: 配置文件支持分数线修改
  Evidence: Config file content
```

---

### Task 5: Create web application framework

**What to do**:
- Create Flask application with routes for:
  - File upload
  - Student ranking display
  - Statistics display (including 单科分数线设置)
  - Trend analysis display
- Create HTML templates for each page
- Create CSS for styling
- **Create 配置文件系统**:
  - `config.json`: 分数线配置文件
  - Web界面支持修改分数线
  - 默认值: 985线135分、211线120分、一本线105分

**Must NOT do**:
- No complex authentication
- No database integration

**Recommended Agent Profile**:
- **Category**: `visual-engineering`
  - Reason: Frontend UI/UX task
- **Skills**: [`flask`, `html`, `css`]
  - `flask`: For Flask routes and templates
  - `html`: For template creation
  - `css`: For styling

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 2 (with Tasks 3, 4)
- **Blocks**: Tasks 6, 7, 8
- **Blocked By**: Task 2

**References**:
- Flask documentation: https://flask.palletsprojects.com/
- HTML templates: Use Jinja2 templating
- 配置文件示例:
```json
{
  "lines": {
    "985": 135.0,
    "211": 120.0,
    "一本": 105.0
  },
  "subjects": {
    "chinese": 150.0,
    "math": 150.0,
    "english": 150.0
  }
}
```

**Acceptance Criteria**:
- [ ] Flask routes created for all features
- [ ] HTML templates created for each page
- [ ] File upload functionality works
- [ ] Web application runs on localhost:5000
- [ ] 配置文件系统创建
- [ ] Web界面支持分数线修改

**Agent-Executed QA Scenarios**:

```
Scenario: Verify web application routes
  Tool: Playwright
  Preconditions: Flask app running on localhost:5000
  Steps:
    1. Navigate to: http://localhost:5000
    2. Verify: Home page loads
    3. Navigate to: /upload
    4. Verify: Upload page loads
  Expected Result: All routes accessible
  Evidence: Screenshots of each page

Scenario: Verify 配置文件系统
  Tool: Bash (cat)
  Preconditions: config.json created
  Steps:
    1. Run: cat config.json
    2. Verify: Contains lines configuration
    3. Verify: Default values are correct
  Expected Result: 配置文件格式正确
  Evidence: Config file content
```

---

### Task 6: Implement trend analysis module

**What to do**:
- Create `trend.py` module
- Handle multiple exam uploads
- Calculate student performance trends over time
- Calculate ranking changes over time
- Return trend data structure

**Must NOT do**:
- No complex time series analysis (simple line charts)
- No storage of historical data (in-memory only)

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Data processing task requiring trend calculations
- **Skills**: [`python`, `pandas`]
  - `python`: For Python module creation
  - `pandas`: For trend calculations

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 3 (with Task 7)
- **Blocks**: Task 8
- **Blocked By**: Task 5

**References**:
- Excel structure: Multiple sheets for different exams
- Trend calculation: Group by student ID and calculate changes

**Acceptance Criteria**:
- [ ] `trend.py` module created
- [ ] Multiple exam uploads supported
- [ ] Student performance trends calculated correctly
- [ ] Ranking changes calculated correctly

**Agent-Executed QA Scenarios**:

```
Scenario: Verify trend analysis
  Tool: Bash (Python)
  Preconditions: parser.py module exists, multiple Excel files uploaded
  Steps:
    1. Run: python -c "from parser import parse_excel; from trend import calculate_trends; df1 = parse_excel('exam1.xls'); df2 = parse_excel('exam2.xls'); trends = calculate_trends([df1, df2]); print(trends.head())"
    2. Verify: Trends calculated for each student
    3. Verify: Score changes and ranking changes calculated
  Expected Result: Trends calculated correctly
  Evidence: Python output showing trend data
```

---

### Task 7: Create interactive charts with Plotly

**What to do**:
- Create `charts.py` module
- Generate interactive charts for student trends
- Generate charts for statistics visualization
- Integrate charts into web application

**Must NOT do**:
- No static charts (must be interactive)
- No complex chart types (line charts and bar charts only)

**Recommended Agent Profile**:
- **Category**: `visual-engineering`
  - Reason: Visualization task
- **Skills**: [`plotly`, `python`]
  - `plotly`: For interactive charts
  - `python`: For chart generation

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 3 (with Task 6)
- **Blocks**: Task 8
- **Blocked By**: Task 5

**References**:
- Plotly documentation: https://plotly.com/python/
- Chart types: Line charts for trends, bar charts for statistics

**Acceptance Criteria**:
- [ ] `charts.py` module created
- [ ] Interactive charts generated successfully
- [ ] Charts integrated into web application
- [ ] Charts display correctly in browser

**Agent-Executed QA Scenarios**:

```
Scenario: Verify chart generation
  Tool: Playwright
  Preconditions: Web application running, trend data available
  Steps:
    1. Navigate to: http://localhost:5000/trends
    2. Verify: Interactive chart loads
    3. Interact: Hover over chart points
    4. Verify: Tooltips show correct data
  Expected Result: Interactive charts work correctly
  Evidence: Screenshots of charts with tooltips
```

---

### Task 8: Integration and testing

**What to do**:
- Integrate all modules into web application
- Perform end-to-end testing
- Fix any bugs or issues
- Deploy application (local deployment)

**Must NOT do**:
- No production deployment (local only)
- No complex testing framework (simple manual tests)

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Integration task requiring all modules
- **Skills**: [`python`, `flask`, `testing`]
  - `python`: For integration code
  - `flask`: For web application integration
  - `testing`: For end-to-end testing

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 3 (Final)
- **Blocks**: 10, 11, 12
- **Blocked By**: Tasks 3, 4, 5, 6, 7

**References**:
- Integration points: All modules (parser, ranking, statistics, trend, charts)
- Testing approach: End-to-end testing of all features

**Acceptance Criteria**:
- [ ] All modules integrated successfully
- [ ] End-to-end testing completed
- [ ] All features working correctly
- [ ] Application runs on localhost:5000

**Agent-Executed QA Scenarios**:

```
Scenario: End-to-end test of all features
  Tool: Playwright
  Preconditions: Web application running with all features
  Steps:
    1. Upload Excel file
    2. View student rankings
    3. View statistics analysis
    4. View trend analysis for individual student
    5. Verify all charts display correctly
  Expected Result: All features work end-to-end
  Evidence: Screenshots of each feature
```

---

### Task 10: Configure PyInstaller for .exe packaging

**What to do**:
- Install PyInstaller
- Create PyInstaller spec file or command
- Configure for Flask application
- Handle data files and templates

**Must NOT do**:
- No complex packaging options (keep it simple)
- No obfuscation or protection (open source)

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Packaging task requiring PyInstaller knowledge
- **Skills**: [`python`, `packaging`]
  - `python`: For PyInstaller configuration
  - `packaging`: For .exe packaging

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 4
- **Blocks**: 11
- **Blocked By**: Task 8

**References**:
- PyInstaller documentation: https://pyinstaller.org/en/stable/
- Flask packaging examples: https://pyinstaller.org/en/stable/usage.html

**Acceptance Criteria**:
- [ ] PyInstaller installed
- [ ] Spec file or command created
- [ ] Flask app configured for packaging
- [ ] Data files and templates included

**Agent-Executed QA Scenarios**:

```
Scenario: Verify PyInstaller configuration
  Tool: Bash (Python)
  Preconditions: PyInstaller installed
  Steps:
    1. Run: pyinstaller --version
    2. Verify: PyInstaller is installed
    3. Run: pyinstaller --help | grep "onefile"
    4. Verify: --onefile option available
  Expected Result: PyInstaller configured correctly
  Evidence: Command output
```

---

### Task 11: Build and test .exe file

**What to do**:
- Build .exe file using PyInstaller
- Test .exe file on local machine
- Test .exe file on another computer (if available)
- Fix any packaging issues

**Must NOT do**:
- No code changes during packaging (fix issues in source code)

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Packaging task requiring build and test
- **Skills**: [`python`, `packaging`, `testing`]
  - `python`: For build process
  - `packaging`: For .exe generation
  - `testing`: For .exe testing

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 4
- **Blocks**: 12
- **Blocked By**: Task 10

**References**:
- PyInstaller build command: `pyinstaller --onefile --windowed app.py`
- Testing approach: Run .exe and verify functionality

**Acceptance Criteria**:
- [ ] .exe file built successfully
- [ ] .exe file runs on local machine
- [ ] All features work in .exe version
- [ ] .exe file size is reasonable (< 100MB)

**Agent-Executed QA Scenarios**:

```
Scenario: Verify .exe file runs successfully
  Tool: Bash (execute .exe)
  Preconditions: .exe file built at dist/app.exe
  Steps:
    1. Run: ./dist/app.exe --help
    2. Verify: Application starts without errors
    3. Check: Process is running
  Expected Result: .exe file runs correctly
  Evidence: Terminal output and process listing
```

---

### Task 12: Create user guide for .exe usage

**What to do**:
- Create README.md with .exe usage instructions
- Create user guide for running the application
- Include troubleshooting tips

**Must NOT do**:
- No complex documentation (keep it simple)

**Recommended Agent Profile**:
- **Category**: `writing`
  - Reason: Documentation task
- **Skills**: [`documentation`]
  - `documentation`: For writing user guide

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 4 (Final)
- **Blocks**: None
- **Blocked By**: Task 11

**References**:
- README template: https://gist.github.com/PurpleBooth/109311bb0361f42d87bb
- User guide examples

**Acceptance Criteria**:
- [ ] README.md created with .exe usage instructions
- [ ] User guide includes installation and running steps
- [ ] Troubleshooting tips included

**Agent-Executed QA Scenarios**:

```
Scenario: Verify README.md exists and contains usage instructions
  Tool: Bash (cat)
  Steps:
    1. Run: cat README.md
    2. Verify: Contains .exe usage instructions
    3. Verify: Contains installation steps
  Expected Result: README.md with complete user guide
  Evidence: File content output
```

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `feat: Initial project setup` | `app.py`, `requirements.txt` | `python app.py` |
| 9 | `docs: Add MIT License and code规范` | `LICENSE`, `CODE_STYLE.md` | `cat LICENSE` |
| 2 | `feat: Excel parser module` | `parser.py` | `python -c "from parser import parse_excel; ..."` |
| 3 | `feat: Ranking engine` | `ranking.py` | `python -c "from ranking import calculate_rankings; ..."` |
| 4 | `feat: Statistics analyzer` | `statistics.py` | `python -c "from statistics import calculate_statistics; ..."` |
| 5 | `feat: Web application framework` | `templates/*`, `static/*` | `python app.py` + browser test |
| 6 | `feat: Trend analysis module` | `trend.py` | `python -c "from trend import calculate_trends; ..."` |
| 7 | `feat: Interactive charts` | `charts.py` | Browser test |
| 8 | `feat: Integration and testing` | All files | End-to-end test |
| 10 | `build: Configure PyInstaller` | `pyinstaller.spec` or command | `pyinstaller --version` |
| 11 | `build: Build .exe file` | `dist/app.exe` | `./dist/app.exe --help` |
| 12 | `docs: Add user guide` | `README.md` | `cat README.md` |

---

## Success Criteria

### Verification Commands
```bash
# Task 1: Setup
python app.py  # Should start Flask server

# Task 2: Parser
python -c "from parser import parse_excel; df = parse_excel('E:/op/op8/高二期末赋分.xls'); print(f'Parsed {len(df)} students')"

# Task 3: Ranking
python -c "from ranking import calculate_rankings; rankings = calculate_rankings(df); print('Rankings calculated')"

# Task 4: Statistics
python -c "from statistics import calculate_statistics; stats = calculate_statistics(df); print('Statistics calculated')"

# Task 5-8: Integration
# Upload Excel file via web interface
# Verify rankings, statistics, trends display correctly
```

### Final Checklist
- [ ] All "Must Have" features implemented
- [ ] All "Must NOT Have" items excluded
- [ ] Excel file upload works
- [ ] Student rankings calculated correctly
- [ ] Statistics analysis shows correct line counts and rates
- [ ] Trend charts display correctly
- [ ] Web application runs on localhost:5000
- [ ] MIT License file created and correct
- [ ] Code规范文档 created and followed
- [ ] .exe file built and tested
- [ ] User guide created and complete