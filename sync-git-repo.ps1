param(
    [Parameter(Mandatory = $true)]
    [string]$Org,
    [string]$OutputDir = "C:\Users\whouse\Desktop\ref\clonerepo"
)

# Check gh CLI
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) not found. Install it: winget install GitHub.cli"
    exit 1
}

# Check auth
gh auth status > $null 2>&1
if (-not $?) {
    Write-Error "Not authenticated. Run: gh auth login"
    exit 1
}

# Create output dir
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

Write-Host "Fetching repos from $Org ..." -ForegroundColor Cyan
$repos = gh api "/orgs/$Org/repos?per_page=100" --paginate --jq '.[].name' 2>&1

if ($repos.Count -eq 0) {
    Write-Host "No repos found for '$Org'." -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($repos.Count) repos. Cloning into '$OutputDir' ...`n" -ForegroundColor Cyan

$ok = 0
$fail = 0
foreach ($repo in $repos) {
    $path = "$OutputDir\$repo"
    Write-Host ""
    if (Test-Path $path) {
        Write-Host "--- $repo (exists, updating)" -ForegroundColor Cyan
        Push-Location $path
        $output = git pull --rebase 2>&1
        $exitCode = $LASTEXITCODE
        Pop-Location
        $output | ForEach-Object { Write-Host "       $_" -ForegroundColor DarkGray }
        if ($exitCode -eq 0) {
            Write-Host "  + $repo updated" -ForegroundColor Green
            $ok++
        } else {
            Write-Host "  X $repo update failed" -ForegroundColor Red
            $fail++
        }
        continue
    }

    Write-Host "--- $repo (cloning)" -ForegroundColor Cyan
    $output = gh repo clone "$Org/$repo" $path 2>&1
    $exitCode = $LASTEXITCODE
    $output | ForEach-Object { Write-Host "       $_" -ForegroundColor DarkGray }
    if ($exitCode -eq 0) {
        Write-Host "  + $repo cloned" -ForegroundColor Green
        $ok++
    } else {
        Write-Host "  X $repo clone failed" -ForegroundColor Red
        $fail++
    }
}

Write-Host "`n------------------------------" -ForegroundColor Cyan
Write-Host "  Total: $($repos.Count)  |  OK: $ok  |  Failed: $fail" -ForegroundColor Cyan
Write-Host "------------------------------" -ForegroundColor Cyan
