from pathlib import Path

from ...core.base_service import BaseService
from ...core.package_manager import PackageManager

_AUTO_UPGRADES = Path("/etc/apt/apt.conf.d/20auto-upgrades")
_UNATTENDED_UPGRADES = Path("/etc/apt/apt.conf.d/50unattended-upgrades")

_AUTO_UPGRADES_CONTENT = """\
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
"""

_UNATTENDED_UPGRADES_CONTENT = """\
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};
Unattended-Upgrade::Package-Blacklist {};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
"""


class UnattendedUpgradesService(BaseService):
    name = "unattended-upgrades"
    description = "Auto-Updates — автоматические security-обновления"

    def status(self) -> str:
        pkg_check = self._read(["dpkg-query", "--status", "unattended-upgrades"])
        if pkg_check.returncode != 0 or "Status: install ok installed" not in pkg_check.stdout:
            return "❌ unattended-upgrades не установлен"
        if _AUTO_UPGRADES.exists():
            return "✅ Автообновления активны"
        return "⚠️ Пакет установлен, но не настроен"

    def install(self) -> str:
        try:
            pm = PackageManager(self.executor)
            pm.update()
            pm.install(["unattended-upgrades"])
            return "✅ unattended-upgrades установлен"
        except Exception as e:
            return f"❌ Ошибка установки: {e}"

    def is_configured(self) -> bool:
        return _AUTO_UPGRADES.exists() and _UNATTENDED_UPGRADES.exists()

    def apply(self) -> str:
        if self.is_configured() and not self.executor.dry_run:
            return "✅ Автообновления уже настроены"
        try:
            install_result = self.install()
            if "❌" in install_result:
                return install_result

            self.executor.write_file(
                str(_AUTO_UPGRADES),
                _AUTO_UPGRADES_CONTENT,
                description="настроить /etc/apt/apt.conf.d/20auto-upgrades",
            )
            self.executor.write_file(
                str(_UNATTENDED_UPGRADES),
                _UNATTENDED_UPGRADES_CONTENT,
                description="настроить /etc/apt/apt.conf.d/50unattended-upgrades",
            )
            return "✅ Автоматические security-обновления настроены"
        except Exception as e:
            return f"❌ Ошибка настройки автообновлений: {e}"
