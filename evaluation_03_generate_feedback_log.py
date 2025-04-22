import os
import json
from tqdm import tqdm

# Carpeta donde están los traceability maps por fork
evaluation_dir = "evaluation"
feedback_log = []

# Recorrer todos los forks
for fork_folder in tqdm(os.listdir(evaluation_dir), desc="Construyendo feedback log"):
    fork_path = os.path.join(evaluation_dir, fork_folder)
    traceability_file = os.path.join(fork_path, "traceability_map.json")

    if not os.path.exists(traceability_file):
        continue

    with open(traceability_file) as f:
        traceability_map = json.load(f)

    for entry in traceability_map:
        if len(entry) == 4:
            feature, source_type, tag, timestamp = entry
            feedback_log.append([feature, source_type, tag, fork_folder, timestamp])
        else:
            print(f"⚠️  Formato inesperado en {fork_folder}: {entry}")

# Guardar en feedback_log.json
with open("feedback_log.json", "w") as f:
    json.dump(feedback_log, f, indent=2)

print(f"✅ Feedback log generado con {len(feedback_log)} entradas.")
