"""Pydantic data models for Jupyter notebooks and cells."""

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field


class CellOutput(BaseModel):
    """Model for cell output data."""
    output_type: str = Field(description="Type of the output (e.g., 'execute_result', 'stream', 'error')")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadata associated with the output")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Output data for rich display")
    text: Optional[Union[str, List[str]]] = Field(default=None, description="Text output content")
    execution_count: Optional[int] = Field(default=None, description="Execution count for this output")
    traceback: Optional[List[str]] = Field(default=None, description="Traceback for error outputs")
    name: Optional[str] = Field(default=None, description="Name for stream outputs")
    ename: Optional[str] = Field(default=None, description="Error name for error outputs")
    evalue: Optional[str] = Field(default=None, description="Error value for error outputs")


class Cell(BaseModel):
    """Model for a Jupyter notebook cell."""
    cell_type: Literal['code', 'markdown', 'raw'] = Field(
        description="Type of the cell (code, markdown, or raw)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Cell metadata"
    )
    source: Union[str, List[str]] = Field(
        description="Cell content as a string or list of strings"
    )
    # Fields specific to code cells
    outputs: Optional[List[CellOutput]] = Field(
        default=None,
        description="Outputs of code execution (only for code cells)"
    )
    execution_count: Optional[int] = Field(
        default=None,
        description="Execution count (only for code cells)"
    )
    
    class Config:
        extra = "allow"  # Allow extra fields for future compatibility


class NotebookMetadata(BaseModel):
    """Model for Jupyter notebook metadata."""
    kernelspec: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Kernel specification"
    )
    language_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Language information"
    )
    authors: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Authors of the notebook"
    )
    title: Optional[str] = Field(
        default=None,
        description="Title of the notebook"
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the notebook"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Tags associated with the notebook"
    )
    
    class Config:
        extra = "allow"  # Allow extra fields for future compatibility


class Notebook(BaseModel):
    """Model for a complete Jupyter notebook."""
    cells: List[Cell] = Field(
        default_factory=list,
        description="List of cells in the notebook"
    )
    metadata: NotebookMetadata = Field(
        default_factory=NotebookMetadata,
        description="Notebook metadata"
    )
    nbformat: int = Field(
        default=4,
        description="Notebook format version number"
    )
    nbformat_minor: int = Field(
        default=5,
        description="Notebook format minor version number"
    )
    
    class Config:
        extra = "allow"  # Allow extra fields for future compatibility


# Helper functions to convert between Pydantic models and JSON
def notebook_from_json(notebook_json: str) -> Notebook:
    """Convert a JSON string to a Notebook model.
    
    Args:
        notebook_json: The ipynb formatted JSON string
        
    Returns:
        A Notebook model instance
    """
    import json
    notebook_dict = json.loads(notebook_json)
    return Notebook.parse_obj(notebook_dict)


def notebook_to_json(notebook: Notebook, indent: int = 2) -> str:
    """Convert a Notebook model to a JSON string.
    
    Args:
        notebook: The Notebook model instance
        indent: Number of spaces for indentation in the output JSON
        
    Returns:
        The ipynb formatted JSON string
    """
    import json
    return json.dumps(notebook.dict(exclude_none=True), indent=indent)
