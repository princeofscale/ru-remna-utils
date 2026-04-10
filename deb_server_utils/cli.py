import sys

import typer
from rich.console import Console
from rich.table import Table

from .config import config
from .core.utils import check_root, setup_logging
from .services import (
    BBRService,
    DockerService,
    Fail2BanService,
    TrafficGuardService,
    UFWService,
    UVService,
)

app = typer.Typer(
    help="Deb Server Utils — настройка и оптимизация Linux-серверов под VPN",
    add_completion=False,
)
console = Console()

SERVICES = {
    "ufw": UFWService(),
    "bbr": BBRService(),
    "docker": DockerService(),
    "fail2ban": Fail2BanService(),
    "traffic": TrafficGuardService(),
    "uv": UVService(),
}


@app.command()
def status(
    all: bool = typer.Option(False, "--all", "-a", help="Показать статус всех сервисов"),
    services: list[str] | None = typer.Argument(None, help="Список сервисов для проверки"),
) -> None:
    """Показать статус сервисов."""
    check_root()

    table = Table(title="Статус сервисов")
    table.add_column("Сервис", style="cyan", no_wrap=True)
    table.add_column("Описание", style="white")
    table.add_column("Статус", style="green")

    services_to_check = SERVICES.keys() if all or not services else services

    for name in services_to_check:
        if name not in SERVICES:
            console.print(f"[red]Неизвестный сервис: {name}[/red]")
            continue
        service = SERVICES[name]
        table.add_row(name.upper(), service.description, service.status())

    console.print(table)


@app.command()
def install(
    service: str = typer.Argument(..., help="Имя сервиса для установки"),
) -> None:
    """Установить сервис."""
    check_root()

    if service not in SERVICES:
        console.print(f"[red]Неизвестный сервис: {service}[/red]")
        console.print(f"Доступные сервисы: {', '.join(SERVICES.keys())}")
        sys.exit(1)

    svc = SERVICES[service]
    console.print(f"[cyan]Установка {service.upper()}...[/cyan]")
    console.print(svc.install())


@app.command()
def apply(
    service: str = typer.Argument(..., help="Имя сервиса для настройки"),
) -> None:
    """Применить настройки сервиса."""
    check_root()

    if service not in SERVICES:
        console.print(f"[red]Неизвестный сервис: {service}[/red]")
        console.print(f"Доступные сервисы: {', '.join(SERVICES.keys())}")
        sys.exit(1)

    svc = SERVICES[service]
    console.print(f"[cyan]Настройка {service.upper()}...[/cyan]")
    console.print(svc.apply())


@app.command()
def setup_all() -> None:
    """Установить и настроить все сервисы для VPN-сервера."""
    check_root()

    console.print("[bold cyan]Настройка VPN-сервера...[/bold cyan]\n")

    for name in ["ufw", "bbr", "docker", "fail2ban", "traffic", "uv"]:
        service = SERVICES[name]
        console.print(f"\n[cyan]→ {name.upper()}: {service.description}[/cyan]")
        console.print(f"  {service.apply()}")

    console.print("\n[bold green]✅ Настройка завершена![/bold green]")
    console.print("\n[yellow]Рекомендации:[/yellow]")
    console.print("  • Перезагрузите сервер для применения всех изменений")
    console.print("  • Проверьте статус: deb-server-utils status --all")
    console.print("  • Настройте VPN-панель (Remnawave/WireGuard/Xray)")


@app.command()
def info() -> None:
    """Показать информацию о доступных сервисах."""
    table = Table(title="Доступные сервисы")
    table.add_column("Сервис", style="cyan", no_wrap=True)
    table.add_column("Описание", style="white")

    for name, service in SERVICES.items():
        table.add_row(name.upper(), service.description)

    console.print(table)
    console.print("\n[yellow]Использование:[/yellow]")
    console.print("  deb-server-utils status --all          # статус всех сервисов")
    console.print("  deb-server-utils apply ufw             # настроить UFW")
    console.print("  deb-server-utils setup-all             # настроить всё")


def main() -> None:
    """Точка входа CLI."""
    setup_logging(config.log_level)
    app()


if __name__ == "__main__":
    main()
