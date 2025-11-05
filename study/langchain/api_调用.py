import os
from openai import OpenAI

def call_llm(user_input: str):
    client = OpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("qwen")
    )

    response = client.chat.completions.create(
        model="qwen3-32b",
        messages=[
            {"role": "system", "content": "你是一名医疗助手"},
            {"role": "user", "content": user_input},
        ],
        extra_body={"enable_thinking": False},
        stream=True
    )


    for chunk in response:
        print(chunk.choices[0].delta.content)

my_input = input("请输入: ")
get_text = call_llm(my_input)
print("\n完整文本:", get_text)
