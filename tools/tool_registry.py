from tools.web_search import web_search
from tools.file_system import save_to_file


class ToolRegistry:
    def __init__(self):
        self.tools = {
            "web_search": web_search,
            "save_to_file": save_to_file
        }

    def get_tool(self, tool_name):
        return self.tools.get(tool_name)

    def list_tools(self):
        return list(self.tools.keys())

    def execute(self, tool_name, *args, **kwargs):
        tool = self.get_tool(tool_name)

        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        return tool(*args, **kwargs)
