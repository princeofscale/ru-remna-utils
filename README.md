# ru-remna-utils

> Утилиты для автоматизации настройки VPN-серверов — Remnawave, WireGuard, Xray и других.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## Утилиты

### [yacloud-ip-roller](./yacloud-ip-roller/)

**Автоматическая смена публичного IP на Yandex Cloud**

Крутит IP-адреса виртуальных машин до попадания в вайтлист `russia-mobile-internet-whitelist`. Поддерживает параллельную обработку нескольких инстансов и несколько префиксов IP.

Возможности:

- Параллельная обработка нескольких VM
- Фильтрация по нескольким IP-префиксам (`--prefix 51.250 158.160`)
- Кросс-платформенная поддержка (Windows, macOS, Linux)
- Ошибки API не тратят счётчик попыток

```bash
python3 yacloud-ip-roller/roll_ip.py --instance-id <VM_ID>

# несколько инстансов с фильтром по префиксу
python3 yacloud-ip-roller/roll_ip.py \
  --instance-id <ID1> <ID2> \
  --prefix 51.250 158.160 \
  --attempts 2000
```

---

### [vps-setup](./vps_setup/)

**Настройка Linux-сервера под VPN одной командой**

CLI-утилита для автоматизации настройки Debian/Ubuntu серверов. Устанавливает и конфигурирует всё необходимое для работы VPN-панелей.

### Сервисы

| Сервис | Что делает |
| -------- | ---------- |
| `swap` | Создаёт swap-файл (2 ГБ по умолчанию) |
| `sysctl` | BBR + оптимизация TCP/сети |
| `ssh` | Hardening SSH: отключение паролей, ограничение попыток |
| `ufw` | Файрвол с правилами для VPN-портов |
| `fail2ban` | Защита от брутфорс-атак |
| `docker` | Docker + Docker Compose |
| `autoupdate` | Автоматические security-обновления |
| `traffic` | Инструменты мониторинга (vnstat, iftop, nethogs) |
| `uv` | Быстрый менеджер пакетов Python |

```bash
pip install -e .

# настроить всё
sudo vps-setup setup-all

# посмотреть план без выполнения
sudo vps-setup setup-all --dry-run

# статус
sudo vps-setup status --all

# конкретный сервис
sudo vps-setup apply ufw
```

**Конфигурация** через `~/.config/vps-setup/config.toml` (опционально):

```toml
[general]
ssh_port = 2222
swap_size_gb = 4
timezone = "Europe/Moscow"
vpn_ports = [443, 51820, 80]
```

---

## Требования

- Python 3.10+
- Debian 11+ / Ubuntu 20.04+ (для vps-setup)
- Yandex Cloud CLI установлен (для yacloud-ip-roller)

---

## Контрибуция

1. Создайте issue с описанием идеи
2. Форкните репозиторий
3. Создайте ветку: `git checkout -b feature/название`
4. Внесите изменения, проверьте через `ruff check .`
5. Откройте PR

**Инструменты разработки:**

```bash
pip install ruff pre-commit
pre-commit install
ruff check .
ruff format .
```

---

## Участники

- [@princeofscale](https://github.com/princeofscale) — автор
- [@ixycu](https://github.com/ixycu) — поддержка нескольких `--prefix`

---

## Поддержка

- **Сайт:** [rknfuck.space](https://rknfuck.space/)
- **Telegram:** [@tieruser](https://t.me/tieruser)
- **Issues:** [GitHub Issues](https://github.com/princeofscale/ru-remna-utils/issues)

---

## Лицензия

MIT — подробности в [LICENSE](./LICENSE).
