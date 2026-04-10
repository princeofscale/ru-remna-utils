from ...config import config
from ...core.base_service import BaseService
from ...core.package_manager import PackageManager


class UFWService(BaseService):
    name = "ufw"
    description = "UFW — настройка файрвола для VPN"

    def status(self) -> str:
        result = self._read(["ufw", "status"])
        if result.returncode != 0:
            return "❌ UFW не установлен"
        text = result.stdout.strip()
        if "Status: active" in text or "Состояние: активен" in text:
            return "✅ UFW активен"
        return "⚠️ UFW установлен, но не активен"

    def install(self) -> str:
        try:
            pm = PackageManager(self.executor)
            pm.update()
            pm.install(["ufw"])
            return "✅ UFW установлен"
        except Exception as e:
            return f"❌ Ошибка установки UFW: {e}"

    def is_configured(self) -> bool:
        result = self._read(["ufw", "status"])
        return result.returncode == 0 and (
            "Status: active" in result.stdout or "Состояние: активен" in result.stdout
        )

    def apply(self) -> str:
        if self.is_configured() and not self.executor.dry_run:
            return "✅ UFW уже активен"
        try:
            if not self._is_pkg_installed():
                install_result = self.install()
                if "❌" in install_result:
                    return install_result

            self.run_command(
                ["ufw", "allow", str(config.ssh_port)],
                description=f"ufw allow {config.ssh_port} (SSH)",
            )
            for port in config.vpn_ports:
                self.run_command(
                    ["ufw", "allow", str(port)],
                    description=f"ufw allow {port}",
                )
            self.run_command(
                ["ufw", "default", "deny", "incoming"],
                description="ufw default deny incoming",
            )
            self.run_command(
                ["ufw", "default", "allow", "outgoing"],
                description="ufw default allow outgoing",
            )
            self.run_command(
                ["ufw", "--force", "enable"],
                description="ufw --force enable",
            )
            ports = ", ".join(map(str, [config.ssh_port, *config.vpn_ports]))
            return f"✅ UFW настроен (разрешены порты: {ports})"
        except Exception as e:
            return f"❌ Ошибка настройки UFW: {e}"

    def _is_pkg_installed(self) -> bool:
        return PackageManager(self.executor).is_installed("ufw")

    def reset(self) -> str:
        try:
            self.run_command(["ufw", "--force", "reset"], description="ufw reset")
            return "✅ Правила UFW сброшены"
        except Exception as e:
            return f"❌ Ошибка сброса UFW: {e}"
