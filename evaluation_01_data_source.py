import os
import json
import requests
from tqdm import tqdm

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_all_pages(url):
    results = []
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Error {response.status_code} en {url}")
            break
        results.extend(response.json())
        links = response.headers.get("Link", "")
        next_link = None
        for link in links.split(','):
            if 'rel="next"' in link:
                next_link = link[link.find('<')+1:link.find('>')]
                break
        url = next_link
    return results

with open("forks.json") as f:
    forks = json.load(f)

for fork in tqdm(forks, desc="Descargando forks"):
    repo_path = fork["repo"].replace(".csv", "")
    owner, repo = repo_path.split("/")
    folder = f"evaluation/{owner}#{repo}"
    os.makedirs(folder, exist_ok=True)

    # Commits
    commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=100"
    commits = fetch_all_pages(commits_url)
    with open(f"{folder}/commits.json", "w") as f:
        json.dump(commits, f, indent=2)

    # Issues
    issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=100"
    issues = fetch_all_pages(issues_url)
    with open(f"{folder}/issues.json", "w") as f:
        json.dump(issues, f, indent=2)

    # Pull requests
    pulls_url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page=100"
    pulls = fetch_all_pages(pulls_url)
    with open(f"{folder}/pulls.json", "w") as f:
        json.dump(pulls, f, indent=2)

    print(f"✅ Guardado {owner}/{repo}")
