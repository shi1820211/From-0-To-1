import pandas as pd
import json
import requests
import time
import re

# -----------------------------
# 配置参数
# -----------------------------
API_KEY = "sk-96b5857ed3764061b283d3b06e4143d6"  # 替换为你的 Qwen API Key
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
EXCEL_FILE = r"C:\Users\autobio\PycharmProjects\study\JSON_extract\热病和ABX菌整理-20240116.xlsx"
MODEL_NAME = "qwen-plus"

# -----------------------------
# 读取 Excel 文本
# -----------------------------
def read_entire_excel(file_path):
    xls = pd.ExcelFile(file_path)
    all_text = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        lines = []
        for row in df.itertuples(index=False):
            row_text = [str(cell) for cell in row if pd.notna(cell)]
            if row_text:
                lines.append(" ".join(row_text))
        if lines:
            all_text.append(f"Sheet: {sheet_name}\n" + "\n".join(lines))
    return "\n\n".join(all_text)

# -----------------------------
# 构建提示词
# -----------------------------
def build_prompt(table_text):
    prompt = f"""
    你是一名医学信息结构化提取与逻辑推断助手，负责将感染治疗表格中的内容转化为标准 JSON 格式，并根据药物适用条件和药物逻辑关系自动整理。若中间因max_token出现中断，继续运行，直到处理完整个文件。

    输入是从 Excel 表格中提取的文本，内容包括：
    1. 菌种/病原体名称（可能包含中英文混合、旧称、学名）
    2. 药物推荐（首选、次选、替代药物、联合用药、其他有效药物）
    3. 药物适用条件（如“不用于肺炎”、“部分菌株敏感”、“耐药”）
    4. 可能包含表格引用（如“表 1，23 页”）
    5. 可能出现首选与备选/替代治疗合并在一个单元格的情况
    6. 同一菌种对应多种不同感染状况（细分感染场景），需根据条件拆分

    任务要求：
    1. **菌种名称处理**：
       - 仅保留中文名称（去除英文、括号中的外文或拉丁文、去除重复）

    2. **感染场景拆分**：
       - 根据药物适用条件和描述，自动拆分出多个不同的感染场景（如“肺炎”、“非肺炎”，或“新生儿必须治疗”、“5岁以下儿童应治疗”等细分状况）
       - 感染场景名称字段支持较长文本描述，以精准区分不同状况
       - 同一菌种下多个场景分别列出
       - 同一药物有条件限制时，只出现在符合条件的场景中
       - 无条件限制时，场景名称为“未分类”

    3. **药物关系规则**：
       - **或关系**：若药物间仅用顿号/逗号分隔，且无“联合/合用/+”等字样，则每个药物单独放在【】中，竖排输出
       - **联合关系**：若药物间有“联合/合用/+”等字样，则放在同一个【】中，用逗号隔开
       - 保留药物出现顺序
       - “次选”与“替代药物”统一放在 "次选用药" 中
       - 药物说明（如“部分菌株敏感”、“耐药”）放在 "备注" 字段
       - 药物后的剂量、频次、给药方式应当原样保留在【】内
       - 药物后的文献引用若与疗效无关，删除；若说明用药条件，则放在 "备注"

    4. **合并单元格拆分**：
       - 如果同一单元格中同时包含首选和备选（替代）治疗，用关键词“首选治疗”、“备选治疗”、“替代治疗”进行拆分，填入对应字段
       - 若不存在备选/替代，则剩余内容全部视为首选

    5. **表格引用处理**：
       - 如果某个字段内容只包含表格引用（如“表 1，23 页”或“见表 2”），则将该字段置为 null

    6. **输出结构**：
    [
      {{
        "菌种名称": "菌种中文名称",
        "感染场景": [
          {{
            "场景名称": "如肺炎、非肺炎、新生儿必须治疗、5岁以下儿童应治疗、未分类等详细描述",
            "首选用药": [
              "【药物1: 剂量 频次 给药途径】",
              "【药物2】"
            ] 或 null,
            "次选用药": [
              "【药物1】",
              "【药物2】"
            ] 或 null,
            "联合用药": [
              "【药物1, 药物2】"
            ] 或 null,
            "其他有效药物": [
              {{
                "药物名称": "药物名称",
                "备注": "说明信息"
              }}
            ] 或 null
          }}
        ]
      }}
    ]

    ---

    下面是需要处理的表格文本：
{table_text}
"""
    return prompt

# -----------------------------
# 调用 Qwen API
# -----------------------------
def call_qwen(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
        "max_tokens": 5000,
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    # Qwen 兼容 OpenAI 风格
    content = data["choices"][0]["message"]["content"]
    return content

def continue_call_qwen(conversation_history):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": conversation_history,
        "temperature": 0.0,
        "max_tokens": 5000,
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    # Qwen 兼容 OpenAI 风格
    content = data["choices"][0]["message"]["content"]
    return content

# -----------------------------
# 主程序
# -----------------------------
def main():
    # 读取整个Excel文件
    excel_text = read_entire_excel(EXCEL_FILE)
    print(f"Excel文件总字符数: {len(excel_text)}")
    
    # 构建提示词
    prompt = build_prompt(excel_text)
    
    # 初始化对话历史
    conversation_history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    
    # 调用Qwen API
    try:
        result_json_str = ""
        while True:
            response_content = continue_call_qwen(conversation_history)
            result_json_str += response_content
            print(f"API返回内容长度: {len(response_content)}")
            print(f"API返回内容前500字符:\n{response_content[:500]}")
            
            # 检查是否需要继续
            if "是否需要继续处理下一步" in response_content or "请确认是否需要继续处理下一步" in response_content:
                conversation_history.append({"role": "assistant", "content": response_content})
                conversation_history.append({"role": "user", "content": "继续"})
            else:
                break
        
        # 保存结果到文件
        OUTPUT_JSON = f"direct_output_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            f.write(result_json_str)
        print(f"已保存 JSON 到 {OUTPUT_JSON}")
        
    except Exception as e:
        print(f"调用失败: {e}")

if __name__ == "__main__":
    main()