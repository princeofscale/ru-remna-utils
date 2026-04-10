# CLAUDE.md

Ты — senior Python разработчик, работающий над популярным open-source репозиторием [ru-remna-utils](https://github.com/princeofscale/ru-remna-utils).

## О проекте

Репозиторий помогает пользователям [Remnawave](https://github.com/remnawave) и других VPN-панелей (3x-ui, Marzban и др.) настраивать выделенные и виртуальные серверы (VPS/дедики) под VPN-инфраструктуру.

Аудитория: системные администраторы, DevOps-инженеры и продвинутые пользователи, которые разворачивают собственные VPN-серверы на Debian/Ubuntu.

## Правила работы

- Весь код без комментариев и docstrings (кроме typer-команд — там docstring нужен для `--help`)
- Язык общения и коммитов — русский
- Коммиты без упоминания автора (Claude, AI и т.д.)
- Python 3.10+, type hints обязательны
- Линтер: Ruff (`pyproject.toml`), форматтер Ruff

## Структура репозитория

```
ru-remna-utils/
├── yacloud-ip-roller/     # Смена публичного IP на Яндекс Облаке
│   └── roll_ip.py
├── deb_server_utils/      # CLI утилита для настройки Debian/Ubuntu под VPN
│   ├── cli.py
│   ├── config.py
│   ├── core/
│   └── services/
└── pyproject.toml
```

## Ведение CHANGELOG (towncrier)

`towncrier` — официально рекомендуемый инструмент Python-сообщества для автоматического ведения `CHANGELOG.md`. Соответствует **Keep a Changelog** + SemVer.

### Установка

```bash
pip install towncrier
```

### Настройка (pyproject.toml)

```toml
[tool.towncrier]
directory = "changelog.d"
filename = "CHANGELOG.md"
start_string = "<!-- towncrier release notes start -->\n"
title_format = "## [{version}] - {project_date}"
issue_format = "[#{issue}](https://github.com/princeofscale/ru-remna-utils/pull/{issue})"

[[tool.towncrier.type]]
name = "Security"

[[tool.towncrier.type]]
name = "Removed"

[[tool.towncrier.type]]
name = "Deprecated"

[[tool.towncrier.type]]
name = "Added"

[[tool.towncrier.type]]
name = "Changed"

[[tool.towncrier.type]]
name = "Fixed"
```

### Начало CHANGELOG.md

```markdown
# Changelog

Все заметные изменения в этом проекте будут документироваться в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/), проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

Изменения для следующей версии находятся в папке `changelog.d/`.

<!-- towncrier release notes start -->
```

### Создание фрагментов

Каждое изменение = один файл в `changelog.d/`. Название файла:

```
123.added.md
456.fixed.md
+orphan.bugfix.md   # если нет PR/issue
```

Содержимое — одна строка на русском:

```markdown
Добавлена поддержка Python 3.13.
```

Создать через терминал:

```bash
towncrier create 123.fixed.md --content "Исправлена ошибка при потере IP через API."
```

### Сборка релиза

```bash
towncrier build --version 2.3.0 --yes
```

Команда собирает все фрагменты из `changelog.d/`, добавляет секцию в `CHANGELOG.md`, удаляет использованные фрагменты.

### Правило

После каждого изменения кода предлагай towncrier-фрагмент. Никогда не редактируй `CHANGELOG.md` вручную.
