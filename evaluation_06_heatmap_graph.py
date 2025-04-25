import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

# Cargar el feedback log
with open('feedback_log_anonymous.json') as f:
    feedback_log = json.load(f)

# Crear estructura: {feature: {tag: count}}
data = {}
for feature, source_type, tag, fork, timestamp in feedback_log:
    if feature not in data:
        data[feature] = {}
    if tag not in data[feature]:
        data[feature][tag] = 0
    data[feature][tag] += 1

# Convertir a DataFrame
df = pd.DataFrame.from_dict(data, orient='index').fillna(0).astype(int)

# Aplicar escala logarítmica
df_log = df.copy()
df_log[df_log > 0] = df_log[df_log > 0].applymap(lambda x: np.log10(x + 1))

# Ordenar por actividad total
df_log = df_log.loc[df.sum(axis=1).sort_values(ascending=False).index]

# Crear carpeta si no existe
os.makedirs("figures", exist_ok=True)

# Graficar
plt.figure(figsize=(18, 14))
ax = sns.heatmap(
    df_log,
    cmap="Greys",
    linewidths=0.5,
    linecolor='lightgray',
    cbar_kws={"label": "log10(occurrences + 1)"}
)

# Títulos y ejes grandes
plt.title("Log-scaled Semantic Activity Heatmap (Features × Tags)", fontsize=20)
plt.xlabel("Semantic Tags", fontsize=16)
plt.ylabel("Features", fontsize=16)

# Aumentar tamaño de ticks del eje X
ax.tick_params(axis='x', labelsize=12, rotation=45)

# Forzar tamaño de labels del eje Y
ax.set_yticklabels(ax.get_yticklabels(), fontsize=12)

plt.tight_layout()

# Guardar
plt.savefig("figures/feedback_heatmap_log.png")
plt.savefig("figures/feedback_heatmap_log.svg")
plt.close()

print("✅ Mapa de calor actualizado guardado en figures/feedback_heatmap_log.{png,svg}")
