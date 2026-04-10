# RU Remna Utils

> Коллекция утилит для панели Remnawave, помогающих администраторам VPN-сервисов ускорить процесс работы.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## Доступные утилиты

### [yacloud-ip-roller](./yacloud-ip-roller/)

**Автоматическая ротация IP-адресов виртуальных машин в Yandex Cloud**

Утилита для ротации публичных IP-адресов до попадания в вайтлист russia-mobile-internet-whitelist с поддержкой параллельной обработки нескольких инстансов.

**Возможности:**
- Кросс-платформенная поддержка (Windows, macOS, Linux)
- Параллельная обработка нескольких VM одновременно
- Фильтрация по префиксу IP-адреса
- Настраиваемая маска подсети (/16-/24)
- Полная документация на русском языке

**Быстрый старт:**
```bash
cd yacloud-ip-roller
python3 roll_ip.py --instance-id <VM_ID>
```

Подробная документация: [yacloud-ip-roller/README.md](./yacloud-ip-roller/README.md)

### [vps-setup](./vps_setup/)

**Настройка и оптимизация Linux-серверов под VPN**

Автоматизирует установку и настройку критически важных сервисов для VPN-серверов на базе Debian/Ubuntu.

**Возможности:**
- UFW — настройка файрвола с правилами для VPN-портов
- BBR — включение TCP BBR для оптимизации производительности сети
- Docker — установка Docker и Docker Compose
- Fail2Ban — защита от брутфорс-атак
- TrafficGuard — мониторинг сетевого трафика
- uv — установка менеджера пакетов Python

**Быстрый старт:**

```bash
# Установка
pip install -e .

# Настроить всё автоматически
sudo vps-setup setup-all

# Проверить статус
sudo vps-setup status --all
```

Подробная документация: [vps-setup/README.md](./vps_setup/README.md)

---

## Требования

- **Python:** 3.10 или выше
- **Платформы:** Windows, macOS, Linux

---

## Вклад в проект

Мы приветствуем вклад в проект! Если вы хотите добавить новую утилиту или улучшить существующую:

### Процесс контрибуции

1. **Обсудите идею** — создайте issue с описанием вашей идеи
2. **Форкните репозиторий** — сделайте fork и клонируйте его локально
3. **Создайте ветку** — `git checkout -b feature/your-feature-name`
4. **Разработайте** — внесите изменения, следуя стандартам кода
5. **Протестируйте** — убедитесь, что код работает корректно
6. **Отправьте PR** — создайте pull request с описанием изменений

### Стандарты качества кода

Проект использует современный стек инструментов для Python:

- **[Ruff](https://github.com/astral-sh/ruff)** — быстрый линтер и форматтер
- **[pre-commit](https://pre-commit.com/)** — автоматическая проверка перед коммитом
- **[mypy](https://mypy-lang.org/)** — проверка типов
- **GitHub Actions** — автоматическая проверка в CI/CD

**Установка инструментов разработки:**
```bash
pip install ruff pre-commit mypy
pre-commit install
```

**Проверка кода перед коммитом:**
```bash
ruff check .
ruff format .
mypy yacloud-ip-roller/roll_ip.py --ignore-missing-imports
```

### Требования к новым утилитам

- Python 3.10+ обязательно
- Кросс-платформенность (Windows/macOS/Linux) где возможно
- Документация на русском языке
- Соответствие стандартам кода (Ruff, mypy)
- Тесты для основных функций

---

## Поддержка

Если у вас возникли вопросы или проблемы:

- **Сайт поддержки:** [https://rknfuck.space/](https://rknfuck.space/)
- **Telegram:** [@tieruser](https://t.me/tieruser)
- **Issues:** [GitHub Issues](https://github.com/princeofscale/ru-remna-utils/issues)

---

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](./LICENSE).
