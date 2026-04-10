from pathlib import Path

from ...core.base_service import BaseService

_UV_INSTALL_SCRIPT = "https://astral.sh/uv/install.sh"

_UV_PATHS = [
    Path.home() / ".cargo" / "bin" / "uv",
    Path("/usr/local/bin/uv"),
    Path("/usr/bin/uv"),
    Path.home() / ".local" / "bin" / "uv",
]


class UVService(BaseService):
    name = "uv"
    description = "uv — ультра-быстрый менеджер пакетов Python"

    def status(self) -> str:
        if not self._uv_installed():
            return "❌ uv не установлен"
        result = self._read(["uv", "--version"])
        if result.returncode == 0:
            return f"✅ uv установлен ({result.stdout.strip()})"
        return "⚠️ uv установлен, но не работает корректно"

    def install(self) -> str:
        try:
            self.run_command(
                ["sh", "-c", f"curl -LsSf {_UV_INSTALL_SCRIPT} | sh"],
                description="установить uv через astral.sh",
            )
            return "✅ uv установлен"
        except Exception as e:
            return f"❌ Ошибка установки uv: {e}"

    def is_configured(self) -> bool:
        return self._uv_installed()

    def apply(self) -> str:
        try:
            if not self._uv_installed():
                install_result = self.install()
                if "❌" in install_result:
                    return install_result
            return "✅ uv готов к использованию"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def update(self) -> str:
        try:
            self.run_command(["uv", "self", "update"], description="uv self update")
            return "✅ uv обновлён"
        except Exception as e:
            return f"❌ Ошибка обновления uv: {e}"

    def _uv_installed(self) -> bool:
        if any(p.exists() for p in _UV_PATHS):
            return True
        result = self._read(["which", "uv"])
        return result.returncode == 0
