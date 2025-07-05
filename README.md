# Welcome to gits-statuses
In this repo you can find both PowerShell and Python scripts that once executed into the root directory where you have all your local repos
give you a table in output that shows repo status information like branch name, commits ahead/behind, changed files, untracked files, and more, 
in a similar way oh-my-posh provides on the prompt, but here you have a massive view of all your repos.

# How to use it

Clone the repo in the same folder you have all your repos

```
git clone https://github.com/nicolgit/gits-statuses  
```

## PowerShell Version

Then type:

```
# Basic usage - scan current directory
.\gits-statuses\run.ps1

# Detailed view with full remote URLs
.\gits-statuses\run.ps1 -Detailed

# Scan a specific directory
.\gits-statuses\run.ps1 -Path "C:\MyProjects"

# Show help
.\gits-statuses\run.ps1 -Help
```

## Python Version

Alternatively, you can use the Python version:

```
# Basic usage - scan current directory
python3 gits-statuses/run.py

# Detailed view with remote URLs, total commits, and status summary
python3 gits-statuses/run.py --detailed

# Scan a specific directory
python3 gits-statuses/run.py /path/to/projects

# Show help
python3 gits-statuses/run.py --help
```

### Features

Both scripts provide:

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

# Samples

## PowerShell Version

**Standard view (shows only repositories with changes):**
```
Repository    Branch ↑ Push ↓ Pull ~ Changed ? Untracked
--------------------------------------------------------
gits-statuses main   1             1         1         
my-project    dev    2             3         2         
web-app       main         2       1                   

Summary:
  Total repositories: 5
  Repositories with changes: 3
  Repositories ahead of remote: 2
  Repositories behind remote: 1
  Repositories with untracked files: 2
```

**Detailed view (shows all repositories):**
```
Repository    Branch ↑ Push ↓ Pull ~ Changed ? Untracked TotalCommits Status                    RemoteUrl                               
---------------------------------------------------------------------------------------------------------------------------------------
api-service   main                                       45           Clean                     https://github.com/user/api-service
gits-statuses main   1             1         1           9            1 staged, 1 untracked     https://github.com/nicolgit/gits-statuses
my-project    dev    2             3         2           67           2 staged, 3 modified, ... https://github.com/user/my-project
utils-lib     main                                       23           Clean                     https://github.com/user/utils-lib
web-app       main          2      1                     102          1 modified                https://github.com/user/web-app

Summary:
  Total repositories: 5
  Repositories with changes: 3
  Repositories ahead of remote: 2
  Repositories behind remote: 1
  Repositories with untracked files: 2
```

## Python Version

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

## Requirements

- **PowerShell version**: PowerShell 5.1+ or PowerShell Core 6+
- **Python version**: Python 3.7+
- Git must be installed and available in PATH

## Status Symbols (Python Version)

The Python version uses intuitive symbols in the detailed view's status column:

- **↑n**: n commits ahead of remote
- **↓n**: n commits behind remote  
- **~n**: n changed files (modified/added/deleted)
- **?n**: n untracked files
- **Clean**: Repository has no pending changes

Examples:
- `↑2 ~1 ?3` = 2 commits ahead, 1 changed file, 3 untracked files
- `↓1 ~2` = 1 commit behind, 2 changed files
- `Clean` = No changes, fully synchronized