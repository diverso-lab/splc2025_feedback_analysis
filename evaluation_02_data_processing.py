import json
import os
import logging
from collections import defaultdict
from tqdm import tqdm
import requests

# Configuración del log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Token de GitHub
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Palabras clave por tipo de tag
KEYWORDS = {
    'testing': ['test', 'testing', 'ci', 'unit', 'integration'],
    'fix': ['fix', 'bug', 'error', 'fail'],
    'mock': ['mock', 'stub'],
    'config': ['config', 'configuration', 'setup'],
    'model': ['model', 'schema'],
    'extension': ['extend', 'extension', 'feature'],
    'refactor': ['refactor', 'restructure'],
    'obsolete': ['obsolete', 'deprecated', 'remove']
}

def extract_tags(text):
    tags = set()
    text = text.lower()
    for tag, words in KEYWORDS.items():
        if any(word in text for word in words):
            tags.add(tag)
    return tags

def detect_features_from_path(file_path, valid_features):
    parts = file_path.split('/')
    for part in parts:
        if part in valid_features:
            return part
    return None

def get_valid_features_from_repo(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/app/modules'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        logging.warning(f"⚠️  No se pudo acceder a app/modules para {owner}/{repo}")
        return set()
    contents = response.json()
    return {item['name'] for item in contents if item['type'] == 'dir'}

# Procesamiento de todos los forks
with open('forks.json') as f:
    forks = json.load(f)

for entry in tqdm(forks, desc="Procesando forks"):
    repo_csv = entry['repo']
    repo_full = repo_csv.replace('.csv', '')
    owner, repo = repo_full.split('/')
    folder_name = f"{owner}#{repo}"
    folder = os.path.join('evaluation', folder_name)

    commits_file = os.path.join(folder, 'commits.json')
    issues_file = os.path.join(folder, 'issues.json')
    pulls_file = os.path.join(folder, 'pulls.json')

    if not all(os.path.exists(f) for f in [commits_file, issues_file, pulls_file]):
        logging.warning(f"⚠️  Archivos no encontrados para {repo_full}")
        continue

    with open(commits_file) as f:
        commits = json.load(f)
    with open(issues_file) as f:
        issues = json.load(f)
    with open(pulls_file) as f:
        pulls = json.load(f)

    valid_features = get_valid_features_from_repo(owner, repo)
    logging.info(f"✅ Features detectadas en {repo}: {sorted(valid_features)}")

    traceability_map = []

    for commit in commits:
        sha = commit.get('sha')
        message = commit.get('commit', {}).get('message', '')
        tags = extract_tags(message)
        files = [f['filename'] for f in commit.get('files', [])] if 'files' in commit else []
        timestamp = commit.get('commit', {}).get('author', {}).get('date')
        features = {detect_features_from_path(f, valid_features) for f in files}
        for feature in features:
            if feature:
                for tag in tags:
                    traceability_map.append([feature, 'commit', tag, timestamp])

    for issue in issues:
        title = issue.get('title', '')
        tags = extract_tags(title)
        labels = issue.get('labels', [])
        features = {label['name'] for label in labels if label['name'] in valid_features}
        timestamp = issue.get('created_at')
        for feature in features:
            for tag in tags:
                traceability_map.append([feature, 'issue', tag, timestamp])

    for pr in pulls:
        number = pr.get('number')
        title = pr.get('title', '')
        tags = extract_tags(title)
        files = [f['filename'] for f in pr.get('files', [])] if 'files' in pr else []
        timestamp = pr.get('created_at')
        features = {detect_features_from_path(f, valid_features) for f in files}
        for feature in features:
            if feature:
                for tag in tags:
                    traceability_map.append([feature, 'pull_request', tag, timestamp])

    traceability_map = list(set(tuple(t) for t in traceability_map))

    output_path = os.path.join(folder, 'traceability_map.json')
    with open(output_path, 'w') as f:
        json.dump(traceability_map, f, indent=2)

    logging.info(f"✅ {len(traceability_map)} tuplas escritas en {output_path}")
