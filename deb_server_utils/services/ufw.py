from ..config import config
from ..core.base_service import BaseService


class UFWService(BaseService):
    name = "ufw"
    description = "Uncomplicated Firewall — настройка файрвола для VPN"

    def status(self) -> str:
        if not self.is_installed():
            return "❌ UFW не установлен"

        try:
            result = self.run_command(["ufw", "status"], check=False)
            if result.returncode == 0:
                status_text = result.stdout.strip()
                if "Status: active" in status_text or "Состояние: активен" in status_text:
                    return "✅ UFW активен"
                return "⚠️ UFW установлен, но не активен"
            return "❌ Ошибка получения статуса UFW"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def install(self) -> str:
        try:
            self.run_command(["apt", "update", "-qq"])
            self.run_command(["apt", "install", "-y", "ufw"])
            return "✅ UFW успешно установлен"
        except Exception as e:
            return f"❌ Ошибка установки UFW: {e}"

    def apply(self) -> str:
        try:
            if not self.is_installed():
                install_result = self.install()
                if "❌" in install_result:
                    return install_result

            self.run_command(["ufw", "allow", str(config.ssh_port)])
            for port in config.vpn_ports:
                self.run_command(["ufw", "allow", str(port)])
            self.run_command(["ufw", "default", "deny", "incoming"])
            self.run_command(["ufw", "default", "allow", "outgoing"])
            self.run_command(["ufw", "--force", "enable"])

            return f"✅ UFW настроен и активирован (разрешены порты: {', '.join(map(str, [config.ssh_port, *config.vpn_ports]))})"
        except Exception as e:
            return f"❌ Ошибка настройки UFW: {e}"

    def reset(self) -> str:
        try:
            self.run_command(["ufw", "--force", "reset"])
            return "✅ Правила UFW сброшены"
        except Exception as e:
            return f"❌ Ошибка сброса UFW: {e}"
