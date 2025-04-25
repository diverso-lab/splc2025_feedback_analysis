import json
import os
from collections import defaultdict, Counter
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Configuración
FEEDBACK_LOG_PATH = "feedback_log_anonymous.json"
OUTPUT_FOLDER = "figures"
TOP_N_FEATURES = 10

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Cargar el feedback log
with open(FEEDBACK_LOG_PATH) as f:
    feedback_log = json.load(f)

# Agrupar por (feature, mes)
activity_by_feature_month = defaultdict(Counter)
for feature, source_type, tag, fork, timestamp in feedback_log:
    month = datetime.fromisoformat(timestamp).strftime("%Y-%m")
    activity_by_feature_month[feature][month] += 1

# Calcular total por feature
total_by_feature = {
    feature: sum(month_counts.values())
    for feature, month_counts in activity_by_feature_month.items()
}

# Top-N features más activas
top_features = sorted(total_by_feature.items(), key=lambda x: x[1], reverse=True)[:TOP_N_FEATURES]
top_feature_names = [f for f, _ in top_features]

# Extraer todos los meses únicos ordenados
all_months = sorted(
    {month for counts in activity_by_feature_month.values() for month in counts}
)

# Preparar los datos para graficar
feature_series = {
    feature: [activity_by_feature_month[feature].get(month, 0) for month in all_months]
    for feature in top_feature_names
}

# Graficar con texto muy grande
plt.figure(figsize=(14, 7))
for feature, series in feature_series.items():
    plt.plot(all_months, series, label=feature, linewidth=2)

plt.xlabel("Time (YYYY-MM)", fontsize=22)
plt.ylabel("Occurrences", fontsize=22)
plt.title("Top Active Features Over Time", fontsize=26)
plt.xticks(rotation=45, fontsize=20)
plt.yticks(fontsize=20)
plt.legend(fontsize=18)
plt.tight_layout()

# Guardar en PNG y SVG
plt.savefig(os.path.join(OUTPUT_FOLDER, "evolution_top_features.png"))
plt.savefig(os.path.join(OUTPUT_FOLDER, "evolution_top_features.svg"))
plt.close()

print("✅ Gráfica de evolución por feature generada con texto MUY ampliado.")
