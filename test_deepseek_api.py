import requests

API_KEY = "sk-75961d0137714d0c84102b329ff7eb0f"
BASE_URL = "https://api.deepseek.com"   # 先用这个
MODEL = "deepseek-chat"

url = f"{BASE_URL}/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

data = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "用一句话介绍你自己"}
    ],
    "temperature": 0.7,
}

response = requests.post(url, headers=headers, json=data, timeout=60)
print("状态码:", response.status_code)
print("返回:", response.text)
