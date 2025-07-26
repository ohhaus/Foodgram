#!/bin/bash

# Script to set up Git hooks for Django project with Ruff
# Usage: ./scripts/setup-hooks.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "This is not a Git repository. Please run 'git init' first."
    exit 1
fi

print_status "Setting up Git hooks for Django project..."

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Create pre-commit hook
print_status "Creating pre-commit hook..."
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Pre-commit hook for Django project with Ruff
# This hook runs before each commit to ensure code quality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[PRE-COMMIT]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PRE-COMMIT]${NC} $1"
}

print_error() {
    echo -e "${RED}[PRE-COMMIT]${NC} $1"
}

print_status "Running pre-commit checks..."

# Check if ruff is available
if ! command -v ruff &> /dev/null; then
    print_error "Ruff is not installed. Please install it with: pip install ruff"
    exit 1
fi

# Get list of Python files that are staged for commit
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -z "$STAGED_FILES" ]; then
    print_status "No Python files to check."
    exit 0
fi

print_status "Checking staged Python files: $STAGED_FILES"

# Create a temporary directory for staged files
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Copy staged files to temp directory maintaining structure
for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        mkdir -p "$TEMP_DIR/$(dirname "$file")"
        git show ":$file" > "$TEMP_DIR/$file"
    fi
done

# Change to temp directory for checks
cd "$TEMP_DIR"

# Run Ruff checks on staged files
print_status "Running Ruff linting..."
if ! ruff check $STAGED_FILES; then
    print_error "Ruff linting failed. Please fix the issues and try again."
    print_error "You can run 'ruff check --fix' to automatically fix some issues."
    exit 1
fi

# Run Ruff formatting check
print_status "Checking code formatting..."
if ! ruff format --diff $STAGED_FILES | grep -q "^$"; then
    print_error "Code is not properly formatted. Please run 'ruff format' and commit again."
    exit 1
fi

print_success "All pre-commit checks passed! ✨"
EOF

# Make pre-commit hook executable
chmod +x .git/hooks/pre-commit
print_success "Pre-commit hook created and made executable"

# Create pre-push hook
print_status "Creating pre-push hook..."
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash

# Pre-push hook for Django project
# This hook runs before pushing to ensure comprehensive checks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[PRE-PUSH]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PRE-PUSH]${NC} $1"
}

print_error() {
    echo -e "${RED}[PRE-PUSH]${NC} $1"
}

print_status "Running pre-push checks..."

# Check if we're in the right directory (has manage.py)
if [ ! -f "manage.py" ]; then
    print_error "This doesn't appear to be a Django project root."
    exit 1
fi

# Run comprehensive Ruff check
print_status "Running comprehensive Ruff checks..."
if ! ruff check config core users recipes manage.py; then
    print_error "Ruff checks failed. Please fix issues before pushing."
    exit 1
fi

# Check code formatting
print_status "Verifying code formatting..."
if ! ruff format --diff config core users recipes manage.py | grep -q "^$"; then
    print_error "Code formatting issues found. Please run 'ruff format' before pushing."
    exit 1
fi

# Run Django tests if they exist
if [ -d "tests" ] || find . -name "*test*.py" -not -path "./venv/*" -not -path "./.venv/*" | grep -q .; then
    print_status "Running Django tests..."
    if ! python manage.py test --verbosity=0; then
        print_error "Tests failed. Please fix failing tests before pushing."
        exit 1
    fi
fi

print_success "All pre-push checks passed! 🚀"
EOF

# Make pre-push hook executable
chmod +x .git/hooks/pre-push
print_success "Pre-push hook created and made executable"

# Create commit-msg hook for better commit messages
print_status "Creating commit-msg hook..."
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash

# Commit message hook to ensure good commit message format
# This hook checks commit message format and content

commit_regex='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\(.+\))?: .{1,50}'

error_msg="Commit message format error!

Your commit message should follow the format:
<type>[optional scope]: <description>

Types:
  feat:     A new feature
  fix:      A bug fix
  docs:     Documentation only changes
  style:    Changes that do not affect the meaning of the code
  refactor: A code change that neither fixes a bug nor adds a feature
  perf:     A code change that improves performance
  test:     Adding missing tests or correcting existing tests
  build:    Changes that affect the build system or external dependencies
  ci:       Changes to CI configuration files and scripts
  chore:    Other changes that don't modify src or test files

Examples:
  feat: add user authentication
  fix(api): resolve login endpoint error
  docs: update README with setup instructions
  style: format code according to PEP 8
  refactor: simplify user model validation"

if ! grep -qE "$commit_regex" "$1"; then
    echo "$error_msg" >&2
    exit 1
fi
EOF

# Make commit-msg hook executable
chmod +x .git/hooks/commit-msg
print_success "Commit-msg hook created and made executable"

# Summary
echo ""
print_success "Git hooks setup completed! 🎉"
echo ""
echo "The following hooks have been installed:"
echo "  📝 pre-commit:  Runs Ruff linting and formatting checks on staged files"
echo "  🚀 pre-push:    Runs comprehensive checks before pushing"
echo "  💬 commit-msg:  Ensures proper commit message format"
echo ""
echo "These hooks will help maintain code quality automatically."
echo "If you need to bypass hooks temporarily, use:"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""
print_warning "Remember: Hooks are local to your repository and won't be shared with other developers."
print_status "Other developers should run this script to set up their own hooks."
