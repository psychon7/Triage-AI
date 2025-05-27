# Create native CrewAI tools using the tool decorator
from crewai.tools import tool
from tools.search_utils import CachedSearch
from tools.file_write import FileWriteTool
from tools.directory_write import DirWriteTool
from tools.crewai_tools import FileReadTool

file_read_tool = FileReadTool()
cached_search = CachedSearch()
@tool("Search the web")
def search_web(query: str) -> str:
    """Search the web for information with caching and retry logic."""
    return cached_search.search(query)

@tool("Read file")
def read_file(file_path: str) -> str:
    """Read content from a file."""
    return file_read_tool.run(file_path)

@tool("Write file")
def write_file(filename: str, content: str) -> str:
    """Write content to a file."""
    return FileWriteTool().run(filename, content)

@tool("Create directory")
def create_directory(directory_path: str) -> str:
    """Create a new directory."""
    return DirWriteTool().run(directory_path)

# Tool lists
architect_tools = [
    search_web,
    read_file,
    write_file,
    create_directory
]

security_tools = [
    search_web,
    read_file,
    write_file,
    create_directory
]

programmer_tools = [
    read_file,
    write_file,
    create_directory
]

tester_tools = [
    read_file,
    write_file,
    create_directory
]

reviewer_tools = [
    read_file,
    write_file,
    create_directory
]