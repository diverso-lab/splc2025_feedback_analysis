import json
from collections import defaultdict, Counter

# Load the feedback log
with open("feedback_log.json") as f:
    feedback_log = json.load(f)

# Structures for analysis
feature_tags = defaultdict(list)
tag_feature_count = defaultdict(Counter)

# Grouping
for feature, source_type, tag, fork, timestamp in feedback_log:
    feature_tags[feature].append(tag)
    tag_feature_count[tag][feature] += 1

# Printing functions
def print_section(title):
    print("\n" + "=" * len(title))
    print(title)
    print("=" * len(title))

def print_feature_list(title, tag):
    print_section(title)
    for feature, count in tag_feature_count[tag].most_common():
        print(f"- {feature}: {count} occurrences")

def print_composite_section(title, tags):
    print_section(title)
    score = Counter()
    for tag in tags:
        for feature, count in tag_feature_count[tag].items():
            score[feature] += count
    for feature, count in score.most_common():
        active_tags = ', '.join(set(feature_tags[feature]) & set(tags))
        print(f"- {feature}: {count} occurrences ({active_tags})")

# ===============================
# FEEDBACK QUESTIONS
# ===============================

# 🧪 Testing questions
print_section("🧪 TESTING QUESTIONS")

print_composite_section("Which features need more testing?", ['testing', 'fix', 'error'])
print_composite_section("Which features rely heavily on mocks?", ['mock'])
print_composite_section("Which features are poorly designed for testing (refactor)?", ['mock', 'refactor'])

# ✨ Feature evolution
print_section("✨ FEATURE QUESTIONS")

print_feature_list("Which features are being extended?", 'extension')
print_feature_list("Which features are being refactored?", 'refactor')
print_feature_list("Which features could be removed (obsolete)?", 'obsolete')
print_composite_section("Which features are highly active (testing + model + config)?", ['testing', 'model', 'config'])

# ⚙️ CI/CD questions
print_section("⚙️ CI/CD QUESTIONS")

print_feature_list("Which features cause configuration issues?", 'config')
print_feature_list("Which features introduce new models?", 'model')
print_feature_list("Which features fail often (fix)?", 'fix')

# ✅ Totals
print_section("✅ TOTAL")
print(f"Total number of features analyzed: {len(feature_tags)}")
print(f"Total number of feedback log entries: {len(feedback_log)}")
