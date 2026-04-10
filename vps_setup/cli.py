import sys

import typer
from rich.console import Console
from rich.table import Table

from .config import config
from .core.executor import Executor
from .core.utils import check_root, setup_logging
from .services import (
    DockerService,
    Fail2BanService,
    SSHHardeningService,
    SwapService,
    SysctlOptimizerService,
    TrafficGuardService,
    UFWService,
    UnattendedUpgradesService,
    UVService,
)

app = typer.Typer(
    help="vps-setup — настройка и оптимизация Linux-серверов под VPN",
    add_completion=False,
)
console = Console()

SETUP_ORDER = [
    "swap",
    "sysctl",
    "ssh",
    "ufw",
    "fail2ban",
    "docker",
    "autoupdate",
    "traffic",
    "uv",
]


def _make_services(executor: Executor) -> dict:
    return {
        "swap": SwapService(executor),
        "sysctl": SysctlOptimizerService(executor),
        "ssh": SSHHardeningService(executor),
        "ufw": UFWService(executor),
        "fail2ban": Fail2BanService(executor),
        "docker": DockerService(executor),
        "autoupdate": UnattendedUpgradesService(executor),
        "traffic": TrafficGuardService(executor),
        "uv": UVService(executor),
    }


@app.command()
def status(
    all: bool = typer.Option(False, "--all", "-a", help="Показать все сервисы"),
    services: list[str] | None = typer.Argument(None, help="Список сервисов"),
) -> None:
    """Показать статус сервисов."""
    check_root()
    executor = Executor(dry_run=False)
    svc_map = _make_services(executor)

    table = Table(title="Статус сервисов")
    table.add_column("Сервис", style="cyan", no_wrap=True)
    table.add_column("Описание", style="white")
    table.add_column("Статус", style="green")

    names = list(svc_map.keys()) if (all or not services) else (services or [])
    for name in names:
        if name not in svc_map:
            console.print(f"[red]Неизвестный сервис: {name}[/red]")
            continue
        svc = svc_map[name]
        table.add_row(name.upper(), svc.description, svc.status())

    console.print(table)


@app.command()
def install(
    service: str = typer.Argument(..., help="Имя сервиса"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Показать план без выполнения"),
) -> None:
    """Установить сервис."""
    check_root()
    executor = Executor(dry_run=dry_run)
    svc_map = _make_services(executor)

    if service not in svc_map:
        console.print(f"[red]Неизвестный сервис: {service}[/red]")
        console.print(f"Доступные: {', '.join(svc_map.keys())}")
        sys.exit(1)

    console.print(f"[cyan]Установка {service.upper()}...[/cyan]")
    console.print(svc_map[service].install())
    if dry_run:
        executor.print_plan()


@app.command()
def apply(
    service: str = typer.Argument(..., help="Имя сервиса"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Показать план без выполнения"),
) -> None:
    """Применить настройки сервиса."""
    check_root()
    executor = Executor(dry_run=dry_run)
    svc_map = _make_services(executor)

    if service not in svc_map:
        console.print(f"[red]Неизвестный сервис: {service}[/red]")
        console.print(f"Доступные: {', '.join(svc_map.keys())}")
        sys.exit(1)

    svc = svc_map[service]
    if dry_run:
        console.print(f"[yellow]Dry-run: {service.upper()}[/yellow]")
    else:
        console.print(f"[cyan]Настройка {service.upper()}...[/cyan]")

    console.print(svc.apply())
    if dry_run:
        executor.print_plan()


@app.command()
def setup_all(
    dry_run: bool = typer.Option(False, "--dry-run", help="Показать план без выполнения"),
) -> None:
    """Установить и настроить все сервисы для VPN-сервера."""
    check_root()
    executor = Executor(dry_run=dry_run)
    svc_map = _make_services(executor)

    if dry_run:
        console.print("[bold yellow]Dry-run: что будет выполнено[/bold yellow]\n")
    else:
        console.print("[bold cyan]Настройка VPN-сервера...[/bold cyan]\n")

    for name in SETUP_ORDER:
        svc = svc_map[name]
        console.print(f"\n[cyan]-> {name.upper()}: {svc.description}[/cyan]")
        console.print(f"  {svc.apply()}")

    if dry_run:
        executor.print_plan()
    else:
        console.print("\n[bold green]Настройка завершена![/bold green]")
        console.print("\n[yellow]Рекомендации:[/yellow]")
        console.print("  * Перезагрузите сервер для применения всех изменений")
        console.print("  * Проверьте статус: vps-setup status --all")
        console.print("  * Настройте VPN-панель (Remnawave/WireGuard/Xray)")


@app.command()
def info() -> None:
    """Показать информацию о доступных сервисах."""
    executor = Executor(dry_run=False)
    svc_map = _make_services(executor)

    table = Table(title="Доступные сервисы")
    table.add_column("Сервис", style="cyan", no_wrap=True)
    table.add_column("Категория", style="yellow")
    table.add_column("Описание", style="white")

    categories = {
        "swap": "system", "sysctl": "system", "ssh": "system", "autoupdate": "system",
        "ufw": "security", "fail2ban": "security",
        "docker": "tools", "uv": "tools",
        "traffic": "monitoring",
    }

    for name, svc in svc_map.items():
        table.add_row(name.upper(), categories.get(name, ""), svc.description)

    console.print(table)
    console.print("\n[yellow]Примеры:[/yellow]")
    console.print("  vps-setup setup-all              # настроить всё")
    console.print("  vps-setup setup-all --dry-run    # посмотреть план")
    console.print("  vps-setup apply ufw              # настроить UFW")
    console.print("  vps-setup status --all           # статус всех сервисов")


def main() -> None:
    """Точка входа CLI."""
    setup_logging(config.log_level)
    app()


if __name__ == "__main__":
    main()
