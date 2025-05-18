import torch
import numpy as np
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding
)
from sklearn.preprocessing import MultiLabelBinarizer

# Etiquetas disponibles
LABELS = ['testing', 'fix', 'mock', 'config', 'model', 'extension', 'refactor', 'obsolete']
mlb = MultiLabelBinarizer(classes=LABELS)

# Cargar dataset desde JSONL
dataset = Dataset.from_json("dataset.jsonl")

# Codificación multi-hot
multi_hot = mlb.fit_transform(dataset["labels"])
dataset = dataset.remove_columns("labels").add_column("labels", multi_hot.tolist())

# Cargar tokenizer
tokenizer = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")

# Tokenizar y transformar labels a float32
def preprocess(example):
    encoding = tokenizer(example["text"], truncation=True, padding="max_length")
    encoding["labels"] = torch.tensor(example["labels"], dtype=torch.float32)
    return encoding

# Aplicar tokenización
dataset = dataset.map(preprocess)

# Separar en train/test
dataset = dataset.train_test_split(test_size=0.1)

# Asegurar formato correcto
dataset["train"].set_format(type="torch")
dataset["test"].set_format(type="torch")

# Cargar modelo
model = AutoModelForSequenceClassification.from_pretrained(
    "answerdotai/ModernBERT-base",
    num_labels=len(LABELS),
    problem_type="multi_label_classification"
)

# Argumentos de entrenamiento (usa versión moderna de transformers)
args = TrainingArguments(
    output_dir="./model_modernbert",
    per_device_train_batch_size=8,
    num_train_epochs=3,
    logging_dir="./logs"
)

# Instanciar Trainer
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer),
)

# Entrenar modelo
trainer.train()

# Guardar modelo y tokenizer
model.save_pretrained("model_modernbert")
tokenizer.save_pretrained("model_modernbert")

print("✅ Entrenamiento completado")
