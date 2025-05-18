import json
import torch
from sklearn.preprocessing import MultiLabelBinarizer
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
)
from transformers.training_args import TrainingArguments

LABELS = ['testing', 'fix', 'mock', 'config', 'model', 'extension', 'refactor', 'obsolete']
mlb = MultiLabelBinarizer(classes=LABELS)

# Cargar y procesar dataset desde JSONL
raw_dataset = Dataset.from_json("dataset.jsonl")

# Vectorizar etiquetas multi-hot
multi_hot_labels = mlb.fit_transform(raw_dataset["labels"])
raw_dataset = raw_dataset.remove_columns("labels").add_column("labels", multi_hot_labels.tolist())

# Tokenizador base
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# Tokenización
def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, padding=False)

dataset = raw_dataset.map(tokenize, batched=True)
dataset = dataset.train_test_split(test_size=0.1)

# Modelo preentrenado adaptado a clasificación multietiqueta
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(LABELS),
    problem_type="multi_label_classification"
)

# Métrica básica: accuracy multietiqueta
def compute_metrics(p):
    logits, labels = p
    preds = (torch.sigmoid(torch.tensor(logits)) > 0.5).int().numpy()
    labels = labels.astype(int)
    acc = (preds == labels).mean()
    return {"accuracy": acc}

# Collate personalizado para evitar errores de padding en labels
def collate_fn(batch):
    # Extraer inputs y labels por separado
    inputs = [{k: v for k, v in item.items() if k != "labels"} for item in batch]
    labels = [torch.tensor(item["labels"], dtype=torch.float) for item in batch]

    # Padding dinámico de los inputs (textos)
    padded_inputs = tokenizer.pad(
        inputs,
        padding=True,
        return_tensors="pt"
    )


    # Insertar labels como tensor final
    padded_inputs["labels"] = torch.stack(labels)
    return padded_inputs

# Configuración de entrenamiento
training_args = TrainingArguments(
    output_dir="./model",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    logging_dir="./logs"
)

# Entrenador
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
    data_collator=collate_fn
)

# Entrenamiento y guardado
trainer.train()
model.save_pretrained("model")
tokenizer.save_pretrained("model")
print("✅ Entrenamiento completado y modelo guardado en ./model")
