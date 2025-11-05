import requests
import time
import json
import re
import pandas as pd
from datetime import datetime
import os
import xlrd  # 用于读取.xls文件

# API配置
url = "http://172.31.11.52:8012/pathogen_diagnosis"
headers = {
    "Authorization": "939c63377a42cd98cceeeae914ea3ab6329f68c1602d86da24648b54b6abafce",
    "AppKey": "3a09f600c5eabe57104901cc02d706b3",
    "Timestamp": "1741410006121",
    "Content-Type": "application/json"
}

# 存储不一致结果的列表
discrepancy_records = []


def read_excel_file(file_path):
    """读取Excel文件内容"""
    try:
        # 使用xlrd读取.xls文件
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_index(0)  # 获取第一个工作表

        # 读取所有行
        rows = []
        for row_idx in range(sheet.nrows):
            row = sheet.row_values(row_idx)
            rows.append(row)

        return rows
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return None


def parse_excel_content(rows):
    """解析Excel内容，返回病菌数据列表和表头信息"""
    if not rows:
        return [], []

    # 提取表头
    headers = []
    if len(rows) > 0:
        headers = [str(cell).strip() for cell in rows[0]]

    bacteria_data = []

    # 处理每一行（从第二行开始）
    for i in range(1, len(rows)):
        row = rows[i]

        # 跳过空行
        if not row or not any(row):
            continue

        # 确保有足够的列
        if len(row) < 4:
            # 尝试填充缺失列
            row.extend([""] * (4 - len(row)))

        bacteria_name = str(row[0]).strip()
        pathogenic_specimens = str(row[1]).strip() if len(row) > 1 else ""
        colonized_specimens = str(row[2]).strip() if len(row) > 2 else ""
        normal_specimens = str(row[3]).strip() if len(row) > 3 else ""

        # 跳过空行
        if not bacteria_name:
            continue

        bacteria_data.append({
            "菌种": bacteria_name,
            "致病标本": pathogenic_specimens,
            "定植标本": colonized_specimens,
            "正常标本": normal_specimens
        })

    return bacteria_data, headers


def extract_sample_types_and_counts(specimen_str):
    """从标本类型字符串中提取所有样本类型和对应的菌落计数"""
    if not specimen_str:
        return []

    # 按顿号分割，得到所有样本类型
    specimens = specimen_str.split('、')

    # 清理每个样本类型并提取菌落计数
    result = []
    for specimen in specimens:
        specimen = specimen.strip()
        if specimen:
            # 提取基础名称：按"且"、"（"、"且"等分割，取第一部分
            base_type = re.split(r'且|（|且有|且无', specimen)[0].strip()

            # 提取菌落计数
            colony_count = ""

            # 检查是否包含"优势生长"
            if "优势生长" in specimen:
                colony_count = "++"
            # 检查是否包含"菌落计数"，提取定量值
            elif "菌落计数" in specimen:
                # 使用正则表达式提取菌落计数值
                match = re.search(r'菌落计数\s*([^、]*)', specimen)
                if match:
                    colony_count = match.group(1).strip()
                else:
                    # 如果没有明确的值，使用默认值
                    colony_count = ">=103CFU/ml"

            result.append({
                "sample_type": base_type,
                "colony_count": colony_count
            })

    return result


def extract_category_from_header(header):
    """从表头中提取分类信息"""
    if not header:
        return "未知"

    # 从表头中提取分类关键词
    if "致病菌" in header:
        return "致病菌"
    elif "定植菌" in header:
        return "定植菌"
    elif "正常菌" in header:
        return "正常菌"
    else:
        return "未知"


def extract_conclusion_from_response(content):
    """从API响应内容中提取致病菌结论"""
    if not content:
        return "未知"

    match = re.search(r'<span[^>]*>([^<]+)</span>', content)
    if match:
        conclusion = match.group(1).strip()
        if "致病" in conclusion:
            return "致病菌"
        elif "定植" in conclusion:
            return "定植菌"
        elif "正常" in conclusion:
            return "正常菌"
        elif "污染" in conclusion:
            return "污染菌"
        else:
            return conclusion  # 若是其他类别，原样返回

    # 如果没有span结构，再退回老的正则逻辑
    patterns = [
        r'结论[：:]\s*([^\n。]+)',
        r'致病菌判断[：:]\s*([^\n。]+)',
        r'判断[：:]\s*([^\n。]+)',
        r'为([^，。\n]+)菌'
    ]
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            conclusion = match.group(1).strip()
            if "致病" in conclusion:
                return "致病菌"
            elif "定植" in conclusion:
                return "定植菌"
            elif "正常" in conclusion:
                return "正常菌"
            elif "污染" in conclusion:
                return "污染菌"
    return "未知"


def check_and_record_discrepancy(bacteria_name, sample_type, expected_category, actual_conclusion):
    """检查分类是否一致，不一致则记录，并立即打印结果"""
    # 总是打印比较结果
    print(f"比较结果 - 菌种: {bacteria_name}, 样本类型: {sample_type}")
    print(f"表格分类: {expected_category}, API结论: {actual_conclusion}")

    if expected_category != actual_conclusion and expected_category != "未知":
        discrepancy_records.append({
            "菌种": bacteria_name,
            "样本类型": sample_type,
            "表格分类": expected_category,
            "API结论": actual_conclusion
        })

        print(f"❌ 分类不一致！")
        print("---" * 20)
        return True
    else:
        print(f"✅ 分类一致")
        print("---" * 20)
        return False


