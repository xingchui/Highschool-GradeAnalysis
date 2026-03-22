# 高中成绩分析系统

一款用于高中成绩分析的Web应用程序，可以解析包含学生考试成绩的Excel文件，计算排名和统计数据，并为学生生成趋势图表。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 功能特性

- 📊 **Excel文件上传与解析** - 支持 .xls 和 .xlsx 格式
- 🏆 **学生排名** - 支持全校排名和班级排名
- 📈 **分数线统计分析** - 985/211/一本上线人数统计（按班级）
- ⚙️ **分数线配置** - 支持语数外（150分制）及各科目自定义分数线
- 📉 **成绩趋势分析** - 追踪学生成绩和排名变化趋势
- 📊 **交互式图表** - 使用Plotly生成可视化图表
- 🔒 **MIT许可证** - 开源免费使用
- ✅ **符合PEP 8代码规范**

## 📥 安装

### 方式一：直接运行exe（Windows）

从 [Releases](https://github.com/xingchui/Highschool-GradeAnalysis/releases) 下载最新的 `GradeAnalysisApp.exe`，双击运行即可。

### 方式二：源码运行

```bash
# 克隆仓库
git clone https://github.com/xingchui/Highschool-GradeAnalysis.git
cd Highschool-GradeAnalysis

# 安装依赖
pip install -r requirements.txt

# 运行应用
python run.py
```

然后在浏览器中访问 http://localhost:5000

## 🚀 使用方法

### 运行Web应用

```bash
python run.py
```

### 运行测试

```bash
python -m pytest tests/ -v
```

### 构建Windows可执行文件

```bash
# 使用构建脚本
build.bat

# 或手动使用PyInstaller
pyinstaller --onefile --add-data "templates;templates" --add-data "config.json;." ^
    --hidden-import=flask --hidden-import=werkzeug --hidden-import=pandas ^
    --hidden-import=openpyxl --hidden-import=xlrd --hidden-import=plotly ^
    --name GradeAnalysisApp run.py
```

## 📁 项目结构

```
.
├── run.py                      # 应用入口点
├── app/                        # 应用包
│   ├── __init__.py            # 应用工厂 (create_app)
│   ├── config.py              # 配置类
│   ├── extensions.py          # Flask扩展初始化
│   ├── core/                  # 核心服务
│   │   ├── data_service.py    # 会话绑定数据管理
│   │   └── grade_service.py   # 成绩分析服务层
│   └── routes/                # 蓝图路由
│       ├── main.py            # 主页面路由
│       └── api.py             # API接口
├── parser.py                   # Excel解析模块
├── ranking.py                  # 排名计算引擎
├── statistics.py               # 统计分析模块
├── trend.py                    # 趋势分析模块
├── charts.py                   # 图表生成模块
├── config.json                 # 配置文件（分数线设置）
├── requirements.txt            # Python依赖
├── templates/                  # HTML模板 (Jinja2)
│   ├── base.html              # 基础模板
│   ├── index.html             # 上传页面
│   ├── dashboard.html         # 数据概览
│   ├── rankings.html          # 学生排名
│   ├── statistics.html        # 统计分析
│   ├── trend.html             # 趋势分析
│   ├── config.html            # 设置页面
│   ├── student.html           # 学生详情
│   └── about.html             # 关于页面
├── tests/                      # 单元测试
│   ├── conftest.py            # pytest fixtures
│   └── test_data_service.py   # 数据服务测试
├── data/                       # 上传的Excel文件
├── static/                     # 静态资源
├── build.bat                   # Windows构建脚本
├── LICENSE                     # MIT许可证
└── README.md                   # 本文件
```

## ⚙️ 配置

`config.json` 文件包含分数线阈值配置：

```json
{
  "lines": {
    "total_raw": {"985": 600, "211": 550, "yiben": 500},
    "total_scaled": {"985": 600, "211": 550, "yiben": 500},
    "chinese": {"985": 120, "211": 110, "yiben": 105},
    "math": {"985": 120, "211": 110, "yiben": 105},
    "english": {"985": 120, "211": 110, "yiben": 105}
  }
}
```

您可以通过Web界面的 `/config` 页面修改这些配置，或者直接编辑JSON文件。

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | Flask 3.x |
| 数据处理 | Pandas |
| 图表可视化 | Plotly |
| 前端UI | Bootstrap 5 |
| 模板引擎 | Jinja2 |
| 测试框架 | pytest |

## 📝 开发说明

### 代码规范

- 遵循 [PEP 8](https://pep8.org/) Python代码规范
- 使用Google风格的Docstring
- 使用类型注解（Type Hints）

### 添加新功能

1. 在 `app/routes/` 中添加新的路由蓝图
2. 在 `app/core/` 中实现业务逻辑
3. 在 `templates/` 中创建对应的HTML模板

## 📄 许可证

本项目基于 [MIT许可证](LICENSE) 开源。

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**注意**：本系统仅用于教学分析目的，成绩数据请妥善保管。
