import json
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import os

# Load the feedback log
with open("feedback_log.json") as f:
    feedback_log = json.load(f)

# Group by tag
tag_feature_count = defaultdict(Counter)
feature_tags = defaultdict(list)

for feature, source_type, tag, fork, timestamp in feedback_log:
    tag_feature_count[tag][feature] += 1
    feature_tags[feature].append(tag)

# Define analysis groups
GROUPS = {
    "testing_needs": ['testing', 'fix', 'error'],
    "heavy_mock_usage": ['mock'],
    "refactor_needed": ['mock', 'refactor'],
    "ci_cd_activity": ['config', 'model'],
    "active_features": ['testing', 'model', 'config'],
    "extension": ['extension'],
    "obsolete": ['obsolete'],
    "failures": ['fix']
}

TITLES = {
    "testing_needs": "Features that need more testing",
    "heavy_mock_usage": "Features with heavy use of mocks",
    "refactor_needed": "Features likely in need of refactoring",
    "ci_cd_activity": "Features with CI/CD activity",
    "active_features": "Highly active features (testing + model + config)",
    "extension": "Features being extended",
    "obsolete": "Potentially obsolete features",
    "failures": "Frequently failing features"
}

# Create output directory
os.makedirs("figures", exist_ok=True)

# Function to generate plots in PNG and SVG
def plot_tag_group(tag_list, title, filename):
    score = Counter()
    for tag in tag_list:
        for feature, count in tag_feature_count[tag].items():
            score[feature] += count

    if not score:
        print(f"[Warning] No data for '{title}'")
        return

    top_features = score.most_common(10)
    features, counts = zip(*top_features)

    plt.figure(figsize=(10, 6))
    bars = plt.barh(features, counts, color='gray')
    plt.xlabel("Occurrences")
    plt.title(title)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join("figures", f"{filename}.png"))
    plt.savefig(os.path.join("figures", f"{filename}.svg"))
    plt.close()
    print(f"✅ Graphs saved: figures/{filename}.png and .svg")

# Generate all charts
for key, tags in GROUPS.items():
    plot_tag_group(tags, TITLES[key], key)
