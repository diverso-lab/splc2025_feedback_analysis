import json
from collections import defaultdict, Counter

# Cargar el mapa de trazabilidad
with open('proof_of_concept/traceability_map.json') as f:
    traceability_map = json.load(f)

# Estructuras para agrupar datos
feature_tags = defaultdict(list)
tag_feature_count = defaultdict(Counter)

# Rellenar estructuras
for feature, source_type, tag in traceability_map:
    feature_tags[feature].append(tag)
    tag_feature_count[tag][feature] += 1

def print_section(title):
    print("\n" + "="*len(title))
    print(title)
    print("="*len(title))

def print_feature_list(title, tag):
    print_section(title)
    for feature, count in tag_feature_count[tag].most_common():
        print(f"- {feature}: {count} ocurrencies")

def print_composite_section(title, tags):
    print_section(title)
    score = Counter()
    for tag in tags:
        for feature, count in tag_feature_count[tag].items():
            score[feature] += count
    for feature, count in score.most_common():
        print(f"- {feature}: {count} ocurrencies ({', '.join(set(feature_tags[feature]) & set(tags))})")

# ===============================
# RESPUESTAS A LAS PREGUNTAS
# ===============================

# 🧪 Testing questions
print_section("🧪 TESTING QUESTIONS")

print_composite_section("¿Qué features necesitan más pruebas?", ['testing', 'fix', 'error'])
print_composite_section("¿Qué features usan muchos mocks?", ['mock'])
print_composite_section("¿Qué features están mal diseñadas para testeo (refactor)?", ['mock', 'refactor'])

# ✨ Feature evolution
print_section("✨ FEATURE QUESTIONS")

print_feature_list("¿Qué features están siendo extendidas?", 'extension')
print_feature_list("¿Qué features están siendo refactorizadas?", 'refactor')
print_feature_list("¿Qué features podrían eliminarse (obsolete)?", 'obsolete')
print_composite_section("¿Qué features tienen mucha actividad (testing + model + config)?", ['testing', 'model', 'config'])

# ⚙️ CI/CD questions
print_section("⚙️ CI/CD QUESTIONS")

print_feature_list("¿Qué features dan errores de configuración?", 'config')
print_feature_list("¿Qué features introducen nuevos modelos?", 'model')
print_feature_list("¿Qué features fallan a menudo (fix)?", 'fix')

# Total
print_section("✅ TOTAL")
print(f"Total de features analizadas: {len(feature_tags)}")
print(f"Total de entradas en el mapa: {len(traceability_map)}")
