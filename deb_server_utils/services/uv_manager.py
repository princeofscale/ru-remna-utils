from pathlib import Path

from ..core.base_service import BaseService


class UVService(BaseService):
    name = "uv"
    description = "uv — ультра-быстрый менеджер пакетов Python"

    UV_INSTALL_SCRIPT = "https://astral.sh/uv/install.sh"

    def status(self) -> str:
        if not self.is_installed():
            return "❌ uv не установлен"

        try:
            result = self.run_command(["uv", "--version"], check=False)
            if result.returncode == 0:
                return f"✅ uv установлен ({result.stdout.strip()})"
            return "⚠️ uv установлен, но не работает корректно"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def install(self) -> str:
        try:
            self.run_command(["sh", "-c", f"curl -LsSf {self.UV_INSTALL_SCRIPT} | sh"])
            return "✅ uv успешно установлен"
        except Exception as e:
            return f"❌ Ошибка установки uv: {e}"

    def apply(self) -> str:
        try:
            if not self.is_installed():
                install_result = self.install()
                if "❌" in install_result:
                    return install_result
            return "✅ uv готов к использованию"
        except Exception as e:
            return f"❌ Ошибка настройки uv: {e}"

    def update(self) -> str:
        try:
            self.run_command(["uv", "self", "update"])
            return "✅ uv обновлен до последней версии"
        except Exception as e:
            return f"❌ Ошибка обновления uv: {e}"

    def is_installed(self) -> bool:
        try:
            uv_paths = [
                Path.home() / ".cargo" / "bin" / "uv",
                Path("/usr/local/bin/uv"),
                Path("/usr/bin/uv"),
            ]
            if any(p.exists() for p in uv_paths):
                return True
            result = self.run_command(["which", "uv"], check=False)
            return result.returncode == 0
        except Exception:
            return False
