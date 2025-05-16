"""Tools related to CRUD notebooks and conversion between formats"""

import json
import os
import io
import re
from typing import Any, Dict, List, Optional, Union, Tuple, BinaryIO

# Import schema models
from schema.notebook import Notebook, Cell, NotebookMetadata, CellOutput, notebook_from_json, notebook_to_json

def edit_cell(notebook_json: str, cell_index: int, new_content: str, cell_type: Optional[str] = None) -> str:
    """Edit a cell in a Jupyter notebook.
    
    Args:
        notebook_json: The ipynb formatted JSON string
        cell_index: The index of the cell to edit (0-based)
        new_content: The new content for the cell
        cell_type: Optional new cell type ('code', 'markdown', or 'raw')
        
    Returns:
        The updated ipynb formatted JSON string
    """
    try:
        # Convert JSON to Pydantic model
        notebook = notebook_from_json(notebook_json)
        
        # Validate cell index
        if cell_index < 0 or cell_index >= len(notebook.cells):
            raise ValueError(f"Cell index {cell_index} is out of range. Notebook has {len(notebook.cells)} cells.")
        
        # Update cell content
        if isinstance(new_content, str):
            notebook.cells[cell_index].source = new_content.split('\n')
        else:
            notebook.cells[cell_index].source = new_content
        
        # Update cell type if provided
        if cell_type is not None:
            if cell_type not in ['code', 'markdown', 'raw']:
                raise ValueError(f"Invalid cell type: {cell_type}. Must be 'code', 'markdown', or 'raw'.")
            
            # Update the cell type
            notebook.cells[cell_index].cell_type = cell_type
            
            # Reset outputs if changing to markdown or raw
            if cell_type in ['markdown', 'raw']:
                notebook.cells[cell_index].outputs = []
                notebook.cells[cell_index].execution_count = None
        
        # Convert back to JSON
        return notebook_to_json(notebook)
    except json.JSONDecodeError:
        raise ValueError("Invalid notebook JSON format")
    except Exception as e:
        raise ValueError(f"Error editing cell: {str(e)}")


def create_cell(notebook_json: str, content: str, cell_type: str = 'code', metadata: Optional[Dict[str, Any]] = None) -> str:
    """Create a new cell and append it to the end of a Jupyter notebook.
    
    Args:
        notebook_json: The ipynb formatted JSON string
        content: The content for the new cell
        cell_type: The cell type ('code', 'markdown', or 'raw')
        metadata: Optional metadata for the cell
        
    Returns:
        The updated ipynb formatted JSON string
    """
    try:
        # Convert JSON to Pydantic model
        notebook = notebook_from_json(notebook_json)
        
        # Validate cell type
        if cell_type not in ['code', 'markdown', 'raw']:
            raise ValueError(f"Invalid cell type: {cell_type}. Must be 'code', 'markdown', or 'raw'.")
        
        # Create new cell using the Cell model
        new_cell = Cell(
            cell_type=cell_type,
            metadata=metadata or {},
            source=content.split('\n') if isinstance(content, str) else content
        )
        
        # Add outputs and execution_count for code cells
        if cell_type == 'code':
            new_cell.outputs = []
            new_cell.execution_count = None
        
        # Append the new cell
        if notebook.cells is None:
            notebook.cells = []
        notebook.cells.append(new_cell)
        
        # Convert back to JSON
        return notebook_to_json(notebook)
    except json.JSONDecodeError:
        raise ValueError("Invalid notebook JSON format")
    except Exception as e:
        raise ValueError(f"Error creating cell: {str(e)}")


