# 2. Tag Evolution Across All Features
# Muestra cómo varía cada tipo de tag con el tiempo (en total, todas las features combinadas)

import json
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
import os

# Cargar feedback_log.json
with open("feedback_log.json") as f:
    feedback_log = json.load(f)

# Crear DataFrame
df = pd.DataFrame(feedback_log, columns=["feature", "source", "tag", "fork", "timestamp"])
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["month"] = df["timestamp"].dt.to_period("M")

# Agrupar por mes y tag
pivot = df.pivot_table(index="month", columns="tag", aggfunc="size", fill_value=0)

# Crear carpeta de figuras si no existe
os.makedirs("figures", exist_ok=True)

# Graficar
plt.figure(figsize=(12, 6))
pivot.plot(kind="line", colormap="gray", linewidth=2)
plt.title("Tag Evolution Over Time (Global)")
plt.xlabel("Month")
plt.ylabel("Occurrences")
plt.tight_layout()
plt.savefig("figures/tag_evolution_global.png")
plt.savefig("figures/tag_evolution_global.svg")
plt.close()

print("✅ Saved: figures/tag_evolution_global.(png|svg)")
