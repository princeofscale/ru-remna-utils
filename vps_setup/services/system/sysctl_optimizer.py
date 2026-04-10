from pathlib import Path

from ...config import config
from ...core.base_service import BaseService
from ...core.executor import Executor

_SYSCTL_CONF = Path("/etc/sysctl.d/99-vps-setup.conf")

_BASE_PARAMS: dict[str, str] = {
    "net.core.default_qdisc": "fq",
    "net.ipv4.tcp_congestion_control": "bbr",
    "net.core.somaxconn": "65535",
    "net.ipv4.tcp_max_syn_backlog": "8192",
    "net.ipv4.tcp_tw_reuse": "1",
    "net.ipv4.tcp_fin_timeout": "15",
    "vm.swappiness": "10",
    "fs.file-max": "1000000",
}


class SysctlOptimizerService(BaseService):
    name = "sysctl"
    description = "Sysctl Optimizer — оптимизация ядра Linux для VPN"

    def __init__(self, executor: Executor) -> None:
        super().__init__(executor)
        self._params = {**_BASE_PARAMS, **config.sysctl_extra}

    def status(self) -> str:
        try:
            result = self._read(["sysctl", "net.ipv4.tcp_congestion_control"])
            if result.returncode == 0 and "bbr" in result.stdout:
                return "✅ BBR активен + sysctl оптимизирован"
            return "⚠️ BBR не активен"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def install(self) -> str:
        return "ℹ️ Sysctl встроен в ядро Linux"

    def is_configured(self) -> bool:
        if not _SYSCTL_CONF.exists():
            return False
        content = _SYSCTL_CONF.read_text()
        return all(f"{k} = {v}" in content for k, v in self._params.items())

    def apply(self) -> str:
        if self.is_configured() and not self.executor.dry_run:
            return "✅ Sysctl уже оптимизирован"
        try:
            conf_content = "\n".join(f"{k} = {v}" for k, v in self._params.items()) + "\n"
            self.executor.write_file(
                str(_SYSCTL_CONF),
                conf_content,
                description=f"записать {_SYSCTL_CONF}",
            )
            for key, val in self._params.items():
                self.run_command(
                    ["sysctl", "-w", f"{key}={val}"],
                    description=f"sysctl -w {key}={val}",
                    check=False,
                )
            self.run_command(
                ["sysctl", "--system"],
                description="sysctl --system",
                check=False,
            )
            return "✅ Sysctl оптимизирован (BBR, TCP tuning, file limits)"
        except Exception as e:
            return f"❌ Ошибка настройки sysctl: {e}"
