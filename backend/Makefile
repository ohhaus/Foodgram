.PHONY: help lint lint-fix format format-check check test clean install dev migrate runserver shell

# Default target
help:
	@echo "Available commands:"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         - Run Ruff linting checks"
	@echo "  lint-fix     - Run Ruff linting with auto-fix"
	@echo "  format       - Format code with Ruff"
	@echo "  format-check - Check code formatting without changes"
	@echo "  check        - Run all checks (lint + format check)"
	@echo ""
	@echo "Django Commands:"
	@echo "  install      - Install dependencies"
	@echo "  migrate      - Run Django migrations"
	@echo "  runserver    - Start Django development server"
	@echo "  shell        - Start Django shell"
	@echo "  test         - Run Django tests"
	@echo ""
	@echo "Development:"
	@echo "  dev          - Run all development setup (install + migrate)"
	@echo "  clean        - Clean cache and temporary files"

# Code quality targets
lint:
	@echo "🔍 Running Ruff linting checks..."
	ruff check config core users recipes 

lint-fix:
	@echo "🔧 Running Ruff linting with auto-fix..."
	ruff check --fix config core users recipes

format:
	@echo "🎨 Formatting code with Ruff..."
	ruff format config core users recipes

format-check:
	@echo "📋 Checking code formatting..."
	ruff format --diff config core users recipes

check: lint format-check
	@echo "✅ All code quality checks completed!"

# Django targets
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

migrate:
	@echo "🗄️  Running Django migrations..."
	python manage.py migrate

runserver:
	@echo "🚀 Starting Django development server..."
	python manage.py runserver

shell:
	@echo "🐍 Starting Django shell..."
	python manage.py shell

test:
	@echo "🧪 Running Django tests..."
	python manage.py test

# Development targets
dev: install migrate
	@echo "🎯 Development environment ready!"
	@echo "Run 'make runserver' to start the server"

clean:
	@echo "🧹 Cleaning cache and temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .ruff_cache/
	@echo "✨ Cleanup completed!"

# Comprehensive development workflow
dev-check: clean lint-fix format test
	@echo "🎉 Full development check completed!"

# Pre-commit hook simulation
pre-commit: lint-fix format
	@echo "🚦 Pre-commit checks completed!"
