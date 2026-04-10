import logging
import os
import sys
from pathlib import Path


def check_root() -> None:
    try:
        status_file = Path("/proc/self/status")
        if status_file.exists():
            is_root = "Uid:\t0" in status_file.read_text()
        else:
            is_root = os.geteuid() == 0

        if not is_root:
            print("❌ Ошибка: требуются права root (sudo)", file=sys.stderr)
            print("Запустите: sudo python3 -m deb_server_utils.cli", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка проверки прав: {e}", file=sys.stderr)
        sys.exit(1)


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
