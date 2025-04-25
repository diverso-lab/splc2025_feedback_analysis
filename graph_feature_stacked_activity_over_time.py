import json
import os
import matplotlib.pyplot as plt
import pandas as pd

# Cargar el feedback log
with open("feedback_log.json") as f:
    feedback_log = json.load(f)

# Crear DataFrame
df = pd.DataFrame(feedback_log, columns=["feature", "source", "tag", "fork", "timestamp"])
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["month"] = df["timestamp"].dt.to_period("M").dt.to_timestamp()

# Seleccionar las N features más activas
top_n = 6
top_features = df["feature"].value_counts().nlargest(top_n).index.tolist()

# Filtrar solo esas features
df_top = df[df["feature"].isin(top_features)]

# Agrupar por mes y feature
activity_by_month = df_top.groupby(["month", "feature"]).size().unstack(fill_value=0)

# Asegurar que todos los meses estén representados
activity_by_month = activity_by_month.sort_index()

# Crear carpeta
os.makedirs("figures", exist_ok=True)

# Dibujar gráfico de áreas apiladas
plt.figure(figsize=(12, 6))
activity_by_month.plot.area(ax=plt.gca(), cmap="Greys")

plt.title("Stacked Activity of Top Features Over Time")
plt.xlabel("Month")
plt.ylabel("Number of Feedback Entries")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()

# Guardar
plt.savefig("figures/stacked_feature_activity.png")
plt.savefig("figures/stacked_feature_activity.svg")
plt.close()
