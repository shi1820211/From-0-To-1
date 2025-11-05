import pandas as pd
import requests
import json

# -----------------------------
# 配置参数
# -----------------------------
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-96b5857ed3764061b283d3b06e4143d6"  # 替换为你的 API Key
EXCEL_FILE = r"C:\Users\autobio\PycharmProjects\study\JSON_extract\热病和ABX菌整理-20240116.xlsx"
OUTPUT_JSON = "output.json"
MAX_ROWS_PER_CHUNK = 50  # 每块最大行数，可根据表格大小调整

# -----------------------------
# 读取 Excel 文本
# -----------------------------
def read_excel_text(file_path):
    xls = pd.ExcelFile(file_path)
    all_text = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        for start_row in range(0, len(df), MAX_ROWS_PER_CHUNK):
            chunk = df.iloc[start_row:start_row + MAX_ROWS_PER_CHUNK]
            lines = []
            for row in chunk.itertuples(index=False):
                row_text = [str(cell) for cell in row if pd.notna(cell)]
                if row_text:
                    lines.append(" ".join(row_text))
            if lines:
                all_text.append("\n".join(lines))
    return all_text

# -----------------------------
# 构建完整提示词（保留全部任务要求和 few-shot 示例）
# -----------------------------
def build_prompt(table_text):
    prompt = f"""
    你是一名医学信息结构化提取与逻辑推断助手，负责将感染治疗表格中的内容转化为标准 JSON 格式，并根据药物适用条件和药物逻辑关系自动整理。

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

    ### few-shot 示例开始

    [
      {{
        "菌种名称": "无色杆菌",
        "感染场景": [
          {{
            "场景名称": "肺炎",
            "首选用药": [
              "【亚胺培南】",
              "【美罗培南】"
            ],
            "次选用药": [
              "【TMP-SMX】"
            ],
            "联合用药": null,
            "其他有效药物": [
              {{
                "药物名称": "多尼培南",
                "备注": "多尼培南不用于肺炎"
              }},
              {{
                "药物名称": "头孢他啶",
                "备注": "部分菌株敏感"
              }},
              {{
                "药物名称": "哌拉西林/他唑巴坦",
                "备注": "部分菌株敏感"
              }},
              {{
                "药物名称": "氨基糖苷类",
                "备注": "耐药"
              }},
              {{
                "药物名称": "头孢菌素类",
                "备注": "耐药"
              }},
              {{
                "药物名称": "氟唑诺酮类",
                "备注": "耐药"
              }}
            ]
          }},
          {{
            "场景名称": "非肺炎",
            "首选用药": [
              "【亚胺培南】",
              "【美罗培南】",
              "【多尼培南】"
            ],
            "次选用药": [
              "【TMP-SMX】"
            ],
            "联合用药": null,
            "其他有效药物": [
              {{
                "药物名称": "头孢他啶",
                "备注": "部分菌株敏感"
              }},
              {{
                "药物名称": "哌拉西林/他唑巴坦",
                "备注": "部分菌株敏感"
              }},
              {{
                "药物名称": "氨基糖苷类",
                "备注": "耐药"
              }},
              {{
                "药物名称": "头孢菌素类",
                "备注": "耐药"
              }},
              {{
                "药物名称": "氟唑诺酮类",
                "备注": "耐药"
              }}
            ]
          }}
        ]
      }},
      {{
        "菌种名称": "幽门螺杆菌",
        "感染场景": [
          {{
            "场景名称": "未分类",
            "首选用药": null,
            "次选用药": null,
            "联合用药": null,
            "其他有效药物": null
          }}
        ]
      }},
      {{
        "菌种名称": "分枝杆菌",
        "感染场景": [
          {{
            "场景名称": "新生儿必须治疗（有发热、基线胸部X线片异常）",
            "首选用药": [
              "【异烟肼】"
            ],
            "次选用药": null,
            "联合用药": null,
            "其他有效药物": null
          }},
          {{
            "场景名称": "5岁以下儿童应予治疗",
            "首选用药": [
              "【异烟肼】"
            ],
            "次选用药": null,
            "联合用药": null,
            "其他有效药物": null
          }},
          {{
            "场景名称": "较大儿童和成人: 第1年感染风险2%-4%",
            "首选用药": [
              "【异烟肼】"
            ],
            "次选用药": null,
            "联合用药": null,
            "其他有效药物": null
          }}
        ]
      }},
      {{
        "菌种名称": "曲霉菌",
        "感染场景": [
          {{
            "场景名称": "未分类",
            "首选用药": [
              "【伏立康唑: 第一天6mg/kg IV q12h，然后4mg/kg IV q12h】",
              "【200mg po g12h (体重≥40kg)】",
              "【100mg po g12h (体重＜40kg)】"
            ],
            "次选用药": [
              "【硫酸艾沙康唑 负荷剂量 372mg (等价于艾沙康唑200mg) IV/口服 q8h x6剂，之后372mg IV/口服 Qd】",
              "【脂质体两性霉素 B (LAB) (L-AmB) 3~5mg/(kg·d) IV】",
              "【两性霉素 B 脂质体复合物 (ABLC) 5mg/(kg·d) IV】",
              "【卡泊芬净 70mg/d，然后 50mg/d IV】",
              "【米卡芬净 NAI 100mg bid】",
              "【泊沙康唑 NAI 200mg qid，病情稳定后400mg bid】"
            ],
            "联合用药": [
              "【伏立康唑, 棘白菌素类】"
            ],
            "其他有效药物": null
          }}
        ]
      }}
    ]

    ---

    下面是需要处理的表格文本：
    {table_text}
    """+ table_text


    return prompt

# -----------------------------
# 调用模型
# -----------------------------
def call_model(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"APPCODE {API_KEY}"
    }
    data = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "extra_body": {"enable_thinking": False},
        "temperature": 0.0,
        "max_tokens": 5000
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    content = result["result"]["choices"][0]["message"]["content"]
    return content

# -----------------------------
# 合并相同菌种
# -----------------------------
def merge_by_species(results_list):
    merged = {}
    for block_str in results_list:
        try:
            block_data = json.loads(block_str)
        except Exception:
            continue
        for item in block_data:
            species = item["菌种名称"]
            if species not in merged:
                merged[species] = {"菌种名称": species, "感染场景": []}
            merged[species]["感染场景"].extend(item.get("感染场景", []))
    return list(merged.values())

# -----------------------------
# 主程序
# -----------------------------
def main():
    chunks = read_excel_text(EXCEL_FILE)
    all_results = []

    for i, chunk_text in enumerate(chunks):
        print(f"正在处理第 {i + 1}/{len(chunks)} 块...")
        prompt = build_prompt(chunk_text)
        try:
            result_json_str = call_model(prompt)
            all_results.append(result_json_str)
        except Exception as e:
            print(f"第 {i + 1} 块调用失败: {e}")

    merged_results = merge_by_species(all_results)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(merged_results, f, ensure_ascii=False, indent=2)

    print(f"已保存 JSON 到 {OUTPUT_JSON}")

if __name__ == "__main__":
    main()


# 模型调用失败