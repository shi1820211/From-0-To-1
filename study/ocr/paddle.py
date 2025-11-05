from paddleocr import PaddleOCR
import csv
import re

# 初始化 PaddleOCR
# 使用中英文模型（根据图像语言调整 lang 参数，例如 'en' 用于英文，'ch' 用于中文）
ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # lang='en' 如果图像是英文

# 图像路径（替换为您的图像文件）
image_path = 'knowledge_graph_image.jpg'  # 例如：'kg_image.png'

# 使用 PaddleOCR 识别文本
result = ocr.ocr(image_path, cls=True)

# 提取文本内容
text_lines = []  # 存储每行的文本
for line in result:
    line_text = ' '.join([word_info[1][0] for word_info in line])  # 合并一行中的多个单词
    text_lines.append(line_text)

# 解析文本为知识图谱三元组（实体1, 关系, 实体2）
# 假设每行文本格式为 "实体1 关系 实体2"（以空格分隔）
triples = []
for text in text_lines:
    parts = text.split()  # 简单分割
    if len(parts) >= 3:  # 至少三个部分：实体1、关系、实体2
        entity1 = parts[0]
        relation = parts[1]
        entity2 = ' '.join(parts[2:])  # 实体2可能包含多个词
        triples.append((entity1, relation, entity2))
    else:
        print(f"跳过无法解析的行: {text}")  # 记录无法解析的行

# 保存为 CSV 文件
csv_filename = 'knowledge_graph.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:  # utf-8-sig 支持中文Excel
    writer = csv.writer(csvfile)
    writer.writerow(['Entity1', 'Relation', 'Entity2'])  # 写入标题行
    for triple in triples:
        writer.writerow(triple)

print(f"知识图谱内容已保存到 {csv_filename}")
print(f"共解析出 {len(triples)} 个三元组")
