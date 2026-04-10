from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

_CONFIG_PATH = Path("~/.config/vps-setup/config.toml").expanduser()


@dataclass
class Config:
    log_level: str = "INFO"
    ssh_port: int = 22
    vpn_ports: list[int] = field(default_factory=lambda: [443, 51820, 80])
    fail2ban_bantime: int = 3600
    fail2ban_maxretry: int = 5
    swap_size_gb: int = 2
    timezone: str = "Europe/Moscow"
    hostname: str = ""
    sysctl_extra: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls) -> Config:
        if tomllib is None or not _CONFIG_PATH.exists():
            return cls()
        with open(_CONFIG_PATH, "rb") as f:
            data = tomllib.load(f)
        general = data.get("general", {})
        known = {k: v for k, v in general.items() if k in cls.__dataclass_fields__}
        return cls(**known)


config = Config.load()
