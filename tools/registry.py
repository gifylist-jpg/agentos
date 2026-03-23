class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name, func):
        self.tools[name] = func

    def get_tool(self, name):
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
        return self.tools[name]
