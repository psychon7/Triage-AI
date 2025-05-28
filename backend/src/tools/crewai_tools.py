import os
from langchain.tools import tool

class FileReadTool:
    def __init__(self):
        pass
    
    def run(self, file_path):
        """Read content from a file."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                return content
            else:
                return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
