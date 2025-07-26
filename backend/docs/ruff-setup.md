# Настройка Ruff для Django проекта

## Оглавление

1. [Введение](#введение)
2. [Установка](#установка)
3. [Конфигурация](#конфигурация)
4. [Использование](#использование)
5. [Интеграция с редакторами](#интеграция-с-редакторами)
6. [Git Hooks](#git-hooks)
7. [Команды Make](#команды-make)
8. [Скрипты](#скрипты)
9. [Troubleshooting](#troubleshooting)

## Введение

Ruff — это современный и быстрый линтер и форматтер для Python, который заменяет множество инструментов:
- **Линтинг**: flake8, pylint, pycodestyle, pyflakes
- **Форматирование**: black, isort
- **Проверка безопасности**: bandit (частично)

### Особенности настройки для этого проекта

- **Длина строки**: 79 символов (PEP 8)
- **Кавычки**: одинарные для строк, двойные для docstring
- **Импорты**: автоматическая сортировка
- **Django-специфичные правила**: включены

## Установка

```bash
# Установка Ruff
pip install ruff

# Или добавить в requirements.txt
echo "ruff" >> requirements.txt
pip install -r requirements.txt
```

## Конфигурация

### Файл конфигурации `ruff.toml`

```toml
# Основные настройки
line-length = 79
target-version = "py311"

# Исключаемые директории и файлы
exclude = [
    "migrations",
    "venv",
    ".venv",
    "env",
    ".env",
    "__pycache__",
    ".git",
    "staticfiles",
    "media",
]

# Настройки линтинга
[lint]
# Выбор правил для проверки
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "Q",   # flake8-quotes
    "SIM", # flake8-simplify
    "RUF", # ruff-specific rules
]

# Игнорируемые правила
ignore = [
    "E501", # line too long (handled by formatter)
    "B008", # do not perform function calls in argument defaults
]

# Настройки для конкретных файлов
[lint.per-file-ignores]
"config/settings*.py" = ["F405", "F403"]
"**/migrations/*.py" = ["E501", "F401", "F811"]
"manage.py" = ["T201"]

# Настройки isort для Django
[lint.isort]
known-first-party = ["config", "core", "users", "recipes"]
section-order = [
    "future",
    "standard-library",
    "third-party",
    "first-party",
    "local-folder",
]
split-on-trailing-comma = true

# Настройки для flake8-quotes
[lint.flake8-quotes]
inline-quotes = "single"
multiline-quotes = "double"
docstring-quotes = "double"
avoid-escape = true

# Настройки форматирования
[format]
quote-style = "single"
indent-style = "space"
line-ending = "auto"
```

### Объяснение основных настроек

| Параметр | Значение | Описание |
|----------|----------|----------|
| `line-length` | 79 | Максимальная длина строки |
| `target-version` | "py311" | Целевая версия Python |
| `quote-style` | "single" | Использовать одинарные кавычки |
| `indent-style` | "space" | Использовать пробелы для отступов |

## Использование

### Основные команды

```bash
# Проверка кода (без исправлений)
ruff check .

# Проверка с автоматическими исправлениями
ruff check --fix .

# Форматирование кода
ruff format .

# Проверка форматирования (без изменений)
ruff format --diff .

# Проверка конкретного файла
ruff check config/settings.py

# Подробный вывод
ruff check --verbose .
```

### Проверка конкретных правил

```bash
# Показать только ошибки импортов
ruff check --select I .

# Игнорировать конкретное правило
ruff check --ignore E501 .

# Показать статистику по правилам
ruff check --statistics .
```

## Интеграция с редакторами

### VS Code

Файл `.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,

    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "explicit",
            "source.fixAll.ruff": "explicit"
        },
        "editor.rulers": [79]
    },

    "ruff.enable": true,
    "ruff.organizeImports": true,
    "ruff.fixAll": true
}
```

### PyCharm

1. Установите плагин "Ruff"
2. File → Settings → Tools → Ruff
3. Укажите путь к исполняемому файлу ruff
4. Включите "Enable Ruff"

## Git Hooks

### Установка хуков

```bash
# Запустить скрипт установки
./scripts/setup-hooks.sh
```

### Ручная установка pre-commit хука

Создайте файл `.git/hooks/pre-commit`:

```bash
#!/bin/bash
set -e

echo "🔍 Running pre-commit checks..."

# Получить список измененных Python файлов
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -z "$STAGED_FILES" ]; then
    echo "No Python files to check."
    exit 0
fi

# Проверка линтинга
if ! ruff check $STAGED_FILES; then
    echo "❌ Ruff linting failed!"
    exit 1
fi

# Проверка форматирования
if ! ruff format --diff $STAGED_FILES | grep -q "^$"; then
    echo "❌ Code formatting issues found!"
    exit 1
fi

echo "✅ Pre-commit checks passed!"
```

```bash
chmod +x .git/hooks/pre-commit
```

## Команды Make

### Доступные команды

```bash
# Показать справку
make help

# Проверка кода
make lint

# Проверка с исправлениями
make lint-fix

# Форматирование
make format

# Проверка форматирования
make format-check

# Полная проверка
make check
```

### Примеры использования

```bash
# Ежедневная работа
make lint-fix && make format

# Перед коммитом
make check

# Быстрая проверка
make lint
```

## Скрипты

### Скрипт линтинга `./scripts/lint.sh`

```bash
# Показать справку
./scripts/lint.sh --help

# Только проверка
./scripts/lint.sh

# Исправить проблемы
./scripts/lint.sh --fix

# Форматировать код
./scripts/lint.sh --format

# Комбинированная команда
./scripts/lint.sh --fix --format

# Подробный вывод
./scripts/lint.sh --verbose
```

## Troubleshooting

### Частые проблемы и решения

#### 1. Ошибка "ruff: command not found"

```bash
# Проверить установку
which ruff

# Переустановить
pip install --upgrade ruff

# Или установить в виртуальное окружение
source venv/bin/activate
pip install ruff
```

#### 2. Конфликт кавычек

Если Ruff меняет одинарные кавычки на двойные:

```toml
# В ruff.toml
[lint.flake8-quotes]
inline-quotes = "single"
```

#### 3. Длинные строки

Если строки слишком длинные:

```python
# Плохо
some_very_long_variable_name = some_very_long_function_name(parameter1, parameter2, parameter3)

# Хорошо
some_very_long_variable_name = some_very_long_function_name(
    parameter1,
    parameter2,
    parameter3
)
```

#### 4. Проблемы с импортами

```python
# Плохо
import os
import sys
from django.conf import settings
import requests

# Хорошо (автоматически исправляется)
import os
import sys

import requests
from django.conf import settings
```

#### 5. Игнорирование правил для конкретных строк

```python
# Игнорировать для одной строки
some_code_that_violates_rule()  # noqa: E501

# Игнорировать конкретное правило
some_code()  # ruff: noqa: F401

# Игнорировать все правила для строки
some_code()  # noqa
```

#### 6. Проблемы с миграциями Django

Миграции автоматически исключены из проверки:

```toml
# В ruff.toml
[lint.per-file-ignores]
"**/migrations/*.py" = ["E501", "F401", "F811"]
```

### Полезные команды для отладки

```bash
# Показать версию
ruff --version

# Показать конфигурацию
ruff check --show-settings

# Показать все доступные правила
ruff linter

# Объяснить конкретное правило
ruff rule E501

# Показать статистику нарушений
ruff check --statistics --format=github .
```

### Производительность

Ruff очень быстрый, но для больших проектов:

```bash
# Проверить только измененные файлы
git diff --name-only | grep '\.py$' | xargs ruff check

# Использовать кеш (включен по умолчанию)
# Кеш находится в .ruff_cache/

# Очистить кеш при проблемах
rm -rf .ruff_cache/
```

## Заключение

Ruff предоставляет мощные возможности для поддержания качества кода в Django проекте. Основные преимущества:

- ⚡ **Скорость**: в 10-100 раз быстрее традиционных инструментов
- 🔧 **Автоматические исправления**: большинство проблем исправляются автоматически
- 🎯 **Специализация**: встроенная поддержка Django
- 🛠️ **Интеграция**: легко интегрируется с IDE и CI/CD
- 📝 **Конфигурируемость**: гибкие настройки под проект

Регулярное использование этих инструментов поможет поддерживать код в отличном состоянии!
