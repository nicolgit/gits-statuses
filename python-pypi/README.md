# gits-statuses

A CLI tool for scanning directories and displaying Git repository status information. This tool provides a comprehensive overview of all your Git repositories in a clean, tabular format.

Notes:
- Implements a single CLI utility that is:
  - Distributed and downloaded via [PyPi](https://pypi.org/project/gits-statuses/)
  - Used globally as a bona fide CLI utility
  - Easy to install and use for the end user
  - Compatible with any terminal

## Features

This scans your directories and displays:

**Standard View:**
- Repository name
- Current branch
- Last Commit hash
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
```bash
# Install gits-statuses
uv tool install gits-statuses

# Verify installation
gits-statuses --version
```

## Usage

### Basic Commands

```bash
# Basic usage - scan current directory
gits-statuses

# Detailed view with remote URLs and total commits
gits-statuses --detailed

# Scan a specific directory
gits-statuses --path /path/to/projects

# Show help
gits-statuses --help
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
Repository                    | Branch   | Commit                                   | Ahead | Behind | Changed | Untracked | Total Commits | Status | Remote URL                                            
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
andrei-git-statuses           | main     | 0a1b868f152356a10209aaa32092f7c6a9 |       |        |         |           | 39            | Clean  | https://github.com/andreinonea/gits-statuses/                     
azure-firewall-mon            | main     | 8673cfd7fb5a280f807e70c2dd3472862f |       |        |         |           | 211           | Clean  | https://github.com/nicolgit/azure-firewall-mon                    
blast                         | main     | 724a56be21379c2b7beb4770b5d11ef997 |       |        |         |           | 530           | Clean  | https://github.com/nicolgit/blast.git                             
brick-o-ponics                | main     | 2151f4ac998912c94007492c53d79d4a90 |       |        |         |           | 3             | Clean  | https://github.com/nicolgit/brick-o-ponics                        
cidr-tool                     | master   | 389f3901b0f9c23ce25175f68a859612b2 |       |        |         |           | 38            | Clean  | https://github.com/nicolgit/cidr-tool                             
containerapps-albumapi-csharp | main     | 89bcf94e1a05eefde083d7473ecbba9433 |       |        | 1       | 1         | 27            | ~1 ?1  | https://github.com/azure-samples/containerapps-albumapi-csharp.git
drawio-cooking-shapes         | main     | c455d2b8e3f33c049ec0a60bcf3ba8aa31 |       |        |         |           | 19            | Clean  | https://github.com/nicolgit/drawio-cooking-shapes.git             
gits-statuses                 | main     | 7be175881e8d85cb363422be471e77475d |       |        |         |           | 25            | Clean  | https://github.com/nicolgit/gits-statuses                         
hub-and-spoke-playground      | main     | e9ab8852d2ac4eb07d07158c3e679cec5a |       |        |         |           | 250           | Clean  | https://github.com/nicolgit/hub-and-spoke-playground              
metro-proximity               | main     | b44b59bbb5e9e3bd59e51d13105dd69dfc |       |        |         |           | 21            | Clean  | https://github.com/nicolgit/metro-proximity                       
nicolgit.github.io            | master   | 552f0373ba3a499cfa5afe8d7d5a95183b |       |        |         |           | 3063          | Clean  | https://github.com/nicolgit/nicolgit.github.io.git                
Open.Padlock                  | gen-maui | 458c303b08a3c1d6554baed83be0ba720a |       |        | 2       | 1         | 162           | ~2 ?1  | https://github.com/nicolgit/Open.Padlock                          
personal                      | master   | c52682ae2a13beb3e297d3c694bb3f5376 |       |        |         |           | 231           | Clean  | https://github.com/nicolgit/personal-certificates                 
proximity-test                | main     | c3e80667391da1631992d9cfecb770039a |       |        |         |           | 108           | Clean  | https://github.com/CaledosLab/proximity-test                      

Summary:
  Total repositories: 14
  Repositories with changes: 2
  Repositories ahead of remote: 0
  Repositories behind remote: 0
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
