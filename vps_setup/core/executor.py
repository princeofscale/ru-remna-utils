import subprocess

from rich.console import Console

_console = Console()


class Executor:
    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self._plan: list[str] = []

    def run(
        self,
        cmd: list[str],
        description: str = "",
        check: bool = True,
        capture: bool = True,
    ) -> subprocess.CompletedProcess:
        if self.dry_run:
            label = description or " ".join(cmd)
            self._plan.append(label)
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")

        kwargs: dict = {"check": check}
        if capture:
            kwargs["capture_output"] = True
            kwargs["text"] = True
        return subprocess.run(cmd, **kwargs)

    def write_file(self, path: str, content: str, description: str = "") -> None:
        if self.dry_run:
            self._plan.append(description or f"write {path}")
            return
        from pathlib import Path

        Path(path).write_text(content)

    def print_plan(self) -> None:
        if not self._plan:
            _console.print("[yellow]Нет запланированных изменений[/yellow]")
            return
        _console.print("\n[bold yellow]Что будет выполнено:[/bold yellow]")
        for action in self._plan:
            _console.print(f"  [cyan]→[/cyan] {action}")
