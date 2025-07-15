# 使用hugging face 中的数据集
from datasets import load_dataset
from transformers import AutoTokenizer



dataset = load_dataset('imdb',split='train[:100]',trust_remote_code=True)
print(dataset[:2])
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

print(dataset.features)
print(dataset.column_names)

def tokenization(example):
    return tokenizer(
        example['text'],
        truncation=True,
        max_length=512,
        padding=True
    )

final_datasets=dataset.map(
    tokenization,
    batched=True,
    batch_size=8,
    remove_columns=['text']
)

print(final_datasets.column_names)
final_datasets.set_format(
    type='torch',
    columns=['label', 'input_ids', 'token_type_ids', 'attention_mask']
)
print(final_datasets[:2])
