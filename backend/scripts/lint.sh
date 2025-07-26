#!/bin/bash

# Script for linting Django project with Ruff
# Usage: ./scripts/lint.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
FIX=false
FORMAT=false
CHECK_ONLY=false
VERBOSE=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    echo "Django Ruff Linting Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help      Show this help message"
    echo "  -f, --fix       Automatically fix linting issues"
    echo "  --format        Format code with ruff"
    echo "  -c, --check     Only check, don't fix anything"
    echo "  -v, --verbose   Verbose output"
    echo ""
    echo "Examples:"
    echo "  $0                  # Check for issues"
    echo "  $0 --fix           # Check and fix issues"
    echo "  $0 --format        # Format code"
    echo "  $0 --fix --format  # Fix issues and format code"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--fix)
            FIX=true
            shift
            ;;
        --format)
            FORMAT=true
            shift
            ;;
        -c|--check)
            CHECK_ONLY=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if ruff is installed
if ! command -v ruff &> /dev/null; then
    print_error "Ruff is not installed. Please install it with: pip install ruff"
    exit 1
fi

print_status "Starting Django project linting with Ruff..."

# Define directories to check
DIRS_TO_CHECK="config core users recipes"
FILES_TO_CHECK="manage.py"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "This script should be run from the Django project root directory"
    exit 1
fi

# Function to run ruff check
run_ruff_check() {
    local fix_flag=""
    if [ "$FIX" = true ] && [ "$CHECK_ONLY" = false ]; then
        fix_flag="--fix"
    fi

    local verbose_flag=""
    if [ "$VERBOSE" = true ]; then
        verbose_flag="--verbose"
    fi

    print_status "Running Ruff linting checks..."

    if ruff check $fix_flag $verbose_flag $DIRS_TO_CHECK $FILES_TO_CHECK; then
        print_success "Ruff check completed successfully!"
        return 0
    else
        print_error "Ruff found issues that need attention"
        return 1
    fi
}

# Function to run ruff format
run_ruff_format() {
    if [ "$CHECK_ONLY" = true ]; then
        print_status "Running Ruff format check (dry-run)..."
        if ruff format --diff $DIRS_TO_CHECK $FILES_TO_CHECK; then
            print_success "Code is properly formatted!"
            return 0
        else
            print_warning "Code needs formatting"
            return 1
        fi
    else
        print_status "Running Ruff formatter..."
        if ruff format $DIRS_TO_CHECK $FILES_TO_CHECK; then
            print_success "Code formatting completed!"
            return 0
        else
            print_error "Formatting failed"
            return 1
        fi
    fi
}

# Main execution
EXIT_CODE=0

# Run linting
if ! run_ruff_check; then
    EXIT_CODE=1
fi

# Run formatting if requested
if [ "$FORMAT" = true ]; then
    if ! run_ruff_format; then
        EXIT_CODE=1
    fi
fi

# Summary
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    print_success "All checks passed! ✨"
else
    print_error "Some issues were found. Please review and fix them."
    echo ""
    echo "Quick fixes:"
    echo "  • Run with --fix to automatically fix linting issues"
    echo "  • Run with --format to format your code"
    echo "  • Check the Ruff documentation for specific rule explanations"
fi

exit $EXIT_CODE