def send_api_request(bacteria_data, bacteria_name, sample_type, colony_count, expected_category):
    """发送API请求并处理响应，立即比较结果"""
    # 构建payload
    payload = {
        "report": {
            "患者信息": {
                "姓名": "王素萍",
                "患者编号": "00446731",
                "性别": "女",
                "年龄": "45岁",
                "标本编号": "T240418502",
                "初诊": "",
                "症状": "",
                "体征": ""
            },
            "培养数据": {
                "培养日期": "2025-07-15T00:00:00",
                "样本类型": sample_type,
                "菌种": bacteria_name,
                "菌落计数": colony_count
            },
            "生免数据": {}
        }
    }

    try:
        # 发送请求
        response = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False),
            stream=True,
            timeout=30  # 添加超时设置
        )

        full_content = ""
        print(f"处理病菌: {bacteria_name}")
        print(f"样本类型: {sample_type}, 菌落计数: {colony_count}")
        print(f"响应状态码: {response.status_code}")

        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return

        # 处理流式响应
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8').strip()
                if line_str.startswith("data: "):
                    json_str = line_str[len("data: "):]
                    try:
                        data_dict = json.loads(json_str)
                        inner_data = data_dict.get("data")
                        name = data_dict.get("name")

                        if inner_data is None:
                            continue

                        if data_dict.get('done') == True:
                            break

                        if name == "致病菌判断":
                            # 修复：检查inner_data的类型
                            if isinstance(inner_data, dict):
                                content = inner_data.get("message", {}).get("content", "")
                                full_content += content
                            elif isinstance(inner_data, list):
                                # 如果是列表，遍历每个元素
                                for item in inner_data:
                                    if isinstance(item, dict):
                                        item_content = item.get("message", {}).get("content", "")
                                        full_content += item_content
                            else:
                                print(f"未知的inner_data类型: {type(inner_data)}")
                        elif name == "耐药机制分析":
                            break
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"解析JSON时出错: {e}")
                        print(f"原始数据: {json_str}")
                        continue

        print(f"响应内容: {full_content}")

        # 提取结论并立即检查是否一致
        actual_conclusion = extract_conclusion_from_response(full_content)

        # 立即检查分类是否一致并记录
        check_and_record_discrepancy(bacteria_name, sample_type, expected_category, actual_conclusion)

        return full_content

    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return None


def save_discrepancies_to_excel():
    """将不一致的结果保存到Excel文件"""
    if not discrepancy_records:
        print("没有发现分类不一致的记录")
        return

    # 创建DataFrame
    df = pd.DataFrame(discrepancy_records)

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"菌种分类不一致记录_{timestamp}.xlsx"

    # 保存到Excel
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"不一致记录已保存到: {filename}")

    # 显示统计信息
    print(f"\n共发现 {len(discrepancy_records)} 条分类不一致记录")
    print("不一致记录统计:")
    print(df.groupby(['表格分类', 'API结论']).size().reset_index(name='计数'))


def main():
    """主函数"""
    # 获取文件路径
    file_path = input("请输入Excel数据文件路径: ").strip()

    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        return

    # 读取文件内容
    excel_rows = read_excel_file(file_path)
    if not excel_rows:
        print("无法读取文件内容")
        return

    # 解析Excel内容
    bacteria_data, headers = parse_excel_content(excel_rows)

    if not bacteria_data:
        print("未找到有效的病菌数据")
        return

    # 从表头中提取分类信息
    header_categories = []
    if len(headers) >= 4:
        # 提取第二、三、四列的表头分类
        header_categories = [
            extract_category_from_header(headers[1]),  # 第二列表头
            extract_category_from_header(headers[2]),  # 第三列表头
            extract_category_from_header(headers[3])  # 第四列表头
        ]
    else:
        # 如果表头不完整，使用默认分类
        header_categories = ["致病菌", "定植菌", "正常菌"]

    print(f"表头分类: {header_categories}")
    print(f"共找到 {len(bacteria_data)} 种病菌")
    print("开始处理...")

    # 为每种病菌的每个样本类型发送请求
    request_count = 0
    for i, data in enumerate(bacteria_data):
        print(f"\n处理病菌: {data['菌种']}")

        # 提取所有三列的样本类型和对应的菌落计数
        sample_types_and_counts = []

        # 处理致病标本列（第二列）
        pathogenic_samples = extract_sample_types_and_counts(data["致病标本"])
        for sample in pathogenic_samples:
            sample["expected_category"] = header_categories[0]  # 使用第二列表头的分类
            sample_types_and_counts.append(sample)

        # 处理定植标本列（第三列）
        colonized_samples = extract_sample_types_and_counts(data["定植标本"])
        for sample in colonized_samples:
            sample["expected_category"] = header_categories[1]  # 使用第三列表头的分类
            sample_types_and_counts.append(sample)

        # 处理正常标本列（第四列）
        normal_samples = extract_sample_types_and_counts(data["正常标本"])
        for sample in normal_samples:
            sample["expected_category"] = header_categories[2]  # 使用第四列表头的分类
            sample_types_and_counts.append(sample)

        if not sample_types_and_counts:
            print(f"  未找到样本类型，跳过")
            continue

        # 为每个样本类型发送请求
        for j, item in enumerate(sample_types_and_counts):
            request_count += 1
            sample_type = item["sample_type"]
            colony_count = item["colony_count"]
            expected_category = item["expected_category"]

            print(f"[{request_count}] 样本类型: {sample_type}, 菌落计数: {colony_count}, 预期分类: {expected_category}")

            # 发送API请求并立即比较结果
            result = send_api_request(bacteria_data, data["菌种"], sample_type, colony_count, expected_category)

            # 添加延迟，避免API速率限制
            if request_count % 10 == 0:  # 每10个请求延迟一次
                time.sleep(2)
            else:
                time.sleep(0.5)

    # 保存不一致记录到Excel
    save_discrepancies_to_excel()

    print(f"\n处理完成! 共发送 {request_count} 个请求")


if __name__ == "__main__":
    main()