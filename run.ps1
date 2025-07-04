#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Git Status Scanner - Displays status information for all Git repositories in the current directory
.DESCRIPTION
    This script scans the current directory for Git repositories and displays a table with:
    - Repository name
    - Remote URL
    - Branch name
    - Commits ahead/behind remote
    - Total commits
    - Changed files count
    - Status summary
.EXAMPLE
    .\run.ps1
    Scans current directory and displays git status for all repositories
#>

param(
    [string]$Path = ".",
    [switch]$Detailed,
    [switch]$Help
)

if ($Help) {
    Get-Help $MyInvocation.MyCommand.Definition -Detailed
    return
}

# Function to get Git repository information
function Get-GitRepositoryInfo {
    param(
        [string]$RepoPath
    )
    
    $originalLocation = Get-Location
    try {
        Set-Location $RepoPath
        
        # Check if it's a valid Git repository
        $isGitRepo = Test-Path ".git" -PathType Container
        if (-not $isGitRepo) {
            # Check if it's a Git repository (might be in a subdirectory)
            $gitCheck = git rev-parse --is-inside-work-tree 2>$null
            if ($gitCheck -ne "true") {
                return $null
            }
        }
        
        # Get repository name
        $repoName = Split-Path $RepoPath -Leaf
        
        # Get remote URL
        $remoteUrl = git config --get remote.origin.url 2>$null
        if (-not $remoteUrl) {
            $remoteUrl = "No remote"
        }
        
        # Get current branch
        $currentBranch = git branch --show-current 2>$null
        if (-not $currentBranch) {
            $currentBranch = "HEAD detached"
        }
        
        # Get ahead/behind information
        $aheadBehind = git rev-list --left-right --count origin/$currentBranch...$currentBranch 2>$null
        if ($aheadBehind) {
            $parts = $aheadBehind -split '\s+'
            $behind = [int]$parts[0]
            $ahead = [int]$parts[1]
        } else {
            $ahead = 0
            $behind = 0
        }
        
        # Get total commit count
        $totalCommits = git rev-list --count HEAD 2>$null
        if (-not $totalCommits) {
            $totalCommits = 0
        }
        
        # Get changed files count
        $changedFiles = (git status --porcelain 2>$null | Measure-Object).Count
        
        # Get status summary
        $status = git status --porcelain 2>$null
        $statusSummary = "Clean"
        if ($status) {
            $untracked = ($status | Where-Object { $_ -match "^\?\?" } | Measure-Object).Count
            $modified = ($status | Where-Object { $_ -match "^.M" } | Measure-Object).Count
            $staged = ($status | Where-Object { $_ -match "^M" } | Measure-Object).Count
            $deleted = ($status | Where-Object { $_ -match "^.D" } | Measure-Object).Count
            
            $statusParts = @()
            if ($staged -gt 0) { $statusParts += "$staged staged" }
            if ($modified -gt 0) { $statusParts += "$modified modified" }
            if ($deleted -gt 0) { $statusParts += "$deleted deleted" }
            if ($untracked -gt 0) { $statusParts += "$untracked untracked" }
            
            $statusSummary = $statusParts -join ", "
        }
        
        # Check if there are unpushed commits
        $unpushedCommits = git log origin/$currentBranch..HEAD --oneline 2>$null
        $unpushedCount = if ($unpushedCommits) { ($unpushedCommits | Measure-Object).Count } else { 0 }
        
        # Check if there are unpulled commits
        $unpulledCommits = git log HEAD..origin/$currentBranch --oneline 2>$null
        $unpulledCount = if ($unpulledCommits) { ($unpulledCommits | Measure-Object).Count } else { 0 }
        
        return [PSCustomObject]@{
            Repository = $repoName
            Branch = $currentBranch
            RemoteUrl = $remoteUrl
            Ahead = $ahead
            Behind = $behind
            TotalCommits = [int]$totalCommits
            ChangedFiles = $changedFiles
            Status = $statusSummary
            UnpushedCommits = $unpushedCount
            UnpulledCommits = $unpulledCount
            Path = $RepoPath
        }
    }
    catch {
        Write-Warning "Error processing repository at $RepoPath`: $_"
        return $null
    }
    finally {
        Set-Location $originalLocation
    }
}

# Function to format the output table
function Format-GitStatusTable {
    param(
        [array]$Repositories,
        [switch]$Detailed
    )
    
    if ($Repositories.Count -eq 0) {
        Write-Host "No Git repositories found in the current directory." -ForegroundColor Yellow
        return
    }
    
    Write-Host "`nGit Repositories Status Summary" -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
    
    if ($Detailed) {
        $Repositories | Format-Table -Property Repository, Branch, RemoteUrl, Ahead, Behind, TotalCommits, ChangedFiles, Status -AutoSize
    } else {
        $Repositories | Format-Table -Property Repository, Branch, @{Name="↑Push";Expression={$_.Ahead}}, @{Name="↓Pull";Expression={$_.Behind}}, @{Name="Commits";Expression={$_.TotalCommits}}, @{Name="Changed";Expression={$_.ChangedFiles}}, Status -AutoSize
    }
    
    # Summary statistics
    $totalRepos = $Repositories.Count
    $reposWithChanges = ($Repositories | Where-Object { $_.ChangedFiles -gt 0 }).Count
    $reposAhead = ($Repositories | Where-Object { $_.Ahead -gt 0 }).Count
    $reposBehind = ($Repositories | Where-Object { $_.Behind -gt 0 }).Count
    
    Write-Host "`nSummary:" -ForegroundColor Cyan
    Write-Host "  Total repositories: $totalRepos"
    Write-Host "  Repositories with changes: $reposWithChanges" -ForegroundColor $(if ($reposWithChanges -gt 0) { "Yellow" } else { "Green" })
    Write-Host "  Repositories ahead of remote: $reposAhead" -ForegroundColor $(if ($reposAhead -gt 0) { "Yellow" } else { "Green" })
    Write-Host "  Repositories behind remote: $reposBehind" -ForegroundColor $(if ($reposBehind -gt 0) { "Yellow" } else { "Green" })
}

# Main execution
Write-Host "Scanning for Git repositories..." -ForegroundColor Green

# Get all directories in the specified path
$directories = Get-ChildItem -Path $Path -Directory

# Check if current directory is also a Git repository
$currentDirInfo = Get-GitRepositoryInfo -RepoPath $Path
$repositories = @()

if ($currentDirInfo) {
    $repositories += $currentDirInfo
}

# Process each subdirectory
foreach ($dir in $directories) {
    $repoInfo = Get-GitRepositoryInfo -RepoPath $dir.FullName
    if ($repoInfo) {
        $repositories += $repoInfo
    }
}

# Display results
Format-GitStatusTable -Repositories $repositories -Detailed:$Detailed

# Check for Git availability
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is not installed or not in PATH. Please install Git to use this script."
    return
}

Write-Host "`nDone! 🎉" -ForegroundColor Green