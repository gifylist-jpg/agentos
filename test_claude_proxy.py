import requests

# ====== 这里填你的信息 ======
API_KEY = "sk-1EtRec2OceWO85DGQGmmKWWkORuHsKh3M3nWLrn1Zz8FMtDD"
BASE_URL = "https://renrenai.chat"
MODEL = "claude-sonnet-4-5-20250929"
# ===========================

url = f"{BASE_URL}/v1/messages"

headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

data = {
    "model": MODEL,
    "max_tokens": 200,
    "messages": [
        {"role": "user", "content": "用一句话介绍你自己"}
    ]
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=60)

    print("状态码:", response.status_code)
    print("返回内容:", response.text)

    if response.status_code == 200:
        result = response.json()
        print("\n✅ 成功解析：")
        print(result["content"][0]["text"])
    else:
        print("\n❌ 请求失败")

except Exception as e:
    print("异常:", e)