def insert_cell(notebook_json: str, position: int, content: str, cell_type: str = 'code', 
                metadata: Optional[Dict[str, Any]] = None) -> str:
    """Insert a new cell at a specific position in a Jupyter notebook.
    
    Args:
        notebook_json: The ipynb formatted JSON string
        position: The position to insert the cell (0-based)
        content: The content for the new cell
        cell_type: The cell type ('code', 'markdown', or 'raw')
        metadata: Optional metadata for the cell
        
    Returns:
        The updated ipynb formatted JSON string
    """
    try:
        # Convert JSON to Pydantic model
        notebook = notebook_from_json(notebook_json)
        
        # Validate cell type
        if cell_type not in ['code', 'markdown', 'raw']:
            raise ValueError(f"Invalid cell type: {cell_type}. Must be 'code', 'markdown', or 'raw'.")
        
        # Ensure cells list exists
        if notebook.cells is None:
            notebook.cells = []
        
        # Validate position
        if position < 0 or position > len(notebook.cells):
            raise ValueError(f"Position {position} is out of range. Valid range is 0 to {len(notebook.cells)}.")
        
        # Create new cell using the Cell model
        new_cell = Cell(
            cell_type=cell_type,
            metadata=metadata or {},
            source=content.split('\n') if isinstance(content, str) else content
        )
        
        # Add outputs and execution_count for code cells
        if cell_type == 'code':
            new_cell.outputs = []
            new_cell.execution_count = None
        
        # Insert the new cell at the specified position
        notebook.cells.insert(position, new_cell)
        
        # Convert back to JSON
        return notebook_to_json(notebook)
    except json.JSONDecodeError:
        raise ValueError("Invalid notebook JSON format")
    except Exception as e:
        raise ValueError(f"Error inserting cell: {str(e)}")


def merge_cells(notebook_json: str, start_index: int, end_index: int) -> str:
    """Merge multiple consecutive cells in a Jupyter notebook.
    
    Args:
        notebook_json: The ipynb formatted JSON string
        start_index: The index of the first cell to merge (inclusive)
        end_index: The index of the last cell to merge (inclusive)
        
    Returns:
        The updated ipynb formatted JSON string
    """
    try:
        # Convert JSON to Pydantic model
        notebook = notebook_from_json(notebook_json)
        
        # Validate indices
        if not notebook.cells:
            raise ValueError("Notebook has no cells to merge")
            
        cell_count = len(notebook.cells)
        if start_index < 0 or start_index >= cell_count:
            raise ValueError(f"Start index {start_index} is out of range. Valid range is 0 to {cell_count-1}.")
            
        if end_index < start_index or end_index >= cell_count:
            raise ValueError(f"End index {end_index} is invalid. Must be between {start_index} and {cell_count-1}.")
        
        # Get cells to merge
        cells_to_merge = notebook.cells[start_index:end_index+1]
        
        # Determine the cell type of the merged cell (use the type of the first cell)
        merged_cell_type = cells_to_merge[0].cell_type
        
        # Merge the content
        merged_content = []
        for cell in cells_to_merge:
            # Add a newline between cells if not empty
            if merged_content and cell.source:
                merged_content.append('\n')
            if isinstance(cell.source, list):
                merged_content.extend(cell.source)
            else:
                merged_content.append(cell.source)
        
        # Create the merged cell using the Cell model
        merged_cell = Cell(
            cell_type=merged_cell_type,
            metadata=cells_to_merge[0].metadata,
            source=merged_content
        )
        
        # Add outputs and execution_count for code cells
        if merged_cell_type == 'code':
            merged_cell.outputs = []
            merged_cell.execution_count = None
        
        # Replace the range of cells with the merged cell
        notebook.cells[start_index:end_index+1] = [merged_cell]
        
        # Convert back to JSON
        return notebook_to_json(notebook)
    except json.JSONDecodeError:
        raise ValueError("Invalid notebook JSON format")
    except Exception as e:
        raise ValueError(f"Error merging cells: {str(e)}")


def append_cell(notebook_json: str, content: str, cell_type: str = 'code', 
                metadata: Optional[Dict[str, Any]] = None) -> str:
    """Append a new cell to the end of a Jupyter notebook.
    This is a convenience wrapper around create_cell.
    
    Args:
        notebook_json: The ipynb formatted JSON string
        content: The content for the new cell
        cell_type: The cell type ('code', 'markdown', or 'raw')
        metadata: Optional metadata for the cell
        
    Returns:
        The updated ipynb formatted JSON string
    """
    # This function is already a wrapper around create_cell which now uses Pydantic models
    return create_cell(notebook_json, content, cell_type, metadata)


