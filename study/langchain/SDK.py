import os
from openai import OpenAI



MODEL_API_KEY_MAP={
    "qwen1.5-14b": os.environ.get("QWEN1-5_API_KEY"),
    "qwen3-32b" : os.environ.get("QWEN3-32B_API_KEY"),
    "qwen2-72b": os.environ.get("QWEN2-72_API_KEY"),
}

def get_api_key(name):
    return MODEL_API_KEY_MAP.get(name)

model ="qwen1.5-14b"
api_key = get_api_key(model)
client =OpenAI(api_key=api_key)
resp = client.chat(model=model,
                   message=[{"role":"user","content":"user_input"}]
                   )
print(resp)