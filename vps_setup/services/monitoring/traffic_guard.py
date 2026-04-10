from ...core.base_service import BaseService
from ...core.package_manager import PackageManager


class TrafficGuardService(BaseService):
    name = "trafficguard"
    description = "TrafficGuard — мониторинг сетевого трафика"

    def status(self) -> str:
        pm = PackageManager(self.executor)
        if not pm.is_installed("vnstat"):
            return "❌ vnstat не установлен"
        result = self._read(["systemctl", "is-active", "vnstat"])
        if result.returncode == 0 and "active" in result.stdout:
            return "✅ Мониторинг трафика активен (vnstat)"
        return "⚠️ vnstat установлен, но сервис не запущен"

    def install(self) -> str:
        try:
            pm = PackageManager(self.executor)
            pm.update()
            pm.install(["iftop", "nethogs", "vnstat", "tcpdump"])
            self.run_command(
                ["systemctl", "enable", "vnstat"],
                description="systemctl enable vnstat",
            )
            self.run_command(
                ["systemctl", "start", "vnstat"],
                description="systemctl start vnstat",
            )
            return "✅ Инструменты мониторинга установлены"
        except Exception as e:
            return f"❌ Ошибка установки: {e}"

    def is_configured(self) -> bool:
        pm = PackageManager(self.executor)
        return pm.is_installed("vnstat")

    def apply(self) -> str:
        try:
            if not self.is_configured():
                return self.install()
            return "✅ Мониторинг трафика настроен"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def get_stats(self) -> str:
        result = self._read(["vnstat", "--short"])
        if result.returncode == 0:
            return result.stdout
        return "❌ Не удалось получить статистику трафика"
