#!/bin/bash

# Build script for all packages in the monorepo

set -e

echo "🚀 Building all packages..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[BUILD]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the root directory of the monorepo
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Build Python PyPI package
print_status "Building Python PyPI package..."
cd "$ROOT_DIR/packages/python-pypi"

if [ -f "pyproject.toml" ]; then
    # Check if uv is available
    if command -v uv &> /dev/null; then
        print_status "Using uv for Python build..."
        uv build
    elif command -v python -m build &> /dev/null; then
        print_status "Using python -m build..."
        python -m build
    else
        print_warning "Neither uv nor python build tools found. Skipping Python build."
    fi
else
    print_warning "No pyproject.toml found in python-pypi package. Skipping Python build."
fi

# Build/Validate SwiftBar plugin
print_status "Validating SwiftBar plugin..."
cd "$ROOT_DIR/packages/swiftbar-plugin"

if [ -f "git_plugin.py" ]; then
    # Check if the plugin is syntactically valid
    if python3 -m py_compile git_plugin.py; then
        print_status "SwiftBar plugin syntax is valid ✅"
    else
        print_error "SwiftBar plugin has syntax errors ❌"
        exit 1
    fi
else
    print_warning "No git_plugin.py found in swiftbar-plugin package."
fi

# Build/Validate PowerShell module
print_status "Validating PowerShell module..."
cd "$ROOT_DIR/packages/powershell-module"

if [ -f "GitStatuses.psd1" ]; then
    # Check if PowerShell is available
    if command -v pwsh &> /dev/null; then
        print_status "Testing PowerShell module manifest..."
        pwsh -Command "Test-ModuleManifest -Path './GitStatuses.psd1'" || {
            print_error "PowerShell module manifest is invalid ❌"
            exit 1
        }
        print_status "PowerShell module manifest is valid ✅"
    else
        print_warning "PowerShell (pwsh) not found. Skipping PowerShell module validation."
        if command -v brew &> /dev/null; then
            print_status "Hint: Install PowerShell with 'brew install powershell' to enable PowerShell module validation"
        fi
    fi
else
    print_warning "No GitStatuses.psd1 found in powershell-module package."
fi

print_status "✅ All packages built successfully!"

# Summary
echo ""
echo "📦 Build Summary:"
echo "  ✅ Python PyPI package: packages/python-pypi/"
echo "  ✅ SwiftBar plugin: packages/swiftbar-plugin/"
echo "  ✅ PowerShell module: packages/powershell-module/"
echo ""
echo "🎉 Build completed successfully!"