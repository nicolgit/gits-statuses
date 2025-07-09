# gitskan

A CLI tool for scanning directories and displaying Git repository status information. `gitskan` is a fork of [gits-statuses](https://github.com/nicolgit/gits-statuses) which provides a comprehensive overview of all your Git repositories in a clean, tabular format.

Notes:
- This fork was catalyzed by this [GitHub issue](https://github.com/nicolgit/gits-statuses/issues/1)
- This is meant to implement the exact functionality but in a single CLI executable
- Renamed to `gitskan` as to not conflict with `gits-statuses` and to further simplify CLI command
  - Executable name in CLI: `gsk`

## Features

This scans your directories and displays:

**Standard View:**
- Repository name
- Current branch
- Commits ahead of remote
- Commits behind remote  
- Changed files count
- Untracked files count
- Only shows repositories with changes (clean repos are hidden)

**Detailed View:**
- All columns from standard view
- Total commits count
- Status summary (e.g., "↑1 ~2 ?3" for 1 ahead, 2 changed, 3 untracked)
- Remote URL
- Shows ALL repositories (including clean ones)

**Enhanced Summary:**
- Total repositories found
- Repositories with changes
- Repositories ahead of remote
- Repositories behind remote
- Repositories with untracked files

## Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/)

### Install with uv (Recommended)
Note: This is only being temporarily published as an OS CLI tool to PyPi to showcase how it can be distributed and used. The hope is to merge this fork!

```bash
# Install uv if you haven't already
pip install uv     # or brew install uv on mac

# Install gitskan
uv tool install gitskan

# Verify installation
gsk --version
```

## Usage

### Basic Commands

```bash
# Basic usage - scan current directory
gsk

# Detailed view with remote URLs and total commits
gsk --detailed

# Scan a specific directory
gsk --path /path/to/projects

# Show help
gsk --help
```

### Examples

**Standard view (shows only repositories with changes):**
```
Repository    | Branch | Ahead | Behind | Changed | Untracked
-------------------------------------------------------------
gits-statuses | main   | 1     |        | 1       | 1        
my-project    | dev    | 2     |        | 3       | 2        
web-app       | main   |       | 2      | 1       |          

Summary:
  Total repositories: 5
  Repositories with changes: 3
  Repositories ahead of remote: 2
  Repositories behind remote: 1
  Repositories with untracked files: 2
```

**Detailed view (shows all repositories):**
```
Repository    | Branch | Ahead | Behind | Changed | Untracked | Total Commits | Status   | Remote URL                               
---------------------------------------------------------------------------------------------------------------
api-service   | main   |       |        |         |           | 45            | Clean    | https://github.com/user/api-service
gits-statuses | main   | 1     |        | 1       | 1         | 9             | ↑1 ~1 ?1 | https://github.com/nicolgit/gits-statuses
my-project    | dev    | 2     |        | 3       | 2         | 67            | ↑2 ~3 ?2 | https://github.com/user/my-project
utils-lib     | main   |       |        |         |           | 23            | Clean    | https://github.com/user/utils-lib
web-app       | main   |       | 2      | 1       |           | 102           | ↓2 ~1    | https://github.com/user/web-app

Summary:
  Total repositories: 5
  Repositories with changes: 3
  Repositories ahead of remote: 2
  Repositories behind remote: 1
  Repositories with untracked files: 2
```

## Status Symbols 

- **↑n**: n commits ahead of remote
- **↓n**: n commits behind remote  
- **~n**: n changed files (modified/added/deleted)
- **?n**: n untracked files
- **Clean**: Repository has no pending changes

Examples:
- `↑2 ~1 ?3` = 2 commits ahead, 1 changed file, 3 untracked files
- `↓1 ~2` = 1 commit behind, 2 changed files
- `Clean` = No changes, fully synchronized
