import subprocess

from .executor import Executor


class PackageManager:
    def __init__(self, executor: Executor) -> None:
        self.executor = executor

    def is_installed(self, package: str) -> bool:
        result = subprocess.run(
            ["dpkg-query", "--status", package],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0 and "Status: install ok installed" in result.stdout

    def install(self, packages: list[str]) -> None:
        missing = [p for p in packages if not self.is_installed(p)]
        if not missing:
            return
        self.executor.run(
            ["apt", "install", "-y", *missing],
            description=f"apt install {' '.join(missing)}",
        )

    def update(self) -> None:
        self.executor.run(["apt", "update", "-qq"], description="apt update")