def swap_cells(notebook_json: str, index1: int, index2: int) -> str:
    """Swap the positions of two cells in a Jupyter notebook.
    
    Args:
        notebook_json: The ipynb formatted JSON string
        index1: The index of the first cell
        index2: The index of the second cell
        
    Returns:
        The updated ipynb formatted JSON string
    """
    try:
        # Convert JSON to Pydantic model
        notebook = notebook_from_json(notebook_json)
        
        # Validate indices
        if not notebook.cells:
            raise ValueError("Notebook has no cells to swap")
            
        cell_count = len(notebook.cells)
        if index1 < 0 or index1 >= cell_count or index2 < 0 or index2 >= cell_count:
            raise ValueError(f"Cell indices must be between 0 and {cell_count-1}")
        
        # Swap the cells
        notebook.cells[index1], notebook.cells[index2] = notebook.cells[index2], notebook.cells[index1]
        
        # Convert back to JSON
        return notebook_to_json(notebook)
    except json.JSONDecodeError:
        raise ValueError("Invalid notebook JSON format")
    except Exception as e:
        raise ValueError(f"Error swapping cells: {str(e)}")


def convert_notebook_to_format(notebook_json: str, output_format: str, exclude_input: bool = False, 
                        exclude_output: bool = False) -> str:
    """Convert a notebook to a specified format using nbconvert.
    
    Args:
        notebook_json: The ipynb formatted JSON string
        output_format: The target format ('python', 'html', 'markdown', 'rst', 'latex', 'pdf', 'slides')
        exclude_input: Whether to exclude input cells in the output
        exclude_output: Whether to exclude output cells in the output
        
    Returns:
        The converted content as a string
    """
    try:
        from nbconvert import exporters
        import nbformat
        from traitlets.config import Config
        
        # Convert JSON to Pydantic model and then to nbformat NotebookNode
        notebook_model = notebook_from_json(notebook_json)
        
        # Convert Pydantic model to dict and then to nbformat NotebookNode
        notebook_dict = notebook_model.dict(exclude_none=True)
        notebook = nbformat.from_dict(notebook_dict)
        
        # Configure the exporter
        c = Config()
        if exclude_input:
            c.TemplateExporter.exclude_input = True
        if exclude_output:
            c.TemplateExporter.exclude_output = True
        
        # Select the appropriate exporter based on the format
        if output_format.lower() == 'python':
            exporter = exporters.PythonExporter(config=c)
        elif output_format.lower() == 'html':
            exporter = exporters.HTMLExporter(config=c)
        elif output_format.lower() == 'markdown':
            exporter = exporters.MarkdownExporter(config=c)
        elif output_format.lower() == 'rst':
            exporter = exporters.RSTExporter(config=c)
        elif output_format.lower() == 'latex':
            exporter = exporters.LatexExporter(config=c)
        elif output_format.lower() == 'pdf':
            exporter = exporters.PDFExporter(config=c)
        elif output_format.lower() == 'slides':
            exporter = exporters.SlidesExporter(config=c)
        else:
            raise ValueError(f"Unsupported format: {output_format}. Supported formats are: python, html, markdown, rst, latex, pdf, slides")
        
        # Convert the notebook
        output, resources = exporter.from_notebook_node(notebook)
        
        return output
    except ImportError as e:
        raise ImportError(f"Required packages not installed: {str(e)}. Please install nbconvert: pip install nbconvert")
    except Exception as e:
        raise ValueError(f"Error converting notebook: {str(e)}")


