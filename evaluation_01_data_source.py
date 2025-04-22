import os
import json
import requests
from tqdm import tqdm
import logging

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

# Función para obtener todos los resultados paginados
def fetch_all_pages(url):
    results = []
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            logging.warning(f"❌ Error al obtener datos: {response.status_code} - {url}")
            break
        results.extend(response.json())
        # Verificar si hay siguiente página
        if 'Link' in response.headers:
            links = response.headers['Link']
            next_link = None
            for link in links.split(','):
                if 'rel="next"' in link:
                    next_link = link[link.find('<') + 1:link.find('>')]
                    break
            url = next_link
        else:
            url = None
    return results

# Función para obtener archivos de un commit
def enrich_commits_with_files(owner, repo, commits):
    for commit in tqdm(commits, desc="Añadiendo archivos a commits"):
        sha = commit.get('sha')
        url = f'https://api.github.com/repos/{owner}/{repo}/commits/{sha}'
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            commit['files'] = response.json().get('files', [])
        else:
            logging.warning(f"⚠️  Error al obtener archivos del commit {sha}")
    return commits

# Función para obtener archivos de cada PR
def enrich_pulls_with_files(owner, repo, pulls):
    for pr in tqdm(pulls, desc="Añadiendo archivos a PRs"):
        number = pr.get('number')
        url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{number}/files'
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            pr['files'] = response.json()
        else:
            logging.warning(f"⚠️  Error al obtener archivos del PR #{number}")
    return pulls

# Leer forks.json
with open('forks2.json', 'r') as f:
    forks = json.load(f)

for entry in tqdm(forks, desc="Procesando forks"):
    repo_csv = entry['repo']
    repo_full = repo_csv.replace('.csv', '')
    owner, repo = repo_full.split('/')
    folder_name = f"{owner}#{repo}"
    folder = os.path.join('evaluation', folder_name)

    os.makedirs(folder, exist_ok=True)

    # Commits
    commits_url = f'https://api.github.com/repos/{owner}/{repo}/commits?per_page=100'
    commits = fetch_all_pages(commits_url)
    commits = enrich_commits_with_files(owner, repo, commits)
    with open(os.path.join(folder, 'commits.json'), 'w') as f:
        json.dump(commits, f, indent=2)

    # Issues
    issues_url = f'https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=100'
    issues = fetch_all_pages(issues_url)
    with open(os.path.join(folder, 'issues.json'), 'w') as f:
        json.dump(issues, f, indent=2)

    # Pull Requests
    pulls_url = f'https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page=100'
    pulls = fetch_all_pages(pulls_url)
    pulls = enrich_pulls_with_files(owner, repo, pulls)
    with open(os.path.join(folder, 'pulls.json'), 'w') as f:
        json.dump(pulls, f, indent=2)

    logging.info(f"✅ Datos guardados en {folder}")
