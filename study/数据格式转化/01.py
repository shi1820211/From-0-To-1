import pandas as pd

df = pd.read_parquet("0000.parquet")


df.to_json("output.jsonl", orient="records", lines=True, force_ascii=False)