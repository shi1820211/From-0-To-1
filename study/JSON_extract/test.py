import requests
import json

API_URL = "https://openai.fakeopen.com/v1/chat/completions"  # 替换为 Qwen 官方 openai 兼容 URL
API_KEY = "sk-96b5857ed3764061b283d3b06e4143d6"

payload = {
    "model": "qwen-plus",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "测试 Qwen API"}
    ],
    "temperature": 0.0,
    "max_tokens": 500
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

response = requests.post(API_URL, headers=headers, json=payload)
print(response.status_code)
print(response.text)
