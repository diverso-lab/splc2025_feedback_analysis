import json
import os
import requests
import logging
from collections import defaultdict
from tqdm import tqdm

# Configuración del log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Token de GitHub
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# --- FUNCIONES AUXILIARES ---

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

def get_commit_files(owner, repo, sha):
    url = f'https://api.github.com/repos/{owner}/{repo}/commits/{sha}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [f['filename'] for f in response.json().get('files', [])]
    logging.warning(f"Error al obtener archivos del commit {sha}: {response.status_code}")
    return []

def get_pull_files(owner, repo, number):
    files = []
    page = 1
    while True:
        url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{number}/files?page={page}&per_page=100'
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.warning(f"Error al obtener archivos del PR #{number}: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        files += [f['filename'] for f in data]
        page += 1
    return files

def get_valid_features_from_repo(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/app/modules'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.warning(f"⚠️  No se pudo acceder a app/modules para {owner}/{repo}")
        return set()

    contents = response.json()
    valid_features = {item['name'] for item in contents if item['type'] == 'dir'}
    logging.info("✅ Features detectadas automáticamente:")
    for f in sorted(valid_features):
        print(f"- {f}")
    return valid_features

# --- CARGA Y CONFIGURACIÓN DEL REPO ---

with open('proof_of_concept/commits.json') as f:
    commits = json.load(f)
with open('proof_of_concept/issues.json') as f:
    issues = json.load(f)
with open('proof_of_concept/pulls.json') as f:
    pulls = json.load(f)

with open('forks.json', 'r') as f:
    repos = json.load(f)

first_repo_entry = repos[0]
repo_full = first_repo_entry['repo'].replace('.csv', '')
owner, repo = repo_full.split('/')

# Obtener automáticamente las features válidas
VALID_FEATURES = get_valid_features_from_repo(owner, repo)

# --- PROCESAMIENTO ---

traceability_map = []

logging.info("Procesando commits...")
for commit in tqdm(commits, desc="Commits"):
    sha = commit.get('sha')
    message = commit.get('commit', {}).get('message', '')
    tags = extract_tags(message)
    files = get_commit_files(owner, repo, sha)
    features = set()
    for file_path in files:
        feature = detect_features_from_path(file_path, VALID_FEATURES)
        if feature:
            features.add(feature)
    for feature in features:
        for tag in tags:
            traceability_map.append((feature, 'commit', tag))

logging.info("Procesando issues...")
for issue in tqdm(issues, desc="Issues"):
    title = issue.get('title', '')
    tags = extract_tags(title)
    labels = issue.get('labels', [])
    features = set()
    for label in labels:
        label_name = label.get('name', '')
        if label_name in VALID_FEATURES:
            features.add(label_name)
    for feature in features:
        for tag in tags:
            traceability_map.append((feature, 'issue', tag))

logging.info("Procesando pull requests...")
for pr in tqdm(pulls, desc="Pull Requests"):
    number = pr.get('number')
    title = pr.get('title', '')
    tags = extract_tags(title)
    files = get_pull_files(owner, repo, number)
    features = set()
    for file_path in files:
        feature = detect_features_from_path(file_path, VALID_FEATURES)
        if feature:
            features.add(feature)
    for feature in features:
        for tag in tags:
            traceability_map.append((feature, 'pull_request', tag))

# Eliminar duplicados
traceability_map = list(set(traceability_map))

with open('proof_of_concept/traceability_map.json', 'w') as f:
    json.dump(traceability_map, f, indent=2)

logging.info(f"Se han generado {len(traceability_map)} tuplas de trazabilidad.")
