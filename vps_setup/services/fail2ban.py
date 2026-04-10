from pathlib import Path

from ..config import config
from ..core.base_service import BaseService


class Fail2BanService(BaseService):
    name = "fail2ban"
    description = "Fail2Ban — защита от брутфорс-атак"

    JAIL_LOCAL = Path("/etc/fail2ban/jail.local")

    def status(self) -> str:
        if not self.is_installed():
            return "❌ Fail2Ban не установлен"

        try:
            result = self.run_command(["systemctl", "is-active", "fail2ban"], check=False)
            if result.returncode == 0 and "active" in result.stdout:
                status_result = self.run_command(["fail2ban-client", "status"], check=False)
                if status_result.returncode == 0:
                    jails = [
                        line.strip()
                        for line in status_result.stdout.splitlines()
                        if "Jail list:" in line
                    ]
                    return f"✅ Fail2Ban активен ({jails[0] if jails else 'нет jail'})"
                return "✅ Fail2Ban активен"
            return "⚠️ Fail2Ban установлен, но не запущен"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def install(self) -> str:
        try:
            self.run_command(["apt", "update", "-qq"])
            self.run_command(["apt", "install", "-y", "fail2ban"])
            return "✅ Fail2Ban успешно установлен"
        except Exception as e:
            return f"❌ Ошибка установки Fail2Ban: {e}"

    def apply(self) -> str:
        try:
            if not self.is_installed():
                install_result = self.install()
                if "❌" in install_result:
                    return install_result

            jail_config = f"""[DEFAULT]
bantime = {config.fail2ban_bantime}
findtime = 600
maxretry = {config.fail2ban_maxretry}
destemail = root@localhost
sendername = Fail2Ban
action = %(action_)s

[sshd]
enabled = true
port = {config.ssh_port}
logpath = /var/log/auth.log
maxretry = {config.fail2ban_maxretry}
"""
            self.JAIL_LOCAL.write_text(jail_config)
            self.run_command(["systemctl", "start", "fail2ban"])
            self.run_command(["systemctl", "enable", "fail2ban"])

            return f"✅ Fail2Ban настроен и активирован (bantime: {config.fail2ban_bantime}s, maxretry: {config.fail2ban_maxretry})"
        except Exception as e:
            return f"❌ Ошибка настройки Fail2Ban: {e}"

    def get_banned_ips(self) -> str:
        try:
            result = self.run_command(["fail2ban-client", "status", "sshd"], check=False)
            if result.returncode == 0:
                return result.stdout
            return "❌ Не удалось получить список заблокированных IP"
        except Exception as e:
            return f"❌ Ошибка: {e}"
