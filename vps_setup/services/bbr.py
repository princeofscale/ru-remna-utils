from pathlib import Path

from ..core.base_service import BaseService


class BBRService(BaseService):
    name = "bbr"
    description = "TCP BBR — оптимизация производительности сети"

    SYSCTL_CONF = Path("/etc/sysctl.conf")

    def status(self) -> str:
        try:
            result = self.run_command(
                ["sysctl", "net.ipv4.tcp_congestion_control"], check=False
            )
            if result.returncode == 0 and "bbr" in result.stdout:
                return "✅ BBR активен"
            return "⚠️ BBR не активен"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def install(self) -> str:
        return "ℹ️ BBR встроен в ядро Linux (требуется kernel 4.9+)"

    def apply(self) -> str:
        try:
            bbr_params = [
                "net.core.default_qdisc=fq",
                "net.ipv4.tcp_congestion_control=bbr",
            ]

            for param in bbr_params:
                self.run_command(["sysctl", "-w", param])

            if self.SYSCTL_CONF.exists():
                content = self.SYSCTL_CONF.read_text()
                lines = [
                    line
                    for line in content.splitlines()
                    if not any(p.split("=")[0] in line for p in bbr_params)
                ]
                lines.extend(bbr_params)
                self.SYSCTL_CONF.write_text("\n".join(lines) + "\n")
            else:
                self.SYSCTL_CONF.write_text("\n".join(bbr_params) + "\n")

            return "✅ BBR активирован и настроен для автозапуска"
        except Exception as e:
            return f"❌ Ошибка настройки BBR: {e}"

    def check_kernel_version(self) -> str:
        try:
            result = self.run_command(["uname", "-r"])
            kernel_version = result.stdout.strip()
            version_parts = kernel_version.split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1].split("-")[0])

            if major > 4 or (major == 4 and minor >= 9):
                return f"✅ Ядро {kernel_version} поддерживает BBR"
            return f"⚠️ Ядро {kernel_version} может не поддерживать BBR (требуется 4.9+)"
        except Exception as e:
            return f"❌ Ошибка проверки версии ядра: {e}"
