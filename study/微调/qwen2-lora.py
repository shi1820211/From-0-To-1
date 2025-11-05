from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
import torch

# ------------------------------
# 1. 加载模型 & tokenizer
# ------------------------------
model_name = "Qwen/Qwen2-7B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype=torch.float16
)

# ------------------------------
# 2. LoRA 配置 & 注入
# ------------------------------
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,  # LM类型
    r=16,                           # 低秩矩阵秩
    lora_alpha=32,                  # 缩放系数
    target_modules=["q_proj","v_proj"],  # 注入LoRA的模块
    lora_dropout=0.05,              # dropout
    bias="none"
)

model = get_peft_model(model, lora_config)  # LoRA注入
model.print_trainable_parameters()          # 查看哪些参数被微调

# ------------------------------
# 3. 数据集 & tokenization
# ------------------------------
dataset = load_dataset("wikitext", "wikitext-103-v1")
def tokenize_fn(examples):
    return tokenizer(examples['text'], truncation=True, padding='max_length', max_length=512)

tokenized_datasets = dataset.map(tokenize_fn, batched=True)

# ------------------------------
# 4. 训练参数
# ------------------------------
training_args = TrainingArguments(
    output_dir="./qwen_lora_finetune",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=8,
    evaluation_strategy="steps",
    eval_steps=500,
    save_steps=1000,
    learning_rate=3e-4,    # LoRA一般可以用稍大学习率
    weight_decay=0.01,
    warmup_steps=100,
    logging_steps=50,
    fp16=True,
    save_total_limit=3,
    num_train_epochs=1
)

# ------------------------------
# 5. Trainer 初始化
# ------------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['validation']
)

# ------------------------------
# 6. 开始训练
# ------------------------------
trainer.train()

# ------------------------------
# 7. 保存 LoRA 权重（而不是全量模型）
# ------------------------------
model.save_pretrained("./qwen_lora_finetuned")
