# MNR Law Crawler (自然资源部法规爬虫工具) v1.0

> **GUI和命令行二合一**的现代化政策爬虫工具

**English**: MNR Law Crawler | **中文**: 自然资源部法规爬虫工具

## ✨ 特性

- 🖥️ **双模式支持**：支持GUI图形界面和CLI命令行两种模式
- 🎯 **智能爬取**：自动识别并爬取法律法规、部门规章、规范性文件
- 📄 **文档转换**：自动将DOCX/DOC/PDF转换为Markdown格式
- 🤖 **RAG知识库**：生成适合RAG系统的结构化Markdown文件
- 🛡️ **反爬虫对抗**：User-Agent轮换、会话管理、代理IP支持
- 💾 **多格式保存**：同时保存JSON、Markdown和原始文件
- 📊 **实时进度**：实时显示爬取进度和统计信息
- ⚙️ **灵活配置**：支持GUI设置和配置文件两种方式

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
| `api_base_url` | API基础URL | `https://www.mnr.gov.cn/api` |
| `output_dir` | 输出目录 | `crawled_data` |
| `law_rule_types` | 政策类型列表 | `[1, 2, 3]` |

**重要提示**：需要根据自然资源部实际API接口调整以下内容：
- `api_base_url`：API基础URL
- `core/api_client.py`：API接口URL和参数格式
- `core/models.py`：数据模型字段映射
- `core/crawler.py`：政策类型名称和URL生成

## 📂 输出结构

```
crawled_data/
├── json/                          # JSON数据文件
│   ├── policy_{id}.json          # 基础数据
│   └── policy_{id}_complete.json # 完整数据
├── files/                         # 原始附件文件
│   └── {id}_{filename}.{ext}     # 下载的附件
└── markdown/                      # RAG格式Markdown
    └── {编号}_{政策名称}.md       # RAG知识库文件
```

## 🔧 开发说明

本项目基于 `gd-law-crawler` 的项目结构创建，需要根据自然资源部实际API进行以下调整：

1. **API接口调整**：修改 `core/api_client.py` 中的API URL和请求参数
2. **数据模型调整**：修改 `core/models.py` 中的字段映射
3. **爬虫逻辑调整**：根据实际API响应格式调整 `core/crawler.py`
4. **配置调整**：更新 `config.json.example` 中的默认配置

## 📄 许可证

本项目采用 **Apache License 2.0** 开源许可证。

## 👥 作者

**ViVi141**

- **GitHub**: [@ViVi141](https://github.com/ViVi141)
- **邮箱**: 747384120@qq.com

**项目名称**: mnr-law-crawler  
**英文全称**: MNR Law Crawler  
**中文名称**: 自然资源部法规爬虫工具

---

**版本**: 1.0.0  
**最后更新**: 2025-11-25  
**项目主页**: https://github.com/ViVi141/mnr-law-crawler

