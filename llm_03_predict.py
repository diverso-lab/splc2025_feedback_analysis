import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

# Etiquetas usadas en el entrenamiento
LABELS = ['testing', 'fix', 'mock', 'config', 'model', 'extension', 'refactor', 'obsolete']

# Cargar modelo y tokenizer desde la carpeta 'model'
model = AutoModelForSequenceClassification.from_pretrained("./model")
tokenizer = AutoTokenizer.from_pretrained("./model")

model.eval()

def predict_tags(text, threshold=0.5):
    # Tokenizar entrada
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    # Inferencia
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.sigmoid(logits).squeeze().cpu().numpy()

    # Aplicar umbral a cada etiqueta
    predicted_labels = [label for label, prob in zip(LABELS, probs) if prob >= threshold]

    return predicted_labels, probs

# Ejemplo de uso
if __name__ == "__main__":
    text = input("🔍 Enter text for tagging (commit, issue, etc):\n> ")
    labels, scores = predict_tags(text)

    print("\n📌 Predicted labels:")
    for label, score in zip(LABELS, scores):
        print(f"- {label:<10} : {score:.3f} {'✅' if label in labels else ''}")
