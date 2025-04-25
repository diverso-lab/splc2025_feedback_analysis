# 1. Feature × Tag Evolution Over Time
# Muestra cómo cambian los tags dentro de una misma feature a lo largo del tiempo

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

# Seleccionar top-N features más activas
top_features = df["feature"].value_counts().head(3).index.tolist()
df = df[df["feature"].isin(top_features)]

# Crear carpeta para guardar las figuras
os.makedirs("figures", exist_ok=True)

# Generar gráfico por feature
for feature in top_features:
    subset = df[df["feature"] == feature]
    pivot = subset.pivot_table(index="month", columns="tag", aggfunc="size", fill_value=0)
    pivot.plot(
        figsize=(10, 5),
        colormap="gray",
        title=f"Tag Evolution for Feature: {feature}"
    )
    plt.xlabel("Month")
    plt.ylabel("Occurrences")
    plt.tight_layout()
    plt.savefig(f"figures/tag_evolution_{feature}.png")
    plt.savefig(f"figures/tag_evolution_{feature}.svg")
    plt.close()
    print(f"✅ Saved tag_evolution_{feature}.png and .svg")
