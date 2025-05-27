import json
import os

import requests
from langchain.tools import tool

class FileWriteTool:
    def __init__(self):
        pass
        
    def run(self, filename, content):
        """Useful to write content to a file with the given filename."""
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Write the content to the file
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(content)
            return f"File '{filename}' has been written successfully."
        except Exception as e:
            return f"Error writing file: {str(e)}"

# Create an instance of the tool that can be imported directly
file_write_tool = tool("Write file")(FileWriteTool().run)
