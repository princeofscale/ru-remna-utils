from ..core.base_service import BaseService


class TrafficGuardService(BaseService):
    name = "trafficguard"
    description = "TrafficGuard — мониторинг и защита трафика"

    def status(self) -> str:
        try:
            result = self.run_command(["ip", "-s", "link"], check=False)
            if result.returncode == 0:
                return "✅ Мониторинг трафика доступен"
            return "⚠️ Не удалось получить статистику трафика"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def install(self) -> str:
        try:
            self.run_command(["apt", "update", "-qq"])
            self.run_command(
                ["apt", "install", "-y", "iftop", "nethogs", "vnstat", "tcpdump"]
            )
            self.run_command(["systemctl", "enable", "vnstat"])
            self.run_command(["systemctl", "start", "vnstat"])
            return "✅ Инструменты мониторинга трафика установлены"
        except Exception as e:
            return f"❌ Ошибка установки: {e}"

    def apply(self) -> str:
        try:
            if not self.is_installed():
                install_result = self.install()
                if "❌" in install_result:
                    return install_result
            return "✅ Мониторинг трафика настроен"
        except Exception as e:
            return f"❌ Ошибка настройки: {e}"

    def get_traffic_stats(self) -> str:
        try:
            result = self.run_command(["vnstat", "--short"], check=False)
            if result.returncode == 0:
                return result.stdout
            return "❌ Не удалось получить статистику трафика"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def is_installed(self) -> bool:
        try:
            result = self.run_command(["which", "vnstat"], check=False)
            return result.returncode == 0
        except Exception:
            return False
