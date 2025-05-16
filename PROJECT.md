# Notebook Agent Project Overview

## Project Description

The Notebook Agent is a LangGraph-based framework designed to automatically generate Jupyter notebooks for data analysis tasks. It uses an E2E (End-to-End) approach to create notebooks that perform various data analysis operations on specified datasets.

### Key Features

- Exploratory Data Analysis (EDA) on specified datasets
- Statistical analysis and hypothesis testing
- Template-based notebook generation for new datasets (Planned)

## Project Structure

```
notebook_agent_playground/
├── .codespellignore         # Configuration for code spell checking
├── .env.example             # Example environment variables file
├── .git/                    # Git repository data
├── .gitignore               # Git ignore configuration
├── LICENSE                  # Project license
├── Makefile                 # Build automation
├── README.md                # Project documentation
├── PROJECT.md               # This file - project structure overview
├── data/                    # Data directory
│   └── tmall_order_report.csv  # Sample dataset for analysis
├── dest/                    # Output directory for generated notebooks
│   ├── notebook_*.ipynb     # Generated notebooks with timestamps
│   └── test.ipynb           # Test notebook
├── langgraph.json           # LangGraph configuration
├── pyproject.toml           # Python project configuration
├── src/                     # Source code
│   └── react_agent/         # Main agent implementation
│       ├── __init__.py      # Package initialization
│       ├── configuration.py # Configuration settings
│       ├── graph.py         # LangGraph workflow definition
│       ├── prompts.py       # LLM prompt templates
│       ├── state.py         # State management
│       ├── tools.py         # Agent tools implementation
│       └── utils.py         # Utility functions
├── static/                  # Static assets
└── tests/                   # Test directory
```

## Core Components

### 1. LangGraph Framework

The project is built on LangGraph, which provides a framework for creating agent workflows. The main graph is defined in `graph.py`, which orchestrates the flow between the language model and tools.

### 2. Agent Tools

The agent has several tools implemented in `tools.py`:

- `summary_csv`: Reads a CSV file and returns summary statistics
- `generate_notebook`: Creates a JSON format notebook based on a query
- `save_notebook`: Saves the JSON notebook to an .ipynb file

### 3. Workflow

The agent follows a ReAct (Reasoning and Action) pattern:
1. User provides instructions for generating a report (e.g., "Generate a data analysis notebook for tmall_order_report.csv")
2. The agent uses the `summary_csv` tool to get data statistics
3. Based on the summary and user requirements, the agent determines what the notebook should contain
4. The agent generates the notebook structure and content
5. The notebook is saved to the `dest` directory

## Configuration

The project uses environment variables for configuration:
- `LANGSMITH_PROJECT`: Project identifier
- `DEEPSEEK_API_KEY`: API key for the DeepSeek model

The default model is `deepseek/deepseek-chat`.

## Getting Started

1. Install dependencies: `pip install -e .`
2. Create a `.env` file from the example: `cp .env.example .env`
3. Add your API keys to the `.env` file
4. Start the LangGraph API server: `langgraph dev`
5. Test the application in LangGraph Studio using the provided URL

## Customization Options

- Add new tools in `tools.py`
- Select different models via configuration
- Customize prompts in `prompts.py`
- Modify the agent's reasoning process in `graph.py`
- Adjust the ReAct loop or add additional steps to the decision-making process

## Data

The project includes a sample dataset:
- `tmall_order_report.csv`: Contains order data for analysis

## Output

Generated notebooks are stored in the `dest` directory with timestamped filenames.
