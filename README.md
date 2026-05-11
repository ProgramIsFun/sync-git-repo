# sync-git-repo

Clone or update all repositories from a GitHub organization into a local directory.

## Prerequisites

- [GitHub CLI](https://cli.github.com/) (`winget install GitHub.cli`)
- Authenticated with `gh auth login`

## Usage

```powershell
.\sync-git-repo.ps1 -Org <organization>
```

Clones all repos into `C:\Users\whouse\Desktop\ref\clonerepo`. Existing repos are updated with `git pull --rebase`.

### Options

| Param       | Description                                      |
|-------------|--------------------------------------------------|
| `-Org`      | GitHub organization name (required)              |
| `-OutputDir`| Target directory (default: see script source)    |

## Example

```powershell
.\sync-git-repo.ps1 -Org Microsoft
```
