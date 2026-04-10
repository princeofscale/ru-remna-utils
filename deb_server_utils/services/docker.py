from ..core.base_service import BaseService


class DockerService(BaseService):
    name = "docker"
    description = "Docker — контейнеризация приложений"

    def status(self) -> str:
        if not self.is_installed():
            return "❌ Docker не установлен"

        try:
            result = self.run_command(["systemctl", "is-active", "docker"], check=False)
            if result.returncode == 0 and "active" in result.stdout:
                version_result = self.run_command(["docker", "--version"], check=False)
                version = (
                    version_result.stdout.strip()
                    if version_result.returncode == 0
                    else "неизвестна"
                )
                return f"✅ Docker активен ({version})"
            return "⚠️ Docker установлен, но не запущен"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def install(self) -> str:
        try:
            self.run_command(["apt", "update", "-qq"])
            self.run_command(
                ["apt", "install", "-y", "ca-certificates", "curl", "gnupg", "lsb-release"]
            )
            self.run_command(["install", "-m", "0755", "-d", "/etc/apt/keyrings"])
            self.run_command(
                [
                    "sh",
                    "-c",
                    "curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg",
                ]
            )
            self.run_command(["chmod", "a+r", "/etc/apt/keyrings/docker.gpg"])
            self.run_command(
                [
                    "sh",
                    "-c",
                    'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list',
                ]
            )
            self.run_command(["apt", "update", "-qq"])
            self.run_command(
                [
                    "apt",
                    "install",
                    "-y",
                    "docker-ce",
                    "docker-ce-cli",
                    "containerd.io",
                    "docker-buildx-plugin",
                    "docker-compose-plugin",
                ]
            )
            return "✅ Docker успешно установлен"
        except Exception as e:
            return f"❌ Ошибка установки Docker: {e}"

    def apply(self) -> str:
        try:
            if not self.is_installed():
                install_result = self.install()
                if "❌" in install_result:
                    return install_result

            self.run_command(["systemctl", "start", "docker"])
            self.run_command(["systemctl", "enable", "docker"])
            return "✅ Docker запущен и добавлен в автозагрузку"
        except Exception as e:
            return f"❌ Ошибка настройки Docker: {e}"

    def add_user_to_group(self, username: str) -> str:
        try:
            self.run_command(["usermod", "-aG", "docker", username])
            return f"✅ Пользователь {username} добавлен в группу docker (требуется перелогин)"
        except Exception as e:
            return f"❌ Ошибка добавления пользователя в группу: {e}"
