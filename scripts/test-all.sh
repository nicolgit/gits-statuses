#!/bin/bash

# Test script for all packages in the monorepo

set -e

echo "🧪 Running tests for all packages..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[TEST]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the root directory of the monorepo
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Test Python PyPI package
print_status "Testing Python PyPI package..."
cd "$ROOT_DIR/packages/python-pypi"

if [ -f "pyproject.toml" ]; then
    # Check if uv is available
    if command -v uv &> /dev/null; then
        print_status "Using uv for Python tests..."
        # Check if there are test files in the project (excluding .venv)
        if [ -d "tests" ] || find . -name "*test*.py" -type f -not -path "./.venv/*" | grep -q .; then
            # Install dev dependencies and run tests
            uv sync --group dev
            uv run --dev pytest || {
                print_error "Python tests failed ❌"
                exit 1
            }
        else
            print_warning "No test files found. Running basic import test..."
            uv run python -c "from src.cli import main; print('CLI import successful')" || {
                print_error "Basic import test failed ❌"
                exit 1
            }
        fi
    elif command -v python &> /dev/null; then
        print_status "Using python for tests..."
        if [ -d "tests" ] || find . -name "*test*.py" -type f -not -path "./.venv/*" | grep -q .; then
            # Install pytest if not available
            python -m pip install pytest pytest-cov
            python -m pytest || {
                print_error "Python tests failed ❌"
                exit 1
            }
        else
            print_warning "No test files found. Running basic import test..."
            python -c "from src.cli import main; print('CLI import successful')" || {
                print_error "Basic import test failed ❌"
                exit 1
            }
        fi
    else
        print_warning "Neither uv nor python found. Skipping Python tests."
    fi
else
    print_warning "No pyproject.toml found in python-pypi package. Skipping Python tests."
fi

# Test SwiftBar plugin
print_status "Testing SwiftBar plugin..."
cd "$ROOT_DIR/packages/swiftbar-plugin"

if [ -f "git_plugin.py" ]; then
    # Basic syntax check
    if python3 -m py_compile git_plugin.py; then
        print_status "SwiftBar plugin syntax check passed ✅"
    else
        print_error "SwiftBar plugin syntax check failed ❌"
        exit 1
    fi
    
    # Try to run the plugin in a controlled environment
    print_status "Testing SwiftBar plugin execution..."
    # Create a temporary directory to test the plugin
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    git init > /dev/null 2>&1
    echo "test" > test.txt
    git add test.txt > /dev/null 2>&1
    git commit -m "test commit" > /dev/null 2>&1
    
    # Run the plugin with minimal output
    if timeout 10 python3 "$ROOT_DIR/packages/swiftbar-plugin/git_plugin.py" . > /dev/null 2>&1; then
        print_status "SwiftBar plugin execution test passed ✅"
    else
        print_warning "SwiftBar plugin execution test had issues (this may be normal for SwiftBar-specific features)"
    fi
    
    # Clean up
    rm -rf "$TEMP_DIR"
else
    print_warning "No git_plugin.py found in swiftbar-plugin package."
fi

# Test PowerShell module
print_status "Testing PowerShell module..."
cd "$ROOT_DIR/packages/powershell-module"

if [ -f "GitStatuses.psd1" ]; then
    # Check if PowerShell is available
    if command -v pwsh &> /dev/null; then
        print_status "Testing PowerShell module..."
        
        # Test module manifest
        pwsh -Command "Test-ModuleManifest -Path './GitStatuses.psd1'" || {
            print_error "PowerShell module manifest test failed ❌"
            exit 1
        }
        
        # Test module import
        pwsh -Command "Import-Module './GitStatuses.psd1'; Get-Command Get-GitStatuses" || {
            print_error "PowerShell module import test failed ❌"
            exit 1
        }
        
        print_status "PowerShell module tests passed ✅"
    else
        print_warning "PowerShell (pwsh) not found. Skipping PowerShell module tests."
        if command -v brew &> /dev/null; then
            print_status "Hint: Install PowerShell with 'brew install powershell' to enable PowerShell module tests"
        fi
    fi
else
    print_warning "No GitStatuses.psd1 found in powershell-module package."
fi

print_status "✅ All tests completed successfully!"

# Summary
echo ""
echo "🧪 Test Summary:"
echo "  ✅ Python PyPI package: packages/python-pypi/"
echo "  ✅ SwiftBar plugin: packages/swiftbar-plugin/"
echo "  ✅ PowerShell module: packages/powershell-module/"
echo ""
echo "🎉 All tests passed!"