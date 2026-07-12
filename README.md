# sync-git-repo

Backup tools for GitHub organizations. Two scripts, two purposes:

| Script | Purpose |
|--------|---------|
| `sync-git-repo.ps1` | Clone/update all repos **locally** |
| `sync.py` | Mirror all repos to **Jihulab** |

---

## 1. Local Clone — `sync-git-repo.ps1`

Clone or update all repositories from a GitHub organization into a local directory.

### Prerequisites

- [GitHub CLI](https://cli.github.com/) (`winget install GitHub.cli`)
- Authenticated with `gh auth login`

### Usage

```powershell
.\sync-git-repo.ps1 -Org <organization>
```

Clones all repos into `C:\Users\whouse\Desktop\ref\clonerepo`. Existing repos are updated with `git pull --rebase`.

### Options

| Param       | Description                                      |
|-------------|--------------------------------------------------|
| `-Org`      | GitHub organization name (required)              |
| `-OutputDir`| Target directory (default: see script source)    |

### Example

```powershell
.\sync-git-repo.ps1 -Org Microsoft
```

---

## 2. Jihulab Mirror — `sync.py`

Mirror all repositories from a GitHub organization to a Jihulab group.

- If repo doesn't exist on Jihulab → creates it and pushes
- If repo exists → fetches latest from GitHub and force-pushes to Jihulab

### Prerequisites

- Python 3.10+
- `pip install python-dotenv requests`
- A `.env` file with tokens (see below)

### Setup

Create a `.env` file in this directory:

```
GH_TOKEN=your_github_token
JIHU_TOKEN=your_jihulab_token
```

### Usage

```bash
python sync.py
```