def convert_file_to_notebook(file_path: str, cell_type: str = 'code') -> str:
    """Convert a file (e.g., Python script) to a Jupyter notebook.
    
    Args:
        file_path: Path to the file to convert
        cell_type: The cell type to use ('code', 'markdown', or 'raw')
        
    Returns:
        The notebook as a JSON string
    """
    try:
        # Validate cell type
        if cell_type not in ['code', 'markdown', 'raw']:
            raise ValueError(f"Invalid cell type: {cell_type}. Must be 'code', 'markdown', or 'raw'.")
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create a notebook with a single cell containing the file content
        notebook = {
            "cells": [
                {
                    "cell_type": cell_type,
                    "metadata": {},
                    "source": content.split('\n'),
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "codemirror_mode": {
                        "name": "ipython",
                        "version": 3
                    },
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.8.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 5
        }
        
        # Add outputs and execution_count for code cells
        if cell_type == 'code':
            notebook['cells'][0]['outputs'] = []
            notebook['cells'][0]['execution_count'] = None
        
        return json.dumps(notebook, indent=2)
    except Exception as e:
        raise ValueError(f"Error converting file to notebook: {str(e)}")


def convert_notebook_to_executable(notebook_json: str, output_format: str = 'python', 
                             output_path: Optional[str] = None) -> str:
    """Convert a notebook to an executable format and optionally save to a file.
    
    Args:
        notebook_json: The ipynb formatted JSON string
        output_format: The target format (currently only 'python' is supported)
        output_path: Optional path to save the output file
        
    Returns:
        The converted content as a string
    """
    try:
        # Convert the notebook to the specified format
        output = convert_notebook_to_format(notebook_json, output_format)
        
        # Save to file if output_path is provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
        
        return output
    except Exception as e:
        raise ValueError(f"Error converting notebook to executable: {str(e)}")


def notebook_from_markdown(markdown_content: str) -> str:
    """Create a Jupyter notebook from markdown content.
    
    Args:
        markdown_content: The markdown content to convert
        
    Returns:
        The notebook as a JSON string
    """
    try:
        # Split the markdown content into cells based on headers
        import re
        
        # Split on markdown headers (# Header)
        cell_contents = re.split(r'(?m)^(#+\s.*?)$', markdown_content)
        
        # First element might be empty if the markdown starts with a header
        if cell_contents and not cell_contents[0].strip():
            cell_contents.pop(0)
        
        # Create cells from the split content
        cells = []
        
        # If there are no headers, create a single markdown cell
        if not cell_contents:
            cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": markdown_content.split('\n')
            })
        else:
            # Process the split content
            i = 0
            while i < len(cell_contents):
                # Check if this is a header
                if i < len(cell_contents) - 1 and re.match(r'^#+\s', cell_contents[i]):
                    # Combine the header with its content
                    cell_content = cell_contents[i] + '\n' + cell_contents[i+1]
                    cells.append({
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": cell_content.split('\n')
                    })
                    i += 2
                else:
                    # This is content without a header
                    cells.append({
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": cell_contents[i].split('\n')
                    })
                    i += 1
        
        # Create the notebook
        notebook = {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "codemirror_mode": {
                        "name": "ipython",
                        "version": 3
                    },
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.8.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 5
        }
        
        return json.dumps(notebook, indent=2)
    except Exception as e:
        raise ValueError(f"Error creating notebook from markdown: {str(e)}")


def extract_code_from_notebook(notebook_json: str) -> List[str]:
    """Extract code from all code cells in a notebook.
    
    Args:
        notebook_json: The ipynb formatted JSON string
        
    Returns:
        A list of code strings from the code cells
    """
    try:
        # Convert JSON to Pydantic model
        notebook = notebook_from_json(notebook_json)
        
        code_cells = []
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                source = cell.source
                if isinstance(source, list):
                    code_cells.append(''.join(source))
                else:
                    code_cells.append(source)
        
        return code_cells
    except json.JSONDecodeError:
        raise ValueError("Invalid notebook JSON format")
    except Exception as e:
        raise ValueError(f"Error extracting code from notebook: {str(e)}")


# List of tools to be exported
NOTEBOOK_TOOLS = [
    edit_cell,
    create_cell,
    insert_cell,
    merge_cells,
    append_cell,
    swap_cells,
    convert_notebook_to_format,
    convert_file_to_notebook,
    convert_notebook_to_executable,
    notebook_from_markdown,
    extract_code_from_notebook
]