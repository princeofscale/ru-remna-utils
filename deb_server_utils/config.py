from dataclasses import dataclass, field


@dataclass
class Config:
    log_level: str = "INFO"
    vpn_ports: list[int] = field(default_factory=lambda: [443, 51820, 80, 22])
    ssh_port: int = 22
    fail2ban_bantime: int = 3600
    fail2ban_maxretry: int = 5


config = Config()
