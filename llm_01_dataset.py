import os
import json
from tqdm import tqdm

# Diccionario de palabras clave por etiqueta
KEYWORDS = {
    'testing': ['test', 'testing', 'ci', 'unit', 'integration'],
    'fix': ['fix', 'bug', 'error', 'fail'],
    'mock': ['mock', 'stub'],
    'config': ['config', 'configuration', 'setup'],
    'model': ['model', 'schema'],
    'extension': ['extend', 'extension', 'feature'],
    'refactor': ['refactor', 'restructure'],
    'obsolete': ['obsolete', 'deprecated', 'remove']
}

def extract_tags(text):
    text = text.lower()
    return [tag for tag, keywords in KEYWORDS.items() if any(word in text for word in keywords)]

def collect_texts_from_folder(folder):
    dataset_entries = []

    for file_type in ['commits', 'issues', 'pulls']:
        path = os.path.join(folder, f"{file_type}.json")
        if not os.path.exists(path):
            continue

        with open(path, 'r') as f:
            items = json.load(f)

        for item in items:
            if file_type == 'commits':
                text = item.get('commit', {}).get('message', '')
            else:
                text = item.get('title', '')
            tags = extract_tags(text)
            if tags:
                dataset_entries.append({"text": text.strip(), "labels": tags})

    return dataset_entries

# Ruta raíz donde están los forks
EVAL_DIR = "evaluation"
dataset = []

for fork_folder in tqdm(os.listdir(EVAL_DIR), desc="Procesando forks"):
    folder_path = os.path.join(EVAL_DIR, fork_folder)
    if not os.path.isdir(folder_path):
        continue
    dataset.extend(collect_texts_from_folder(folder_path))

# Guardar dataset en JSONL
with open("dataset.jsonl", "w") as f:
    for entry in dataset:
        json.dump(entry, f)
        f.write("\n")

print(f"✅ Dataset generado con {len(dataset)} entradas.")
