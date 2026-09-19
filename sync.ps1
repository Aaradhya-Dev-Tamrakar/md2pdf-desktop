<#
.SYNOPSIS
    Automated Git synchronization, secret scanner, and environment health engine for md2pdf-desktop.

.DESCRIPTION
    sync.ps1 — The central synchronization hub for the md2pdf-desktop repository:
    https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop

    Capabilities:
    1. Remote Verification: Ensures 'origin' remote is correctly configured.
    2. Safe Remote Pull: Pulls latest updates with --rebase --autostash.
    3. Pre-Commit Secret Scanner Guard: Prevents accidental credential/API key commits.
    4. Intelligent Conventional Commits: Analyzes staged changes and generates scoped
       conventional commit messages (e.g. feat(core), fix(latex), feat(mcp), feat(ui), etc.).
    5. Toolchain Telemetry & Health (-CheckTools): Verifies pandoc, wkhtmltopdf, pdflatex,
       and validates the LaTeX template compiler.
    6. Clean Push & Conflict Recovery: Automatically retries rejected pushes via rebase.
    7. Repository Telemetry (-Status): Displays branch health, commits ahead/behind, and status.
    8. Dry Run Mode (-WhatIf): Previews staging, secret scan, and commit message safely.

.PARAMETER Message
    Custom commit message (e.g. -m "feat(core): add unicode logic symbol mapping").
    Alias: -m. If omitted, an intelligent conventional commit message is generated.

.PARAMETER Branch
    Target or switch to a specific branch to synchronize (e.g. -Branch main).
    Alias: -b.

.PARAMETER PullOnly
    Safely pull remote updates with --rebase --autostash without committing or pushing.

.PARAMETER PushOnly
    Pushes existing local commits without creating new commits.

.PARAMETER NoPush
    Stages and commits changes locally without pushing to remote origin.

.PARAMETER WhatIf
    Dry-run mode: previews changes, secret scan, and auto-generated commit message
    without modifying git repository state.

.PARAMETER Status
    Displays repository telemetry: branch status, remote configuration, ahead/behind
    commits, and working tree health.

.PARAMETER CheckTools
    Verifies PDF conversion toolchains (pandoc, wkhtmltopdf, pdflatex) and tests the LaTeX template.

.PARAMETER Test
    Runs automated probe and test verification before staging and committing.

.EXAMPLE
    .\sync.ps1                               # Routine sync: commit & push active branch
    .\sync.ps1 -m "fix(latex): fix margins"  # Sync with custom commit message
    .\sync.ps1 -PullOnly                     # Safely pull updates only
    .\sync.ps1 -PushOnly                     # Push existing local commits
    .\sync.ps1 -Status                       # Show repository telemetry
    .\sync.ps1 -CheckTools                   # Verify pandoc, pdflatex, wkhtmltopdf toolchain
    .\sync.ps1 -WhatIf                       # Dry-run preview
#>

[CmdletBinding()]
param (
    [Alias("m")]
    [string]$Message,

    [Alias("b")]
    [string]$Branch,

    [switch]$PullOnly,

    [switch]$PushOnly,

    [switch]$NoPush,

    [switch]$WhatIf,

    [switch]$Status,

    [switch]$CheckTools,

    [switch]$Test
)

$ErrorActionPreference = "Stop"

# Terminal & Encoding Configuration
$Host.UI.RawUI.WindowTitle = "md2pdf-desktop Sync"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$TargetRemoteName = "origin"
$TargetRemoteUrl  = "https://github.com/Aaradhya-Dev-Tamrakar/md2pdf-desktop.git"

function Write-Status {
    param(
        [string]$Message,
        [System.ConsoleColor]$Color = [System.ConsoleColor]::Cyan
    )
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] $Message" -ForegroundColor $Color
}

function Write-Notice {
    param([string]$Message)
    Write-Status -Message $Message -Color ([System.ConsoleColor]::Yellow)
}

function Write-Success {
    param([string]$Message)
    Write-Status -Message $Message -Color ([System.ConsoleColor]::Green)
}

function Write-Fail {
    param([string]$Message)
    Write-Status -Message $Message -Color ([System.ConsoleColor]::Red)
}

