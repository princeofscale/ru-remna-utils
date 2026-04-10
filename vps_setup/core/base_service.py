import logging
import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path


class BaseService(ABC):
    name: str
    description: str

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def run_command(
        self, cmd: list[str], check: bool = True, capture: bool = True
    ) -> subprocess.CompletedProcess:
        if not self.is_root():
            raise PermissionError("Требуются права root (sudo)")

        kwargs: dict = {"check": check}
        if capture:
            kwargs["capture_output"] = True
            kwargs["text"] = True

        return subprocess.run(cmd, **kwargs)

    @staticmethod
    def is_root() -> bool:
        try:
            status_file = Path("/proc/self/status")
            if status_file.exists():
                return "Uid:\t0" in status_file.read_text()
            return os.geteuid() == 0
        except Exception:
            return False

    @abstractmethod
    def status(self) -> str: ...

    @abstractmethod
    def install(self) -> str: ...

    @abstractmethod
    def apply(self) -> str: ...

    def is_installed(self) -> bool:
        try:
            result = subprocess.run(
                ["which", self.name.lower()],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False
