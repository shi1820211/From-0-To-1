from transformers import BertTokenizerFast, BertForTokenClassification, Trainer, TrainingArguments
from datasets import load_dataset
import numpy as np
from sklearn.metrics import f1_score

# ------------------------------
# 1. 模型与Tokenizer
# ------------------------------
model_name = "bert-base-chinese"
tokenizer = BertTokenizerFast.from_pretrained(model_name)
model = BertForTokenClassification.from_pretrained(model_name, num_labels=9)  # BIO标签

# ------------------------------
# 2. 数据集
# ------------------------------
dataset = load_dataset("msra_ner")
def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(examples['tokens'], truncation=True, is_split_into_words=True)
    labels = []
    for i, label in enumerate(examples['ner_tags']):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            else:
                label_ids.append(label[word_idx])
        labels.append(label_ids)
    tokenized_inputs["labels"] = labels
    return tokenized_inputs

tokenized_datasets = dataset.map(tokenize_and_align_labels, batched=True)

# ------------------------------
# 3. 训练参数
# ------------------------------
training_args = TrainingArguments(
    output_dir="./bert_ner_finetune",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    learning_rate=3e-5,
    evaluation_strategy="epoch",
    logging_steps=50,
    save_strategy="epoch",
    load_best_model_at_end=True
)

# ------------------------------
# 4. Metrics
# ------------------------------
def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=-1)
    labels = p.label_ids
    preds_flat = [p for pred, lab in zip(preds, labels) for p, l in zip(pred, lab) if l != -100]
    labels_flat = [l for pred, lab in zip(preds, labels) for p, l in zip(pred, lab) if l != -100]
    return {"f1": f1_score(labels_flat, preds_flat, average="micro")}

# ------------------------------
# 5. Trainer
# ------------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['validation'],
    compute_metrics=compute_metrics
)

trainer.train()
