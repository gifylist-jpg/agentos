import os
import subprocess

# 要搜索的目录（可以根据实际情况调整）
search_directory = "."

# 定义需要查找的关键词
search_keywords = [
    "tool_executor.execute",
    ".execute(",  # 查找执行调用
    "production_agent",
    "ops_agent"
]

# 执行查找操作的函数
def run_search():
    for keyword in search_keywords:
        print(f"\nSearching for '{keyword}' in {search_directory}...")
        result = subprocess.run(["grep", "-R", keyword, search_directory], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            print(f"Found matches for '{keyword}':\n{result.stdout}")
        else:
            print(f"No matches found for '{keyword}'.")

# 运行查找操作
if __name__ == "__main__":
    run_search()
