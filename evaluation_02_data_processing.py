import os
import json
import requests
import logging
from collections import defaultdict
from tqdm import tqdm

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Token de GitHub
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Tags por palabra clave
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

# Auxiliar: extraer tags de texto
def extract_tags(text):
    tags = set()
    text = text.lower()
    for tag, words in KEYWORDS.items():
        if any(word in text for word in words):
            tags.add(tag)
    return tags

# Auxiliar: detectar feature en una ruta
def detect_features_from_path(file_path, valid_features):
    parts = file_path.split('/')
    for part in parts:
        if part in valid_features:
            return part
    return None

# Obtener archivos de un commit
def get_commit_files(owner, repo, sha):
    url = f'https://api.github.com/repos/{owner}/{repo}/commits/{sha}'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return [f['filename'] for f in r.json().get('files', [])]
    return []

# Obtener archivos de un PR
def get_pull_files(owner, repo, number):
    files = []
    page = 1
    while True:
        url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{number}/files?page={page}&per_page=100'
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            break
        data = r.json()
        if not data:
            break
        files += [f['filename'] for f in data]
        page += 1
    return files

# Obtener features desde app/modules
def get_valid_features_from_repo(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/app/modules'
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        logging.warning(f"⚠️ No se pudo acceder a app/modules para {owner}/{repo}")
        return set()
    contents = r.json()
    return {item['name'] for item in contents if item['type'] == 'dir'}

# === PROCESAR TODOS LOS FORKS ===
traceability_map = []

for fork_folder in tqdm(os.listdir('evaluation'), desc="Procesando forks"):
    fork_path = os.path.join('evaluation', fork_folder)
    if not os.path.isdir(fork_path):
        continue

    try:
        owner, repo = fork_folder.split('#')
    except ValueError:
        logging.warning(f"❌ Carpeta mal nombrada: {fork_folder}")
        continue

    # Cargar archivos JSON
    try:
        with open(os.path.join(fork_path, 'commits.json')) as f:
            commits = json.load(f)
        with open(os.path.join(fork_path, 'issues.json')) as f:
            issues = json.load(f)
        with open(os.path.join(fork_path, 'pulls.json')) as f:
            pulls = json.load(f)
    except FileNotFoundError:
        logging.warning(f"⚠️ Archivos JSON faltantes en {fork_folder}")
        continue

    valid_features = get_valid_features_from_repo(owner, repo)

    # --- Commits ---
    for commit in commits:
        sha = commit.get('sha')
        message = commit.get('commit', {}).get('message', '')
        tags = extract_tags(message)
        files = get_commit_files(owner, repo, sha)
        features = {detect_features_from_path(f, valid_features) for f in files}
        for feature in features:
            if not feature: continue
            for tag in tags:
                traceability_map.append([feature, 'commit', tag, fork_folder, commit['commit']['committer']['date']])

    # --- Issues ---
    for issue in issues:
        title = issue.get('title', '')
        tags = extract_tags(title)
        labels = issue.get('labels', [])
        features = {label['name'] for label in labels if label['name'] in valid_features}
        for feature in features:
            for tag in tags:
                traceability_map.append([feature, 'issue', tag, fork_folder, issue['created_at']])

    # --- Pull Requests ---
    for pr in pulls:
        number = pr.get('number')
        title = pr.get('title', '')
        tags = extract_tags(title)
        files = get_pull_files(owner, repo, number)
        features = {detect_features_from_path(f, valid_features) for f in files}
        for feature in features:
            if not feature: continue
            for tag in tags:
                traceability_map.append([feature, 'pull_request', tag, fork_folder, pr['created_at']])

# Guardar resultado global
os.makedirs('evaluation', exist_ok=True)
with open('evaluation/traceability_map.json', 'w') as f:
    json.dump(traceability_map, f, indent=2)

logging.info(f"✅ Mapa de trazabilidad global generado con {len(traceability_map)} entradas.")
