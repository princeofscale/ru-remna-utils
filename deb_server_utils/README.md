# Deb Server Utils

**Утилита для настройки и оптимизации Linux-серверов под VPN**

Автоматизирует установку и настройку критически важных сервисов для VPN-серверов на базе Debian/Ubuntu.

## Возможности

- **UFW** — настройка файрвола с правилами для VPN-портов
- **BBR** — включение TCP BBR для оптимизации производительности сети
- **Docker** — установка Docker и Docker Compose
- **Fail2Ban** — защита от брутфорс-атак
- **TrafficGuard** — мониторинг сетевого трафика
- **uv** — установка современного менеджера пакетов Python

## Требования

- **ОС:** Debian 11+, Ubuntu 20.04+
- **Python:** 3.10+
- **Права:** root (sudo)

## Установка

```bash
cd ru-remna-utils
pip install -e .
```

## Использование

### Быстрый старт (настроить всё)

```bash
sudo deb-server-utils setup-all
```

Эта команда установит и настроит все сервисы автоматически.

### Статус сервисов

```bash
# Все сервисы
sudo deb-server-utils status --all

# Конкретные сервисы
sudo deb-server-utils status ufw bbr docker
```

### Установка отдельного сервиса

```bash
sudo deb-server-utils install ufw
```

### Настройка отдельного сервиса

```bash
sudo deb-server-utils apply ufw
```

### Информация о сервисах

```bash
deb-server-utils info
```

## Описание сервисов

### UFW (Uncomplicated Firewall)

Настраивает файрвол с безопасными правилами по умолчанию:
- Разрешает SSH (порт 22)
- Разрешает VPN-порты (443, 51820, 80)
- Блокирует все остальные входящие соединения
- Разрешает все исходящие соединения

```bash
sudo deb-server-utils apply ufw
```

### BBR (Bottleneck Bandwidth and RTT)

Включает современный алгоритм TCP congestion control для улучшения производительности сети:
- Оптимизирует пропускную способность
- Снижает задержки
- Улучшает работу VPN-соединений

```bash
sudo deb-server-utils apply bbr
```

**Требования:** Linux kernel 4.9+

### Docker

Устанавливает Docker и Docker Compose:
- Официальный репозиторий Docker
- Docker Engine + Docker Compose
- Автозапуск при загрузке системы

```bash
sudo deb-server-utils apply docker
```

### Fail2Ban

Защита от брутфорс-атак:
- Автоматическая блокировка IP после неудачных попыток входа
- Настроенные jail для SSH
- Время бана: 1 час (настраивается)
- Максимум попыток: 5 (настраивается)

```bash
sudo deb-server-utils apply fail2ban
```

### TrafficGuard

Инструменты для мониторинга трафика:
- `iftop` — мониторинг в реальном времени
- `nethogs` — трафик по процессам
- `vnstat` — статистика трафика
- `tcpdump` — анализ пакетов

```bash
sudo deb-server-utils apply traffic
```

### uv

Современный менеджер пакетов Python:
- В 10-100 раз быстрее pip
- Управление виртуальными окружениями
- Совместимость с pip

```bash
sudo deb-server-utils apply uv
```

## Конфигурация

Настройки можно изменить в файле `deb-server-utils/config.py`:

```python
@dataclass
class Config:
    log_level: str = "INFO"
    vpn_ports: list[int] = [443, 51820, 80, 22]  # VPN-порты
    ssh_port: int = 22                            # SSH-порт
    fail2ban_bantime: int = 3600                  # Время бана (секунды)
    fail2ban_maxretry: int = 5                    # Макс. попыток
```

## Примеры использования

### Настройка нового VPN-сервера

```bash
# 1. Установить и настроить всё
sudo deb-server-utils setup-all

# 2. Проверить статус
sudo deb-server-utils status --all

# 3. Перезагрузить сервер
sudo reboot
```

### Настройка только файрвола и BBR

```bash
sudo deb-server-utils apply ufw
sudo deb-server-utils apply bbr
```

### Проверка версии ядра для BBR

```bash
uname -r  # Должно быть >= 4.9
```

## Безопасность

- Все операции требуют root-прав
- UFW настраивается с безопасными правилами по умолчанию
- Fail2Ban защищает от брутфорса
- Рекомендуется изменить SSH-порт после настройки

## Устранение неполадок

### UFW блокирует соединения

Проверьте правила:
```bash
sudo ufw status verbose
```

Добавьте нужный порт:
```bash
sudo ufw allow <порт>
```

### BBR не активируется

Проверьте версию ядра:
```bash
uname -r  # Должно быть >= 4.9
```

Проверьте текущий алгоритм:
```bash
sysctl net.ipv4.tcp_congestion_control
```

### Docker не запускается

Проверьте статус:
```bash
sudo systemctl status docker
```

Проверьте логи:
```bash
sudo journalctl -u docker
```

## Совместимость

Протестировано на:
- Debian 11 (Bullseye)
- Debian 12 (Bookworm)
- Ubuntu 20.04 LTS
- Ubuntu 22.04 LTS
- Ubuntu 24.04 LTS

## Автор
Вдохновился проектом github.com/thegrayfoxxx/deb_scripts автора thegrayfoxxx
В общем то прикольный проект, захотите - зайдите и сами посмотрите

## Лицензия

MIT License — см. [LICENSE](../LICENSE)
