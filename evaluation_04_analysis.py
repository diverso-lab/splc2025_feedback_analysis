import json
from collections import defaultdict, Counter

# Cargar el feedback log
with open("feedback_log.json") as f:
    feedback_log = json.load(f)

# Estructuras para análisis
feature_tags = defaultdict(list)
tag_feature_count = defaultdict(Counter)

# Agrupar
for feature, source_type, tag, fork, timestamp in feedback_log:
    feature_tags[feature].append(tag)
    tag_feature_count[tag][feature] += 1

# Funciones de impresión
def print_section(title):
    print("\n" + "="*len(title))
    print(title)
    print("="*len(title))

def print_feature_list(title, tag):
    print_section(title)
    for feature, count in tag_feature_count[tag].most_common():
        print(f"- {feature}: {count} ocurrencias")

def print_composite_section(title, tags):
    print_section(title)
    score = Counter()
    for tag in tags:
        for feature, count in tag_feature_count[tag].items():
            score[feature] += count
    for feature, count in score.most_common():
        print(f"- {feature}: {count} ocurrencias ({', '.join(set(feature_tags[feature]) & set(tags))})")

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
print(f"Total de entradas en el feedback log: {len(feedback_log)}")
