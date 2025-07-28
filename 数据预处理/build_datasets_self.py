import re
from datasets import load_dataset
from transformers import AutoTokenizer
# 加载数据
dataset = load_dataset("json",
                       data_files="C:\\Users\\autobio\\PycharmProjects\\PythonProject2\\数据预处理\\mydata.jsonl",
                       split="train"
                       )
# 数据清洗
def clean_text(example):
    texts = example["text"]
    cl_text =[]
    for t in texts:
        t1= re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9，。！？]", "", t)
        t1 = t1.strip()
        cl_text.append(t1)

    return {"text":cl_text}

cleaned_dataset=dataset.map(clean_text,batched=True,batch_size=7)
print(cleaned_dataset[2])

# 分词
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
def tokenize(example):
    return tokenizer(example["text"],
                     padding="max_length",
                     max_length=512,
                     truncation=True
    )

tk_text =cleaned_dataset.map(tokenize,batched=True,batch_size=7)
print(tk_text)
print(tk_text.column_names)

tk_text.set_format("torch",
                    columns=['text', 'label', 'input_ids', 'token_type_ids', 'attention_mask']
)
print(tk_text[2])
