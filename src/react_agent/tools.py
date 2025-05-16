"""This module provides tools for notebook manipulation and data analysis.

It includes tools for creating, editing, and converting Jupyter notebooks,
as well as tools for data analysis and visualization.
"""

from typing import Any, Callable, List, Optional, cast
import json, os, time
import pandas as pd

# Import from our custom tools and schema modules
import sys
import os.path

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import tools and schema
from tools.notebook import edit_cell, create_cell, insert_cell, merge_cells, append_cell, swap_cells
from tools.notebook import convert_notebook_to_format, convert_file_to_notebook, convert_notebook_to_executable
from tools.notebook import notebook_from_markdown, extract_code_from_notebook

# Import schema models
from schema.notebook import Notebook, Cell, NotebookMetadata, CellOutput

# Local imports
from react_agent.configuration import Configuration


# async def search(query: str) -> Optional[dict[str, Any]]:
#     """Search for general web results.

#     This function performs a search using the Tavily search engine, which is designed
#     to provide comprehensive, accurate, and trusted results. It's particularly useful
#     for answering questions about current events.
#     """
#     configuration = Configuration.from_context()
#     wrapped = TavilySearch(max_results=configuration.max_search_results)
#     return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))


def summary_csv(file_path: str):
    """Read the csv file and return summary data
    
    This function should be applied before considering what elements should be incorporated into the EDA analysis or hypothesis testing"""

    df = pd.read_csv(os.path.join('data', file_path))
    return df.describe().to_dict()

def generate_notebook(query: str):
    """create the json format of notebook for the given query"""
    requirements = [
        "Use os.path.join('../data', file_path) for file reading. ",
        "Use Chinese descriptions. ",
        "Ensure Chinese characters display correctly in plots if any. ",
        "Ensure the code is executable.",
        "If hypothesis testing is required, the default significance level is 0.05, and conclusions should be described based on this value"
    ]
    description = f"根据要求{requirements},完成{query}的代码，并封装为ipynb框架的json格式，最终仅返回json。"

    return description

def save_notebook(notebook):
    """Save the json format of notebook to ipynb file."""
    
    def get_notebook_name():
        return 'notebook_' + str(int(time.time())) + '.ipynb'
    
    file_name = get_notebook_name()
    with open(os.path.join('dest', file_name), 'w', encoding='utf-8') as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)
    return f"{file_name} 保存成功"


# Define all available tools
TOOLS: List[Callable[..., Any]] = [
    # Existing tools
    generate_notebook, 
    save_notebook, 
    summary_csv,
    
    # Cell manipulation tools
    edit_cell,
    create_cell,
    insert_cell,
    merge_cells,
    append_cell,
    swap_cells,
    
    # Conversion tools
    convert_notebook_to_format,
    convert_file_to_notebook,
    convert_notebook_to_executable,
    notebook_from_markdown,
    extract_code_from_notebook
]