function Ensure-RemoteConfigured {
    $existingRemotes = @(git remote)
    if ($existingRemotes -notcontains $TargetRemoteName) {
        Write-Status "Adding remote '$TargetRemoteName' ($TargetRemoteUrl)..."
        git remote add $TargetRemoteName $TargetRemoteUrl
    }
    else {
        $currentUrl = (git remote get-url $TargetRemoteName 2>$null)
        if ($currentUrl) { $currentUrl = $currentUrl.Trim() }
        $cleanCurrent = $currentUrl -replace '\.git$', ''
        $cleanTarget  = $TargetRemoteUrl -replace '\.git$', ''
        if ($cleanCurrent -ne $cleanTarget) {
            Write-Notice "Updating remote '$TargetRemoteName' URL to $TargetRemoteUrl..."
            git remote set-url $TargetRemoteName $TargetRemoteUrl
        }
    }
}

function Test-PDFTools {
    Write-Host "`n========================================================" -ForegroundColor DarkCyan
    Write-Host " 🛠️  MD2PDF ENGINE & TOOLCHAIN HEALTH" -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor DarkCyan

    $tools = @{
        "pandoc"      = (Get-Command pandoc -ErrorAction SilentlyContinue)
        "wkhtmltopdf" = (Get-Command wkhtmltopdf -ErrorAction SilentlyContinue)
        "pdflatex"    = (Get-Command pdflatex -ErrorAction SilentlyContinue)
    }

    foreach ($t in $tools.Keys) {
        if ($tools[$t]) {
            Write-Host "  ✅ $t : $($tools[$t].Source)" -ForegroundColor Green
        }
        else {
            Write-Host "  ❌ $t : NOT FOUND on PATH" -ForegroundColor Red
        }
    }

    # Probe LaTeX template compilation
    $pythonCmd = (Get-Command python -ErrorAction SilentlyContinue)
    if ($pythonCmd) {
        try {
            $probeOut = python -c "from md2pdf.core import probe_latex_template; ok, err = probe_latex_template(); print('OK' if ok else f'FAIL: {err}')" 2>$null
            if ($probeOut -match "^OK") {
                Write-Host "  ✅ styled.latex template : Compilation Verified (LaTeX engine operational)" -ForegroundColor Green
            }
            else {
                Write-Host "  ⚠️  styled.latex template : Probe warning: $probeOut" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "  ⚠️  Could not run template probe." -ForegroundColor Yellow
        }
    }
    Write-Host "========================================================`n" -ForegroundColor DarkCyan
}

function Find-StagedSecrets {
    $stagedDiff = git diff --cached -U0 2>$null
    if (-not $stagedDiff) { return @() }

    $addedLines = @($stagedDiff | Where-Object { $_ -match '^\+[^+]' } | ForEach-Object { $_.Substring(1) })
    if ($addedLines.Count -eq 0) { return @() }

    $secretPatterns = @(
        'AKIA[0-9A-Z]{16}',                                              # AWS Access Key
        'sk-[a-zA-Z0-9]{20,}',                                           # OpenAI API Key
        'sk-ant-[a-zA-Z0-9\-]{20,}',                                     # Anthropic API Key
        'ghp_[a-zA-Z0-9]{36}',                                           # GitHub Personal Token
        'github_pat_[a-zA-Z0-9_]{20,}',                                  # GitHub Fine-grained PAT
        'AIza[0-9A-Za-z\-_]{35}',                                        # Google / Gemini API Key
        'xox[baprs]-[0-9a-zA-Z\-]{10,}',                                 # Slack Token
        '-----BEGIN (RSA|EC|OPENSSH|PGP|DSA)? ?PRIVATE KEY-----',        # Private Keys
        '(?i)(api[_-]?key|secret|password|token|passwd)\s*[:=]\s*[''"][^''"\s]{8,}[''"]' # Generic Secrets
    )

    $hits = @()
    foreach ($line in $addedLines) {
        foreach ($pattern in $secretPatterns) {
            if ($line -match $pattern) {
                $snippet = $line.Trim()
                $redacted = if ($snippet.Length -gt 45) { $snippet.Substring(0, 45) + "..." } else { $snippet }
                $hits += [PSCustomObject]@{
                    Pattern = $pattern
                    Snippet = $redacted
                }
                break
            }
        }
    }

    return @($hits)
}

function Get-AutoCommitMessage {
    param([string]$ActiveBranch = "main")

    $statusLines = @(git status --porcelain 2>$null)
    if (-not $statusLines -or $statusLines.Count -eq 0) { return $null }

    $modifiedFiles = @()
    $addedFiles = @()
    $deletedFiles = @()
    $allChanged = @()

    foreach ($line in $statusLines) {
        if ([string]::IsNullOrWhiteSpace($line) -or $line.Length -lt 3) { continue }
        $statusCode = $line.Substring(0, 2)
        $rawPath = $line.Substring(3).Trim()

        if ($rawPath -match '->') {
            $rawPath = ($rawPath -split '->')[-1].Trim()
        }

        $cleanPath = $rawPath.Trim('"')
        $fileName = Split-Path $cleanPath -Leaf
        if ([string]::IsNullOrWhiteSpace($fileName)) { continue }

        $allChanged += $cleanPath

        if ($statusCode -match 'A|\?\?') {
            $addedFiles += $cleanPath
        }
        elseif ($statusCode -match 'D') {
            $deletedFiles += $cleanPath
        }
        else {
            $modifiedFiles += $cleanPath
        }
    }

    if ($allChanged.Count -eq 0) { return $null }

    # Component-aware classification for md2pdf-desktop
    $scope = "app"
    $type = "chore"

    $hasCore     = $allChanged | Where-Object { $_ -match 'md2pdf/core\.py' }
    $hasLatex    = $allChanged | Where-Object { $_ -match 'styled\.latex|\.latex$|\.lua$' }
    $hasApp      = $allChanged | Where-Object { $_ -match 'md2pdf_app\.py' }
    $hasMcp      = $allChanged | Where-Object { $_ -match '^mcp_server/' -or $_ -match 'mcp' }
    $hasDocs     = $allChanged | Where-Object { $_ -match '\.md$' }
    $hasScripts  = $allChanged | Where-Object { $_ -match '\.(ps1|bat|sh)$' }
    $hasConfig   = $allChanged | Where-Object { $_ -match 'pyproject\.toml|requirements\.txt|uv\.lock|\.gitignore' }

    if ($hasCore) {
        $type = if ($addedFiles.Count -gt 0) { "feat" } else { "fix" }
        $scope = "core"
    }
    elseif ($hasLatex) {
        $type = "fix"
        $scope = "latex"
    }
    elseif ($hasMcp) {
        $type = if ($addedFiles.Count -gt 0) { "feat" } else { "fix" }
        $scope = "mcp"
    }
    elseif ($hasApp) {
        $type = if ($addedFiles.Count -gt 0) { "feat" } else { "fix" }
        $scope = "ui"
    }
    elseif ($hasDocs) {
        $type = "docs"
        $scope = "docs"
    }
    elseif ($hasConfig) {
        $type = "build"
        $scope = "deps"
    }
    elseif ($hasScripts) {
        $type = "chore"
        $scope = "scripts"
    }

    $fileNames = @($allChanged | ForEach-Object { Split-Path $_ -Leaf })
    $summary = ""
    if ($fileNames.Count -le 2) {
        $summary = $fileNames -join ", "
    }
    else {
        $firstTwo = ($fileNames[0..1]) -join ", "
        $extraCount = $fileNames.Count - 2
        $summary = "$firstTwo +$extraCount more"
    }

    $diffStat = git diff --cached --shortstat 2>$null
    $churn = ""
    if ($diffStat -match '(\d+)\s+insertion') { $ins = $Matches[1] } else { $ins = 0 }
    if ($diffStat -match '(\d+)\s+deletion') { $del = $Matches[1] } else { $del = 0 }
    if (($ins -as [int]) -gt 0 -or ($del -as [int]) -gt 0) {
        $churn = " (+$ins/-$del)"
    }

    # Action verb
    $action = "update"
    if ($addedFiles.Count -gt 0 -and $modifiedFiles.Count -eq 0 -and $deletedFiles.Count -eq 0) {
        $action = "add"
    }
    elseif ($deletedFiles.Count -gt 0 -and $modifiedFiles.Count -eq 0 -and $addedFiles.Count -eq 0) {
        $action = "remove"
    }

    return "${type}(${scope}): ${action} ${summary}${churn}"
}

function Switch-ToBranch {
    param([string]$TargetBranch)

    $current = (git branch --show-current 2>$null)
    if ($current) { $current = $current.Trim() }
    if ($current -eq $TargetBranch) { return $TargetBranch }

    Write-Status "Switching from [$current] to target branch: [$TargetBranch]..."
    $localBranches = @(git branch --format="%(refname:short)")

    if ($localBranches -contains $TargetBranch) {
        git switch $TargetBranch
        if ($LASTEXITCODE -ne 0) {
            Write-Notice "Stashing local changes to switch branch safely..."
            git stash push -u -m "sync-branch-switch" | Out-Null
            git switch $TargetBranch
            git stash pop | Out-Null
        }
    }
    else {
        git fetch origin --prune
        $remoteBranches = @(git branch -r --format="%(refname:short)")
        if ($remoteBranches -contains "origin/$TargetBranch") {
            git switch --track "origin/$TargetBranch"
        }
        else {
            Write-Status "Creating new local branch [$TargetBranch] from current HEAD..."
            git checkout -b $TargetBranch
        }
    }

    return $TargetBranch
}

function Show-RepoStatus {
    param([string]$RepoPath, [string]$Branch)

    Write-Host "`n========================================================" -ForegroundColor DarkCyan
    Write-Host " 🚀 MD2PDF-DESKTOP REPOSITORY STATUS" -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor DarkCyan
    Write-Host "Path          : $RepoPath"
    Write-Host "Active Branch : $Branch"
    Write-Host "Remote URL    : $(git remote get-url origin 2>$null)"

    $aheadBehind = git rev-list --left-right --count "origin/$Branch...$Branch" 2>$null
    if ($aheadBehind) {
        $parts = $aheadBehind.Trim() -split '\s+'
        $behind = $parts[0]
        $ahead  = $parts[1]
        Write-Host "Commits Ahead : $ahead" -ForegroundColor $(if ($ahead -gt 0) { [System.ConsoleColor]::Yellow } else { [System.ConsoleColor]::Green })
        Write-Host "Commits Behind: $behind" -ForegroundColor $(if ($behind -gt 0) { [System.ConsoleColor]::Red } else { [System.ConsoleColor]::Green })
    }

    Write-Host "`nLocal Working Tree:" -ForegroundColor DarkCyan
    $statusOutput = git status --short
    if ($statusOutput) {
        Write-Host $statusOutput
    }
    else {
        Write-Host "  (clean, no unstaged or untracked changes)" -ForegroundColor Green
    }
    Write-Host "========================================================`n" -ForegroundColor DarkCyan
}

# -------------------------------------------------------------
# Main Execution Routine
# -------------------------------------------------------------

$RepoPath = $PSScriptRoot
if (-not (Test-Path (Join-Path $RepoPath '.git'))) {
    Write-Fail "Not inside a git repository: $RepoPath"
    exit 1
}

Push-Location $RepoPath
try {
    Ensure-RemoteConfigured

    # Branch resolution
    if ($Branch) {
        $currentBranch = Switch-ToBranch -TargetBranch $Branch
    }
    else {
        $currentBranch = (git branch --show-current 2>$null)
        if ($currentBranch) { $currentBranch = $currentBranch.Trim() }
        if (-not $currentBranch) { $currentBranch = "main" }
    }

    if ($CheckTools) {
        Test-PDFTools
        exit 0
    }

    if ($Status) {
        Show-RepoStatus -RepoPath $RepoPath -Branch $currentBranch
        exit 0
    }

    Write-Status "Repository : $RepoPath"
    Write-Status "Branch     : $currentBranch"
    Write-Status "Remote URL : $TargetRemoteUrl"

    if ($Test) {
        Write-Status "Running LaTeX template probe test..."
        python -c "from md2pdf.core import probe_latex_template; ok, err = probe_latex_template(); assert ok, err"
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "Probe test failed. Aborting sync."
            exit 1
        }
        Write-Success "LaTeX engine and template probe passed."
    }

    # 1. Pull latest changes
    Write-Status "Pulling latest updates from origin/$currentBranch..."
    git pull --rebase --autostash origin $currentBranch
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "git pull encountered conflicts or errors."
        exit $LASTEXITCODE
    }

    if ($PullOnly) {
        Write-Success "Pull complete (-PullOnly active)."
        exit 0
    }

    # 2. Check changes
    $statusPorcelain = git status --porcelain 2>$null
    $hasUncommitted = [bool]($statusPorcelain -and $statusPorcelain.Trim().Length -gt 0)

    $unpushed = git rev-list "origin/$currentBranch..$currentBranch" 2>$null
    $hasUnpushed = [bool]($unpushed -and $unpushed.Trim().Length -gt 0)

    if ($PushOnly) {
        if ($hasUnpushed) {
            Write-Status "Pushing existing commits to origin/$currentBranch..."
            git push origin $currentBranch
            Write-Success "Push completed successfully."
        }
        else {
            Write-Success "No unpushed commits found. Remote is up to date."
        }
        exit 0
    }

    if (-not $hasUncommitted) {
        if ($hasUnpushed) {
            Write-Notice "No local changes to commit, but local branch is ahead of remote."
            if (-not $NoPush -and -not $WhatIf) {
                Write-Status "Pushing pending commit(s) to origin/$currentBranch..."
                git push origin $currentBranch
                Write-Success "All commits synchronized to remote origin."
            }
        }
        else {
            Write-Success "Working tree clean and synchronized with origin. Nothing to commit."
        }
        exit 0
    }

    # 3. Dry run / WhatIf inspection
    if ($WhatIf) {
        Write-Notice "[WhatIf] Local changes detected on [$currentBranch]. Previewing synchronization:"
        git status --short
        git add -A
        $secretHits = Find-StagedSecrets
        if (@($secretHits).Count -gt 0) {
            Write-Fail "[WhatIf] Security Alert: Found possible secret(s) in staged changes:"
            foreach ($hit in @($secretHits)) {
                Write-Host "    Pattern: $($hit.Pattern)" -ForegroundColor Yellow
                Write-Host "    Snippet: $($hit.Snippet)" -ForegroundColor Gray
            }
        }
        $candidateMsg = if ($Message) { $Message } else { Get-AutoCommitMessage -ActiveBranch $currentBranch }
        Write-Notice "[WhatIf] Auto commit message : '$candidateMsg'"
        Write-Notice "[WhatIf] Push destination    : origin/$currentBranch"
        git reset --quiet
        Write-Success "[WhatIf] Dry run completed. No changes committed or pushed."
        exit 0
    }

    # 4. Stage changes & run security scan
    Write-Status "Staging changes..."
    git add -A

    $secretHits = Find-StagedSecrets
    if (@($secretHits).Count -gt 0) {
        Write-Fail "Security gate failed: Possible secret(s) detected in staged changes!"
        foreach ($hit in @($secretHits)) {
            Write-Host "    Pattern: $($hit.Pattern)" -ForegroundColor Yellow
            Write-Host "    Snippet: $($hit.Snippet)" -ForegroundColor Gray
        }
        Write-Notice "Staged files have been un-staged for safety. Please remove credentials before committing."
        git reset --quiet
        exit 1
    }

    # 5. Determine commit message
    if (-not $Message) {
        $Message = Get-AutoCommitMessage -ActiveBranch $currentBranch
        if (-not $Message) {
            $Message = "chore(core): update workspace files"
        }
        Write-Notice "Auto-generated commit message: '$Message'"
    }

    # 6. Commit changes
    Write-Status "Committing changes on [$currentBranch]..."
    git commit -m "$Message"
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "git commit failed."
        exit $LASTEXITCODE
    }

    # 7. Push to remote
    if ($NoPush) {
        Write-Success "Changes committed locally on [$currentBranch]. Push skipped (-NoPush active)."
        exit 0
    }

    Write-Status "Pushing to origin/$currentBranch..."
    git push origin $currentBranch
    if ($LASTEXITCODE -ne 0) {
        Write-Notice "Push was rejected (remote may have new changes). Pulling with rebase and retrying..."
        git pull --rebase --autostash origin $currentBranch
        git push origin $currentBranch
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "Push failed after retry. Please inspect conflicts manually."
            exit $LASTEXITCODE
        }
    }

    Write-Success "Repository synchronized successfully with origin/$currentBranch."
}
catch {
    Write-Fail "Sync error: $_"
    exit 1
}
finally {
    Pop-Location
}
