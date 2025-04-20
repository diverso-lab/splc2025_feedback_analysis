import json
import requests
import os

# Cargar el archivo forks.json
with open('forks.json', 'r') as f:
    repos = json.load(f)

# Obtener el primer repositorio
first_repo_entry = repos[0]
repo_full = first_repo_entry['repo'].replace('.csv', '')
owner, repo = repo_full.split('/')

# Configurar el token de acceso personal de GitHub
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Asegúrate de establecer esta variable de entorno

# Configurar la cabecera de autenticación
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Función para manejar la paginación de la API de GitHub
def fetch_all_pages(url):
    results = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error al obtener datos: {response.status_code}")
            break
        results.extend(response.json())
        # Manejar la paginación
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

# Obtener commits
commits_url = f'https://api.github.com/repos/{owner}/{repo}/commits?per_page=100'
commits = fetch_all_pages(commits_url)
with open('proof_of_concept/commits.json', 'w') as f:
    json.dump(commits, f, indent=2)

# Obtener issues
issues_url = f'https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=100'
issues = fetch_all_pages(issues_url)
with open('proof_of_concept/issues.json', 'w') as f:
    json.dump(issues, f, indent=2)

# Obtener pull requests
pulls_url = f'https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page=100'
pulls = fetch_all_pages(pulls_url)
with open('proof_of_concept/pulls.json', 'w') as f:
    json.dump(pulls, f, indent=2)

print("Datos recopilados y almacenados en archivos JSON.")
