import pandas as pd

# 读取Excel文件
file_path = r'C:\Users\autobio\PycharmProjects\study\JSON_extract\热病和ABX菌整理-20240116.xlsx'

df = pd.read_excel(file_path, header=None, engine='openpyxl')

# 打印前100行数据
print(df.head(100))

# 过滤掉非菌种名称的行
# 假设菌种名称行不包含'表'字且不为空
filtered_df = df[df.iloc[:, 0].notna() & ~df.iloc[:, 0].astype(str).str.contains('表')]

# 统计菌种名称
species_counts = filtered_df.iloc[:, 0].value_counts()

# 将统计结果保存到文件
with open('species_counts.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total species: {len(species_counts)}\n")
    f.write(species_counts.to_string())

print(f"Total species: {len(species_counts)}")