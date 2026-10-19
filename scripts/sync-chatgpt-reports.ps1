<#
.SYNOPSIS
Pushes any new ChatGPT research report to origin/main.

.DESCRIPTION
The external ChatGPT research task writes dated reports to
topics/chatgpt-reports/<YYYY-MM-DD>.md on this machine but does not commit
or push them (see topics/chatgpt-reports/README.md). This script closes
that gap: it fast-forwards main, looks for new untracked dated report
files, and commits + pushes any it finds. Intended to run on an unattended
daily schedule so it's robust to the source task's own (unverified)
schedule time/timezone -- a day with nothing new is a fast no-op.

Never force-pushes, never touches any file outside
topics/chatgpt-reports/*.md, and aborts without changing anything if main
can't fast-forward cleanly (e.g. local history has diverged) rather than
guessing at a resolution.
#>

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$logFile = Join-Path $repoRoot ".chatgpt-sync.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp  $Message" | Out-File -FilePath $logFile -Append -Encoding utf8
}

try {
    Set-Location $repoRoot

    git checkout -q main 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Log "ABORT: could not check out main."
        exit 1
    }

    git fetch -q origin main 2>&1 | Out-Null
    git merge -q --ff-only origin/main 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Log "ABORT: local main could not fast-forward to origin/main (diverged?). Needs manual attention."
        exit 1
    }

    $newFiles = git status --porcelain -- "topics/chatgpt-reports/*.md" |
        Where-Object { $_ -match '^\?\?\s' } |
        ForEach-Object { $_.Substring(3).Trim() } |
        Where-Object { (Split-Path $_ -Leaf) -match '^\d{4}-\d{2}-\d{2}\.md$' }

    if (-not $newFiles) {
        Write-Log "No new report files found."
        exit 0
    }

    git add -- $newFiles
    $fileList = ($newFiles -join ", ")

    git commit -q -m "Add ChatGPT research report(s): $fileList" -m "Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR: commit failed for $fileList."
        exit 1
    }

    git push -q origin main 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR: commit succeeded but push failed for $fileList. Local commit is in place -- retry the push manually."
        exit 1
    }

    Write-Log "Pushed: $fileList"
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}
