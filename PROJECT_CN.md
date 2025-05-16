# Notebook Agent 项目概览

## 项目描述

Notebook Agent 是一个基于 LangGraph 的框架，旨在自动生成用于数据分析任务的 Jupyter 笔记本。它采用端到端（E2E）的方法创建笔记本，对指定的数据集执行各种数据分析操作。

### 主要功能

- 对指定数据集进行探索性数据分析（EDA）
- 统计分析和假设检验
- 基于模板为新数据集生成笔记本（计划中）

## 项目结构

```
notebook_agent_playground/
├── .codespellignore         # 代码拼写检查配置
├── .env.example             # 环境变量示例文件
├── .git/                    # Git 仓库数据
├── .gitignore               # Git 忽略配置
├── LICENSE                  # 项目许可证
├── Makefile                 # 构建自动化
├── README.md                # 项目文档
├── PROJECT.md               # 本文件 - 项目结构概览
├── data/                    # 数据目录
│   └── tmall_order_report.csv  # 用于分析的示例数据集
├── dest/                    # 生成的笔记本输出目录
│   ├── notebook_*.ipynb     # 带时间戳的生成笔记本
│   └── test.ipynb           # 测试笔记本
├── langgraph.json           # LangGraph 配置
├── pyproject.toml           # Python 项目配置
├── src/                     # 源代码
│   └── react_agent/         # 主要代理实现
│       ├── __init__.py      # 包初始化
│       ├── configuration.py # 配置设置
│       ├── graph.py         # LangGraph 工作流定义
│       ├── prompts.py       # LLM 提示模板
│       ├── state.py         # 状态管理
│       ├── tools.py         # 代理工具实现
│       └── utils.py         # 实用函数
├── static/                  # 静态资源
└── tests/                   # 测试目录
```

## 核心组件

### 1. LangGraph 框架

该项目基于 LangGraph 构建，它提供了一个用于创建代理工作流的框架。主要图形在 `graph.py` 中定义，它协调语言模型和工具之间的流程。

### 2. 代理工具

代理在 `tools.py` 中实现了几个工具：

- `summary_csv`：读取 CSV 文件并返回汇总统计信息
- `generate_notebook`：基于查询创建 JSON 格式的笔记本
- `save_notebook`：将 JSON 笔记本保存为 .ipynb 文件

### 3. 工作流程

该代理遵循 ReAct（推理和行动）模式：
1. 用户提供生成报告的指令（例如，"为 tmall_order_report.csv 生成数据分析笔记本"）
2. 代理使用 `summary_csv` 工具获取数据统计信息
3. 基于摘要和用户需求，代理确定笔记本应包含的内容
4. 代理生成笔记本结构和内容
5. 笔记本保存到 `dest` 目录

## 配置

该项目使用环境变量进行配置：
- `LANGSMITH_PROJECT`：项目标识符
- `DEEPSEEK_API_KEY`：DeepSeek 模型的 API 密钥

默认模型是 `deepseek/deepseek-chat`。

## 入门指南

1. 安装依赖项：`pip install -e .`
2. 从示例创建 `.env` 文件：`cp .env.example .env`
3. 将您的 API 密钥添加到 `.env` 文件
4. 启动 LangGraph API 服务器：`langgraph dev`
5. 使用提供的 URL 在 LangGraph Studio 中测试应用程序

## 自定义选项

- 在 `tools.py` 中添加新工具
- 通过配置选择不同的模型
- 在 `prompts.py` 中自定义提示
- 修改 `graph.py` 中的代理推理过程
- 调整 ReAct 循环或向决策过程添加其他步骤

## 数据

该项目包含一个示例数据集：
- `tmall_order_report.csv`：包含用于分析的订单数据

## 输出

生成的笔记本存储在 `dest` 目录中，文件名带有时间戳。
