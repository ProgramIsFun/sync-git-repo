"""
Sync all repos from GitHub org (ProgramIsFun) to Jihulab group (ProgramIsFun).
- If repo doesn't exist on Jihulab: create it and push
- If repo exists on Jihulab: fetch latest from GitHub and force-push to Jihulab
"""

import os
import subprocess
import requests
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

GITHUB_ORG = "ProgramIsFun"
JIHU_GROUP = "ProgramIsFun"
JIHU_BASE = "https://www.jihulab.com/api/v4"
JIHU_TOKEN = os.environ["JIHU_TOKEN"]
GH_TOKEN = os.environ["GH_TOKEN"]


def github_get(path):
    r = requests.get(
        f"https://api.github.com{path}",
        headers={"Authorization": f"Bearer {GH_TOKEN}", "Accept": "application/vnd.github+json"},
    )
    r.raise_for_status()
    return r.json()


def jihu_get(path, params=None):
    r = requests.get(
        f"{JIHU_BASE}{path}",
        headers={"PRIVATE-TOKEN": JIHU_TOKEN},
        params=params,
    )
    r.raise_for_status()
    return r.json()


def jihu_post(path, data):
    r = requests.post(
        f"{JIHU_BASE}{path}",
        headers={"PRIVATE-TOKEN": JIHU_TOKEN},
        json=data,
    )
    r.raise_for_status()
    return r.json()


def get_github_repos():
    repos = []
    page = 1
    while True:
        data = github_get(f"/orgs/{GITHUB_ORG}/repos?per_page=100&page={page}")
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos


def get_jihu_repos():
    repos = []
    page = 1
    while True:
        data = jihu_get(f"/groups/{JIHU_GROUP}/projects", {"per_page": 100, "page": page})
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos


def create_jihu_repo(name, description=""):
    print(f"  Creating repo {JIHU_GROUP}/{name} on Jihulab...")
    return jihu_post("/projects", {
        "name": name,
        "namespace_id": jihu_get("/groups", {"search": JIHU_GROUP})[0]["id"],
        "description": description,
        "visibility": "public",
    })


def sync_repo(repo_name, tmpdir):
    print(f"  Cloning https://github.com/{GITHUB_ORG}/{repo_name}.git ...")
    clone_url = f"https://{GH_TOKEN}@github.com/{GITHUB_ORG}/{repo_name}.git"
    repo_path = os.path.join(tmpdir, repo_name)

    result = subprocess.run(
        ["git", "clone", "--mirror", clone_url, repo_path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  ERROR cloning: {result.stderr.strip()}")
        return False

    jihu_push_url = f"https://oauth2:{JIHU_TOKEN}@www.jihulab.com/{JIHU_GROUP}/{repo_name}.git"
    result = subprocess.run(
        ["git", "push", "--mirror", jihu_push_url],
        cwd=repo_path,
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  ERROR pushing: {result.stderr.strip()}")
        return False

    return True


def main():
    print("Fetching GitHub repos...")
    gh_repos = get_github_repos()
    print(f"  Found {len(gh_repos)} repos on GitHub\n")

    print("Fetching Jihulab repos...")
    jh_repos = get_jihu_repos()
    jh_names = {r["path"] for r in jh_repos}
    print(f"  Found {len(jh_repos)} repos on Jihulab\n")

    tmpdir = tempfile.mkdtemp(prefix="repo-sync-")
    print(f"Working directory: {tmpdir}\n")

    created = 0
    updated = 0
    failed = 0

    for repo in gh_repos:
        name = repo["name"]
        print(f"[{name}]")

        if name not in jh_names:
            print(f"  Not found on Jihulab, creating...")
            try:
                create_jihu_repo(name, repo.get("description", ""))
                created += 1
            except Exception as e:
                print(f"  ERROR creating repo: {e}")
                failed += 1
                continue

        if sync_repo(name, tmpdir):
            updated += 1
            print(f"  Synced")
        else:
            failed += 1

        print()

    shutil.rmtree(tmpdir, ignore_errors=True)
    print(f"\nDone: {created} created, {updated} updated, {failed} failed")


if __name__ == "__main__":
    main()
