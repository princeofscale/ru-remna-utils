from pathlib import Path

from ...config import config
from ...core.base_service import BaseService
from ...core.executor import Executor

_SWAP_FILE = Path("/swapfile")
_FSTAB = Path("/etc/fstab")


class SwapService(BaseService):
    name = "swap"
    description = "Swap — виртуальная память"

    def __init__(self, executor: Executor) -> None:
        super().__init__(executor)
        self._size_gb = config.swap_size_gb

    def status(self) -> str:
        result = self._read(["swapon", "--show", "--noheadings"])
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().splitlines()
            return f"✅ Swap активен ({len(lines)} раздел(а))"
        return "⚠️ Swap не активен"

    def install(self) -> str:
        return "ℹ️ Swap создаётся через apply"

    def is_configured(self) -> bool:
        return _SWAP_FILE.exists() and "/swapfile" in (_FSTAB.read_text() if _FSTAB.exists() else "")

    def apply(self) -> str:
        if self.is_configured() and not self.executor.dry_run:
            return f"✅ Swap уже настроен ({_SWAP_FILE})"
        try:
            size_mb = self._size_gb * 1024
            self.run_command(
                ["fallocate", "-l", f"{size_mb}M", str(_SWAP_FILE)],
                description=f"создать swap-файл {self._size_gb}GB",
            )
            self.run_command(
                ["chmod", "600", str(_SWAP_FILE)],
                description="chmod 600 /swapfile",
            )
            self.run_command(
                ["mkswap", str(_SWAP_FILE)],
                description="mkswap /swapfile",
            )
            self.run_command(
                ["swapon", str(_SWAP_FILE)],
                description="swapon /swapfile",
            )

            if not self.executor.dry_run:
                fstab = _FSTAB.read_text() if _FSTAB.exists() else ""
                if "/swapfile" not in fstab:
                    _FSTAB.write_text(fstab + "/swapfile none swap sw 0 0\n")
            else:
                self.executor._plan.append("добавить /swapfile в /etc/fstab")

            return f"✅ Swap {self._size_gb}GB создан и активирован"
        except Exception as e:
            return f"❌ Ошибка создания swap: {e}"
