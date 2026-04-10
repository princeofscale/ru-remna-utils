import shutil
from pathlib import Path

from ...config import config
from ...core.base_service import BaseService
from ...core.executor import Executor

_SSHD_CONFIG = Path("/etc/ssh/sshd_config")
_SSHD_BACKUP = Path("/etc/ssh/sshd_config.bak")

_HARDENING_PARAMS = {
    "PasswordAuthentication": "no",
    "PubkeyAuthentication": "yes",
    "PermitRootLogin": "no",
    "MaxAuthTries": "3",
    "LoginGraceTime": "20",
    "X11Forwarding": "no",
    "AllowAgentForwarding": "no",
    "AllowTcpForwarding": "no",
}


class SSHHardeningService(BaseService):
    name = "ssh"
    description = "SSH Hardening — усиление безопасности SSH"

    def __init__(self, executor: Executor) -> None:
        super().__init__(executor)
        self._port = config.ssh_port

    def status(self) -> str:
        result = self._read(["sshd", "-T"], check=False)
        if result.returncode != 0:
            return "⚠️ sshd не найден или не запущен"
        params = dict(
            line.split(None, 1)
            for line in result.stdout.splitlines()
            if " " in line
        )
        port = params.get("port", "?")
        auth = params.get("passwordauthentication", "?")
        root = params.get("permitrootlogin", "?")
        return f"✅ SSH: порт {port}, пароли {'✗' if auth == 'no' else '✓'}, root {'✗' if root == 'no' else '✓'}"

    def install(self) -> str:
        return "ℹ️ SSH встроен в систему"

    def is_configured(self) -> bool:
        if not _SSHD_CONFIG.exists():
            return False
        content = _SSHD_CONFIG.read_text()
        return all(
            f"{k} {v}" in content for k, v in _HARDENING_PARAMS.items()
        )

    def apply(self) -> str:
        try:
            if not _SSHD_CONFIG.exists():
                return "❌ /etc/ssh/sshd_config не найден"

            if not self.executor.dry_run and not _SSHD_BACKUP.exists():
                shutil.copy2(_SSHD_CONFIG, _SSHD_BACKUP)

            content = _SSHD_CONFIG.read_text() if not self.executor.dry_run else ""
            lines = content.splitlines()
            updated: dict[str, bool] = dict.fromkeys(_HARDENING_PARAMS, False)

            new_lines = []
            for line in lines:
                stripped = line.strip()
                matched = False
                for key, val in _HARDENING_PARAMS.items():
                    if stripped.lower().startswith(key.lower()):
                        new_lines.append(f"{key} {val}")
                        updated[key] = True
                        matched = True
                        break
                if not matched:
                    new_lines.append(line)

            for key, val in _HARDENING_PARAMS.items():
                if not updated[key]:
                    new_lines.append(f"{key} {val}")

            if str(self._port) not in content:
                new_lines.append(f"Port {self._port}")

            new_content = "\n".join(new_lines) + "\n"
            self.executor.write_file(
                str(_SSHD_CONFIG),
                new_content,
                description=f"обновить sshd_config (порт {self._port}, отключить пароли)",
            )

            check = self._read(["sshd", "-t", "-f", str(_SSHD_CONFIG)])
            if check.returncode != 0 and not self.executor.dry_run:
                shutil.copy2(_SSHD_BACKUP, _SSHD_CONFIG)
                return f"❌ Ошибка в конфигурации sshd, откат: {check.stderr}"

            self.run_command(
                ["systemctl", "reload", "sshd"],
                description="systemctl reload sshd",
                check=False,
            )

            return f"✅ SSH hardening применён (порт {self._port}, пароли отключены)"
        except Exception as e:
            return f"❌ Ошибка SSH hardening: {e}"
