from pathlib import Path

from ...config import config
from ...core.base_service import BaseService
from ...core.package_manager import PackageManager

_JAIL_LOCAL = Path("/etc/fail2ban/jail.local")


class Fail2BanService(BaseService):
    name = "fail2ban"
    description = "Fail2Ban — защита от брутфорс-атак"

    def status(self) -> str:
        pm = PackageManager(self.executor)
        if not pm.is_installed("fail2ban"):
            return "❌ Fail2Ban не установлен"
        result = self._read(["systemctl", "is-active", "fail2ban"])
        if result.returncode == 0 and "active" in result.stdout:
            jails = self._read(["fail2ban-client", "status"])
            jail_line = next(
                (line.strip() for line in jails.stdout.splitlines() if "Jail list:" in line), ""
            )
            return f"✅ Fail2Ban активен ({jail_line or 'нет jail'})"
        return "⚠️ Fail2Ban установлен, но не запущен"

    def install(self) -> str:
        try:
            pm = PackageManager(self.executor)
            pm.update()
            pm.install(["fail2ban"])
            return "✅ Fail2Ban установлен"
        except Exception as e:
            return f"❌ Ошибка установки Fail2Ban: {e}"

    def is_configured(self) -> bool:
        return _JAIL_LOCAL.exists()

    def apply(self) -> str:
        try:
            pm = PackageManager(self.executor)
            if not pm.is_installed("fail2ban"):
                install_result = self.install()
                if "❌" in install_result:
                    return install_result

            jail_config = (
                f"[DEFAULT]\n"
                f"bantime = {config.fail2ban_bantime}\n"
                f"findtime = 600\n"
                f"maxretry = {config.fail2ban_maxretry}\n"
                f"destemail = root@localhost\n"
                f"sendername = Fail2Ban\n"
                f"action = %(action_)s\n\n"
                f"[sshd]\n"
                f"enabled = true\n"
                f"port = {config.ssh_port}\n"
                f"logpath = /var/log/auth.log\n"
                f"maxretry = {config.fail2ban_maxretry}\n"
            )
            self.executor.write_file(
                str(_JAIL_LOCAL),
                jail_config,
                description=f"записать jail.local (bantime={config.fail2ban_bantime}s)",
            )
            self.run_command(
                ["systemctl", "start", "fail2ban"],
                description="systemctl start fail2ban",
            )
            self.run_command(
                ["systemctl", "enable", "fail2ban"],
                description="systemctl enable fail2ban",
            )
            return f"✅ Fail2Ban настроен (bantime: {config.fail2ban_bantime}s, maxretry: {config.fail2ban_maxretry})"
        except Exception as e:
            return f"❌ Ошибка настройки Fail2Ban: {e}"

    def get_banned_ips(self) -> str:
        result = self._read(["fail2ban-client", "status", "sshd"])
        if result.returncode == 0:
            return result.stdout
        return "❌ Не удалось получить список заблокированных IP"
