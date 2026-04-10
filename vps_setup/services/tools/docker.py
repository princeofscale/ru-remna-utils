from ...core.base_service import BaseService
from ...core.package_manager import PackageManager


class DockerService(BaseService):
    name = "docker"
    description = "Docker — контейнеризация приложений"

    def status(self) -> str:
        pm = PackageManager(self.executor)
        if not pm.is_installed("docker-ce"):
            return "❌ Docker не установлен"
        result = self._read(["systemctl", "is-active", "docker"])
        if result.returncode == 0 and "active" in result.stdout:
            ver = self._read(["docker", "--version"])
            return f"✅ Docker активен ({ver.stdout.strip()})"
        return "⚠️ Docker установлен, но не запущен"

    def install(self) -> str:
        try:
            pm = PackageManager(self.executor)
            pm.update()
            pm.install(["ca-certificates", "curl", "gnupg", "lsb-release"])
            self.run_command(
                ["install", "-m", "0755", "-d", "/etc/apt/keyrings"],
                description="создать /etc/apt/keyrings",
            )
            self.run_command(
                ["sh", "-c", "curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg"],
                description="добавить GPG ключ Docker",
            )
            self.run_command(
                ["chmod", "a+r", "/etc/apt/keyrings/docker.gpg"],
                description="chmod docker.gpg",
            )
            self.run_command(
                ["sh", "-c", 'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list'],
                description="добавить репозиторий Docker",
            )
            pm.update()
            pm.install(["docker-ce", "docker-ce-cli", "containerd.io", "docker-buildx-plugin", "docker-compose-plugin"])
            return "✅ Docker установлен"
        except Exception as e:
            return f"❌ Ошибка установки Docker: {e}"

    def is_configured(self) -> bool:
        result = self._read(["systemctl", "is-enabled", "docker"])
        return result.returncode == 0 and "enabled" in result.stdout

    def apply(self) -> str:
        try:
            pm = PackageManager(self.executor)
            if not pm.is_installed("docker-ce"):
                install_result = self.install()
                if "❌" in install_result:
                    return install_result

            self.run_command(
                ["systemctl", "start", "docker"],
                description="systemctl start docker",
            )
            self.run_command(
                ["systemctl", "enable", "docker"],
                description="systemctl enable docker",
            )
            return "✅ Docker запущен и добавлен в автозагрузку"
        except Exception as e:
            return f"❌ Ошибка настройки Docker: {e}"

    def add_user_to_group(self, username: str) -> str:
        try:
            self.run_command(
                ["usermod", "-aG", "docker", username],
                description=f"usermod -aG docker {username}",
            )
            return f"✅ {username} добавлен в группу docker (требуется перелогин)"
        except Exception as e:
            return f"❌ Ошибка: {e}"
