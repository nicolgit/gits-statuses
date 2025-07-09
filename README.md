# Git Statuses - Monorepo

A unified repository containing multiple deployments for Git repository status scanning across different platforms.

## 📦 Packages Structure

This monorepo contains three separate deployments:

- **`packages/python-pypi/`** - Python CLI package with PyPI deployment
- **`packages/swiftbar-plugin/`** - SwiftBar plugin for macOS menu bar
- **`packages/powershell-module/`** - PowerShell module for Windows/cross-platform

## 🔗 Shared Code

- **`shared/git_tools/`** - Symlinked Git utilities (from python-pypi)
- **`shared/utils/`** - Symlinked utility functions (from python-pypi)
- **`packages/swiftbar-plugin/shared/`** - Local symlinks to shared utilities

## 🛠️ Build Infrastructure

- **`scripts/build-all.sh`** - Builds all packages
- **`scripts/test-all.sh`** - Tests all packages
- **`scripts/deploy/`** - Deployment scripts (ready for expansion)

## ✨ Key Features

1. **Code Sharing**: Swift and Python both use the same Git utilities via symlinks
2. **Separate Deployments**: Each package can be deployed independently
3. **Unified Build**: Single command builds all packages
4. **Shared Git Logic**: Extracted from SwiftBar plugin to shared utilities

## 🚀 Quick Start

### Build All Packages
```bash
./scripts/build-all.sh
```

### Test All Packages
```bash
./scripts/test-all.sh
```

> **Note**: Scripts automatically detect available tools and provide helpful hints:
> - Python package: Uses `uv` if available, falls back to `python`
> - SwiftBar plugin: Validates syntax and basic execution
> - PowerShell module: Requires `pwsh` (install with `brew install powershell` on macOS)

## 📋 Usage

### Python PyPI Package
```bash
# Navigate to the Python package
cd packages/python-pypi

# Install dependencies
uv sync

# Run the CLI (use --path to specify directory)
uv run src/cli.py --path ../..

# For detailed view
uv run src/cli.py --path ../.. --detailed
```

### SwiftBar Plugin
```bash
# Navigate to the SwiftBar plugin
cd packages/swiftbar-plugin

# Run the plugin (specify path to scan)
python3 git_plugin.py ../..

# Or run with default path (~/GitHub)
python3 git_plugin.py
```

### PowerShell Module
```powershell
# Navigate to the PowerShell module
cd packages/powershell-module

# Import the module
Import-Module ./GitStatuses.psd1

# Use the function
Get-GitStatuses

# For detailed view
Get-GitStatuses -Detailed
```

> **Note**: PowerShell Core (`pwsh`) is required. Install with `brew install powershell` on macOS.

## 🔧 Development

Each package maintains its own development workflow while sharing core Git utilities:

1. **Shared utilities** are maintained in `packages/python-pypi/src/`
2. **Symlinks** ensure all packages use the same core logic
3. **Build scripts** validate all packages together
4. **Independent deployment** allows each package to be released separately

### Test Coverage
- **Python PyPI**: Basic import tests and syntax validation
- **SwiftBar Plugin**: Syntax validation and execution testing
- **PowerShell Module**: Module manifest validation and import testing

### Build Outputs
- **Python PyPI**: Creates wheel and source distributions in `packages/python-pypi/dist/`
- **SwiftBar Plugin**: Validates Python syntax and shared utility imports
- **PowerShell Module**: Validates module manifest and function exports

## 📊 What This Tool Does

This tool scans directories for Git repositories and displays a comprehensive table with:

- Repository name
- Current branch
- Commits ahead/behind remote
- Changed files count
- Untracked files count
- Status summary
- Remote URL (in detailed view)

## 🎯 Target Platforms

- **Python**: Cross-platform CLI tool via PyPI
- **SwiftBar**: macOS menu bar integration
- **PowerShell**: Windows/cross-platform module

## 📄 Legacy Information

This monorepo was created from individual PowerShell and Python scripts that provided repository status information. The original functionality is preserved while adding a unified structure for better maintainability and code sharing.

## 🔍 Status Symbols 

- **↑n**: n commits ahead of remote
- **↓n**: n commits behind remote  
- **~n**: n changed files (modified/added/deleted)
- **?n**: n untracked files
- **Clean**: Repository has no pending changes

Examples:
- `↑2 ~1 ?3` = 2 commits ahead, 1 changed file, 3 untracked files
- `↓1 ~2` = 1 commit behind, 2 changed files
- `Clean` = No changes, fully synchronized

## 📋 Requirements

- Git must be installed and available in PATH
- **Python package**: Python 3.7+
- **PowerShell module**: PowerShell 5.1+ or PowerShell Core 6+
- **SwiftBar plugin**: Python 3.7+ and SwiftBar installed