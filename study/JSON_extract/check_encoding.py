import pandas as pd

# 读取Excel文件
file_path = r'C:\Users\autobio\PycharmProjects\study\JSON_extract\热病和ABX菌整理-20240116.xlsx'

df = pd.read_excel(file_path, header=None)

# 打印前100行数据
print(df.head(100))

# 检查数据类型
dtypes = df.dtypes
print(dtypes)

# 检查是否有任何非UTF-8字符
for col in df.columns:
    if df[col].dtype == object:  # 只检查字符串列
        try:
            df[col].str.encode('utf-8')
        except UnicodeEncodeError as e:
            print(f"列 {col} 包含非UTF-8字符: {e}")