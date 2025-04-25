import json
import pandas as pd
import matplotlib.pyplot as plt
import os

# Cargar feedback_log.json
with open("feedback_log.json") as f:
    feedback_log = json.load(f)

# Convertir a DataFrame
df = pd.DataFrame(feedback_log, columns=["feature", "source", "tag", "fork", "timestamp"])
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Calcular fechas mínima y máxima del log para usar como rango del eje X
min_date = df["timestamp"].min()
max_date = df["timestamp"].max()

# Obtener la primera aparición de cada feature
first_appearance = df.groupby("feature")["timestamp"].min().sort_values()

# Calcular los días desde el primer timestamp
days_since_start = first_appearance.apply(lambda ts: (ts - min_date).days)

# Crear carpeta de salida
os.makedirs("figures", exist_ok=True)

# Plot
plt.figure(figsize=(12, max(6, 0.3 * len(first_appearance))))
plt.barh(first_appearance.index, days_since_start, color="gray")
plt.xlabel("Days since first activity in the log")
plt.title("Feature Introduction Timeline")
plt.xlim(0, (max_date - min_date).days)
plt.tight_layout()
plt.savefig("figures/feature_introduction_timeline.png")
plt.savefig("figures/feature_introduction_timeline.svg")
plt.close()

print("✅ Saved as figures/feature_introduction_timeline.(png|svg)")
