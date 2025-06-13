import json
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
import os

# =======================
# CONFIGURACIÓN INICIAL
# =======================

TRACEABILITY_FILE = 'proof_of_concept/traceability_map.json'
OUTPUT_DIR = 'analysis_charts'

# Crear carpeta si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Tags relevantes por pregunta del paper
TAG_GROUPS = {
    'testing_needed': ['testing', 'fix', 'error'],
    'mock_usage': ['mock'],
    'refactor_needed': ['mock', 'refactor'],
    'high_activity': ['testing', 'model', 'config'],
    'ci_cd_issues': ['config', 'model', 'fix'],
}

# Títulos bonitos para los gráficos
TITLES = {
    'testing_needed': '🔬 Features que necesitan más pruebas',
    'mock_usage': '🧪 Features con muchos mocks',
    'refactor_needed': '🔧 Features que requieren refactor para testabilidad',
    'high_activity': '📈 Features con mayor actividad (testing, model, config)',
    'ci_cd_issues': '⚙️ Features problemáticas en CI/CD',
}

# =======================
# CARGA DE DATOS
# =======================

with open(TRACEABILITY_FILE) as f:
    traceability_map = json.load(f)

# Agrupar por feature y contar tags
feature_tag_count = defaultdict(Counter)
for feature, source_type, tag in traceability_map:
    feature_tag_count[feature][tag] += 1

# Función auxiliar para contar tags por grupo
def sum_tags(counter, tags):
    return sum(counter[tag] for tag in tags)

# =======================
# GENERACIÓN DE GRÁFICAS
# =======================

def generate_chart(question_key, tags):
    data = [
        (feature, sum_tags(counter, tags))
        for feature, counter in feature_tag_count.items()
        if sum_tags(counter, tags) > 0
    ]
    if not data:
        return

    data.sort(key=lambda x: x[1], reverse=True)
    features, counts = zip(*data)

    plt.figure(figsize=(10, 5))
    plt.bar(features, counts)
    plt.title(TITLES[question_key])
    plt.ylabel('ocurrencies')
    plt.xlabel('Feature')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, f'{question_key}.png')
    plt.savefig(output_path)
    plt.close()

    print(f'[✓] Gráfico generado: {output_path}')

# Generar todas las gráficas
for key, tags in TAG_GROUPS.items():
    generate_chart(key, tags)
