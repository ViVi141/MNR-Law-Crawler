# MNR Law Crawler (自然资源部法规爬虫工具) v2.0

> **GUI和命令行二合一**的现代化政策爬虫工具

**English**: MNR Law Crawler | **中文**: 自然资源部法规爬虫工具

## ✨ 特性

- 🖥️ **双模式支持**：支持GUI图形界面和CLI命令行两种模式
- 🎯 **智能爬取**：自动识别并爬取法律法规、部门规章、规范性文件
- 📄 **文档转换**：自动将DOCX/DOC/PDF转换为Markdown格式
- 🤖 **RAG知识库**：生成适合RAG系统的结构化Markdown文件（含YAML Front Matter）
- 🛡️ **反爬虫对抗**：User-Agent轮换、会话管理、代理IP支持
- 💾 **多格式保存**：同时保存JSON、Markdown、DOCX和原始文件
- 📊 **实时进度**：实时显示爬取进度和统计信息
- ⚙️ **灵活配置**：支持GUI设置和配置文件两种方式
- 🧹 **智能清洗**：自动清洗HTML内容，移除页面元素和重复元信息
- 📋 **完整元信息**：自动提取发布日期、发布机构、效力级别等完整元信息

## 📦 项目结构

```
mnr-law-crawler/
├── core/                      # 核心业务逻辑
│   ├── __init__.py
│   ├── config.py             # 配置管理
│   ├── models.py             # 数据模型
│   ├── api_client.py         # API客户端
│   ├── converter.py          # 文档转换
│   └── crawler.py            # 爬虫核心
├── gui/                       # GUI界面
│   ├── __init__.py
│   ├── main_window.py        # 主窗口
│   ├── crawl_tab.py          # 爬取配置标签
│   ├── progress_tab.py       # 进度显示标签
│   └── settings_tab.py       # 设置标签
├── cli/                       # 命令行界面
│   ├── __init__.py
│   └── commands.py           # CLI命令
├── utils/                     # 工具函数
│   ├── __init__.py
│   ├── logger.py             # 日志管理
│   ├── file_handler.py       # 文件处理
│   └── validator.py          # 数据验证
├── main.py                    # 统一入口
├── config.json                # 配置文件（首次运行自动创建）
├── config.json.example        # 配置文件模板
├── requirements.txt           # 依赖清单
└── README.md                  # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置设置（可选）

首次运行程序会自动创建 `config.json` 配置文件。如果需要自定义配置，可以：

```bash
# 复制配置模板
cp config.json.example config.json

# 然后编辑 config.json 文件，设置你的参数
```

**注意**：需要根据自然资源部实际API调整 `api_base_url` 和相关API接口。

### 3. 运行程序

#### GUI模式（图形界面）

```bash
python main.py
```

#### CLI模式（命令行）

```bash
# 查看帮助
python main.py --help

# 爬取单个政策
python main.py crawl --type 1

# 批量爬取
python main.py batch --types 1,2,3

# 查看版本
python main.py version
```

## ⚙️ 配置说明

### 核心配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `base_url` | 网站基础URL | `https://f.mnr.gov.cn/` |
| `search_api` | 搜索API地址 | `https://search.mnr.gov.cn/was5/web/search` |
| `channel_id` | 频道ID | `174757` |
| `output_dir` | 输出目录 | `crawled_data` |
| `perpage` | 每页数量 | `20` |
| `max_pages` | 最大页数 | `999999` |
| `timeout` | 请求超时（秒） | `30` |
| `request_delay` | 请求延迟（秒） | `2` |
| `retry_delay` | 重试延迟（秒） | `5` |

### 数据源配置

支持配置多个数据源，每个数据源可独立设置：
- `name`: 数据源名称
- `base_url`: 基础URL
- `search_api`: 搜索API
- `ajax_api`: AJAX API
- `channel_id`: 频道ID
- `enabled`: 是否启用

## 📂 输出结构

```
crawled_data/
├── json/                          # JSON数据文件
│   └── policy_{标题}_{来源}.json  # 政策数据（含完整元信息）
├── docx/                          # DOCX格式文件
│   └── {编号}_{政策名称}.docx     # Word文档
├── files/                         # 原始附件文件
│   └── {编号}_{filename}.{ext}   # 下载的附件
└── markdown/                      # RAG格式Markdown
    └── {编号}_{政策名称}.md       # RAG知识库文件（含YAML Front Matter）
```

### Markdown文件格式

生成的Markdown文件包含：
- **YAML Front Matter**：包含标题、发布机构、发布日期、发文字号等元信息
- **基本信息**：结构化的政策基本信息
- **正文内容**：清洗后的正文内容（已移除页面元素和重复元信息）

## 🔧 技术特性

### 内容清洗
- 自动移除页面元素（搜索框、导航栏、打印按钮等）
- 移除重复的元信息表格
- 智能识别正文开始位置
- 处理被拆分的文本（如"来一一源"）

### 元信息提取
- 从列表页提取基础元信息
- 从详情页提取完整元信息（发布日期、发布机构、效力级别等）
- 自动验证日期格式，避免误提取
- 按行匹配标签和值，确保准确性

### HTML解析
- 针对 f.mnr.gov.cn 的特定HTML结构定制化解析
- 支持多种正文容器（id="content"、class="Custom_UnionStyle"等）
- 智能识别政策表格（基于行数和标签特征）

## 📄 许可证

本项目采用 **MIT License** 开源许可证。

## 👥 作者

**ViVi141**

- **GitHub**: [@ViVi141](https://github.com/ViVi141)
- **邮箱**: 747384120@qq.com

**项目名称**: mnr-law-crawler  
**英文全称**: MNR Law Crawler  
**中文名称**: 自然资源部法规爬虫工具

---

**版本**: 2.0.0  
**最后更新**: 2025-12-07  
**项目主页**: https://github.com/ViVi141/mnr-law-crawler

## 📝 更新日志

### v2.0.0 (2025-12-07)
- ✅ 支持多数据源并行爬取（政府信息公开平台、政策法规库）
- ✅ 实现针对不同网站的专用HTML解析器
- ✅ 优化日志系统，支持彩色输出和文件轮转
- ✅ 实现政策重试机制，支持自动重试和手动重试失败政策
- ✅ 添加失败政策专用日志记录
- ✅ 优化测试模式，支持多数据源各自输出第一条政策
- ✅ 改进GUI界面，支持数据源选择和管理

### v1.0.0 (2025-11-28)
- ✅ 适配 f.mnr.gov.cn 网站结构
- ✅ 实现智能内容清洗，移除页面元素和重复元信息
- ✅ 完善元信息提取，支持从详情页提取完整元信息
- ✅ 修复标签和值匹配错位问题
- ✅ 优化日期格式验证，避免误提取
- ✅ 支持多数据源配置
- ✅ 支持打包为exe可执行文件

## 📦 打包说明

### 打包为EXE

使用提供的打包脚本：

```bash
python build_exe.py
```

打包完成后，exe文件位于 `dist/MNR-Law-Crawler.exe`

**打包要求**：
- 已安装 PyInstaller: `pip install pyinstaller`
- Python 3.8+

**使用打包的EXE**：
1. 将 `MNR-Law-Crawler.exe` 和 `config.json.example` 放在同一目录
2. 复制 `config.json.example` 为 `config.json`（可选，程序会自动创建）
3. 双击运行 `MNR-Law-Crawler.exe`

