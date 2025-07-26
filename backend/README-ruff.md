# Ruff для Django проекта 🚀

Быстрый линтер и форматтер Python кода, настроенный для этого Django проекта.

## Быстрый старт

```bash
# Установка
pip install ruff

# Проверка кода
make lint

# Исправление проблем
make lint-fix

# Форматирование кода
make format

# Полная проверка
make check
```

## Основные настройки

- **Длина строки**: 79 символов
- **Кавычки**: одинарные для строк, двойные для docstring
- **Импорты**: автоматическая сортировка
- **Отступы**: 4 пробела

## Команды Make

| Команда | Описание |
|---------|----------|
| `make lint` | Проверка кода |
| `make lint-fix` | Проверка + автоисправление |
| `make format` | Форматирование кода |
| `make format-check` | Проверка форматирования |
| `make check` | Полная проверка |

## Команды Ruff

```bash
# Основные команды
ruff check .                    # Проверка
ruff check --fix .             # Проверка + исправления
ruff format .                  # Форматирование
ruff format --diff .           # Показать изменения

# Для конкретного файла
ruff check config/settings.py
ruff format recipes/models.py
```

## Скрипты

```bash
# Универсальный скрипт
./scripts/lint.sh --help       # Справка
./scripts/lint.sh              # Проверка
./scripts/lint.sh --fix        # Исправления
./scripts/lint.sh --format     # Форматирование

# Установка Git hooks
./scripts/setup-hooks.sh
```

## VS Code интеграция

Расширение **Ruff** уже настроено в `.vscode/settings.json`:
- Автоматическое форматирование при сохранении
- Автоисправление проблем
- Сортировка импортов

## Git Hooks

После выполнения `./scripts/setup-hooks.sh`:
- **pre-commit**: проверяет код перед коммитом
- **pre-push**: полная проверка перед push
- **commit-msg**: проверяет формат сообщения коммита

## Конфигурация

Настройки в файле `ruff.toml`:
- Исключения для миграций Django
- Настройки для settings.py
- Правила для первых импортов проекта

## Игнорирование правил

```python
# Для одной строки
long_line_code()  # noqa: E501

# Для конкретного правила Ruff
unused_import  # ruff: noqa: F401

# Для всех правил
some_code()  # noqa
```

## Полезные команды

```bash
# Версия
ruff --version

# Объяснение правила
ruff rule E501

# Статистика
ruff check --statistics .

# Показать настройки
ruff check --show-settings
```

## Пример workflow

```bash
# Ежедневная разработка
make lint-fix && make format

# Перед коммитом
make check

# Быстрая проверка одного файла
ruff check recipes/views.py --fix
```

## Решение проблем

**Ошибка установки:**
```bash
pip install --upgrade ruff
```

**Конфликт кавычек:**
- Настройка в `ruff.toml` уже корректная

**Длинные строки:**
- Используйте многострочные конструкции
- Разбивайте на логические части

**Проблемы с импортами:**
- Ruff автоматически сортирует по группам
- Django импорты в секции third-party

---

📚 **Подробная документация**: [docs/ruff-setup.md](docs/ruff-setup.md)

🔧 **Конфигурация**: [ruff.toml](ruff.toml)

⚡ **Скорость**: Ruff в 10-100 раз быстрее традиционных линтеров!
