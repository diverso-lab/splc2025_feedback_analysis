import json
import os
from collections import defaultdict, Counter
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# Cargar el feedback log
with open("feedback_log.json") as f:
    feedback_log = json.load(f)

# Definir grupos de tags semánticos
TAG_GROUPS = {
    "Testing/Fix": {"testing", "fix"},
    "Refactor/Mock": {"refactor", "mock"},
    "Configuration": {"config"},
    "Modeling": {"model"},
    "Extension": {"extension"},
    "Obsolete": {"obsolete"},
}

# Contador por mes y grupo
group_time_series = defaultdict(Counter)

# Procesar el feedback log
for feature, source, tag, fork, timestamp in feedback_log:
    dt = datetime.fromisoformat(timestamp)
    month_str = dt.strftime("%Y-%m")
    for group, tag_set in TAG_GROUPS.items():
        if tag in tag_set:
            group_time_series[group][month_str] += 1

# Crear DataFrame y ordenarlo
df = pd.DataFrame(group_time_series).fillna(0).sort_index()
df.index = pd.to_datetime(df.index)

# Graficar área
plt.figure(figsize=(14, 7))
df.plot.area(colormap='Greys', linewidth=0, alpha=0.9)
plt.title("Semantic Activity Evolution Over Time")
plt.xlabel("Time")
plt.ylabel("Occurrences")
plt.xticks(rotation=45)
plt.tight_layout()

# Guardar en PNG y SVG
os.makedirs("figures", exist_ok=True)
plt.savefig("figures/semantic_activity_evolution.svg", format='svg')
plt.savefig("figures/semantic_activity_evolution.png", format='png')
plt.close()
