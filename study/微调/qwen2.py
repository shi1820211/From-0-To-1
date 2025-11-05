from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
import torch

# ------------------------------
# 1. 加载模型与Tokenizer
# ------------------------------
model_name = "Qwen/Qwen2-7B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float16)

# ------------------------------
# 2. 数据集加载
# ------------------------------
dataset = load_dataset("wikitext", "wikitext-103-v1")
def tokenize_fn(examples):
    return tokenizer(examples['text'], truncation=True, padding='max_length', max_length=512)

tokenized_datasets = dataset.map(tokenize_fn, batched=True)

# ------------------------------
# 3. 训练参数设置
# ------------------------------
training_args = TrainingArguments(
    output_dir="./qwen_finetune",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=8,
    evaluation_strategy="steps",
    eval_steps=500,
    save_steps=1000,
    learning_rate=5e-5,
    weight_decay=0.01,
    warmup_steps=100,
    logging_steps=50,
    fp16=True,
    save_total_limit=3,
    num_train_epochs=1
)

# ------------------------------
# 4. Trainer初始化
# ------------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['validation']
)

# ------------------------------
# 5. 开始微调
# ------------------------------
trainer.train()
