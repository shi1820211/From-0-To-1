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
MAX_ROWS_PER_CHUNK = 110  # 每块最大行数
MODEL_NAME = "qwen-plus"

# -----------------------------
# 读取 Excel 文本
# -----------------------------
def read_excel_text(file_path):
    xls = pd.ExcelFile(file_path)
    all_text = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        # 统计菌种名称出现次数
        species_counts = df.iloc[:, 0].value_counts()
        print(f"Sheet {sheet_name} 总共有 {len(species_counts)} 个不同的菌种")
        
        # 保留每个菌种第一次出现的行，去除重复
        seen_species = set()
        rows_to_keep = []
        for index, row in df.iterrows():
            species = row.iloc[0]
            if pd.notna(species) and species not in seen_species:
                seen_species.add(species)
                rows_to_keep.append(index)
        
        # 创建新的DataFrame，只保留每个菌种第一次出现的行
        df_unique = df.loc[rows_to_keep].reset_index(drop=True)
        
        print(f"Sheet {sheet_name} 去重后保留 {len(df_unique)} 行数据")
        
        total_rows = len(df_unique)
        for start_row in range(0, total_rows, MAX_ROWS_PER_CHUNK):
            end_row = min(start_row + MAX_ROWS_PER_CHUNK, total_rows)
            # 添加前后文叠加
            context_start = max(0, start_row - 10)  # 包含前一个块的最后10行
            context_end = min(total_rows, end_row + 10)  # 包含后一个块的第10行
            chunk = df_unique.iloc[context_start:context_end]
            lines = []
            for row in chunk.itertuples(index=False):
                row_text = [str(cell) for cell in row if pd.notna(cell)]
                if row_text:
                    lines.append(" ".join(row_text))
            if lines:
                all_text.append("\n".join(lines))
                print(f"添加数据块: 行 {context_start} 到 {context_end-1}")
                print(f"数据块内容前200字符: {(' '.join(lines))[:200]}\n")
    return all_text

# -----------------------------
# 构建提示词
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
    
    # 验证返回内容是否包含JSON格式数据
    if not content.strip().startswith("[") and not content.strip().startswith("```"):
        print(f"警告: API返回内容可能不包含JSON数据:\n{content[:500]}")
    
    # 增加详细日志输出
    print(f"API返回的完整内容:\n{content}")
    
    return content


# -----------------------------
# 合并相同菌种
# -----------------------------
# -----------------------------
# 合并相同菌种（改进版）
# -----------------------------
def extract_json_str(raw_str):
    # 去掉 Markdown 代码块标记
    raw_str = raw_str.strip()
    raw_str = re.sub(r"^```json\s*", "", raw_str)
    raw_str = re.sub(r"```$", "", raw_str)

    # 提取第一个 [ 开头 到 最后一个 ] 之间的内容
    match = re.search(r"\[.*\]", raw_str, re.S)
    if match:
        return match.group(0)
    return raw_str

def is_valid_json(json_str):
    """
    验证字符串是否为有效的JSON格式
    """
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False

def merge_by_species(results_list):
    merged = {}
    for i, block_str in enumerate(results_list):
        print(f"第 {i + 1} 块原始返回内容长度: {len(block_str)}")
        print(f"第 {i + 1} 块原始返回内容前500字符:\n{block_str[:500]}\n")
        
        try:
            json_str = extract_json_str(block_str)
            print(f"第 {i + 1} 块提取后的JSON字符串长度: {len(json_str)}")
            print(f"第 {i + 1} 块提取后的JSON字符串前500字符:\n{json_str[:500]}\n")
            
            # 验证提取后的JSON字符串是否有效
            if not is_valid_json(json_str):
                print(f"第 {i + 1} 块提取后的JSON字符串格式无效\n")
                continue
                
            block_data = json.loads(json_str)
        except Exception as e:
            print(f"第 {i + 1} 块 JSON 解析失败: {e}\n")
            continue

        if not isinstance(block_data, list):
            print(f"第 {i + 1} 块解析结果不是列表，跳过\n")
            continue

        for item in block_data:
            species = item.get("菌种名称")
            if not species:
                continue
            if species not in merged:
                merged[species] = {"菌种名称": species, "感染场景": [], "来源块": []}
            merged[species]["感染场景"].extend(item.get("感染场景", []))
            merged[species]["来源块"].append(i + 1)

    print(f"合并后的菌种数量: {len(merged)}")
    # 打印每个菌种的来源块信息
    for species, data in merged.items():
        print(f"菌种 {species} 来源于块: {data['来源块']}")
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
            result_json_str = call_qwen(prompt)
            print(f"第 {i + 1} 块返回内容长度: {len(result_json_str)}")
            print(f"第 {i + 1} 块返回内容前200字符:\n{result_json_str[:200]}\n")
            all_results.append(result_json_str)
        except Exception as e:
            print(f"第 {i + 1} 块调用失败: {e}\n")

    merged_results = merge_by_species(all_results)

    # 每次生成新文件
    OUTPUT_JSON = f"output_{time.strftime('%Y%m%d_%H%M%S')}.json"
    print(f"最终 merged_results 长度: {len(merged_results)}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(merged_results, f, ensure_ascii=False, indent=2)

    print(f"已保存 JSON 到 {OUTPUT_JSON}")

if __name__ == "__main__":
    main()