import json
import os

import requests
from langchain.tools import tool

class DirWriteTool:
    def __init__(self):
        pass
        
    def run(self, directory_path):
        """Useful to create a directory with the given path."""
        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                return f"Directory '{directory_path}' has been created successfully."
            else:
                return f"Directory '{directory_path}' already exists."
        except Exception as e:
            return f"Error creating directory: {str(e)}"

# Create an instance of the tool that can be imported directly
dir_write_tool = tool("Create directory")(DirWriteTool().run)
