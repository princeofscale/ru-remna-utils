#!/usr/bin/env python3

import argparse
import ipaddress
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import urllib.request

CIDR_URL = (
    "https://raw.githubusercontent.com/hxehex/russia-mobile-internet-whitelist"
    "/main/cidrwhitelist.txt"
)

PRINT_LOCK = threading.Lock()


def tprint(*args, **kwargs):
    with PRINT_LOCK:
        print(*args, **kwargs)


def find_yc() -> str:
    if platform.system() == "Windows":
        candidates = [
            os.path.join(os.path.expanduser("~"), "yandex-cloud", "bin", "yc.exe"),
            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "Yandex.Cloud",
                "bin",
                "yc.exe",
            ),
            os.path.join(
                os.environ.get("PROGRAMFILES", ""),
                "Yandex.Cloud",
                "bin",
                "yc.exe",
            ),
            "yc.exe",
            "yc",
        ]
    else:
        candidates = [
            os.path.join(os.path.expanduser("~"), "yandex-cloud", "bin", "yc"),
            "/usr/local/bin/yc",
            "yc",
        ]

    for path in candidates:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
        if os.sep not in path and "/" not in path:
            found = shutil.which(path)
            if found:
                return found

    sys.exit(
        "Ошибка: yc CLI не найден.\n"
        "Установите Yandex Cloud CLI: https://yandex.cloud/ru/docs/cli/quickstart\n"
        "  macOS/Linux: curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash\n"
        "  Windows:     https://storage.yandexcloud.net/yandexcloud-yc/release/latest/windows/amd64/yc.exe"
    )


def fetch_whitelist(min_prefix: int) -> list:
    networks = []
    lines = urllib.request.urlopen(CIDR_URL).read().decode().splitlines()
    skipped = 0
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            net = ipaddress.ip_network(line, strict=False)
            if net.prefixlen >= min_prefix:
                networks.append(net)
            else:
                skipped += 1
        except ValueError:
            pass
    tprint(
        f"  Подсетей /{min_prefix}+: {len(networks)}"
        f"  (пропущено /{min_prefix - 1} и шире: {skipped})",
        flush=True,
    )
    return networks


def is_in_whitelist(ip_str: str, networks: list):
    addr = ipaddress.ip_address(ip_str)
    for net in networks:
        if addr in net:
            return net
    return None


def get_current_ip(yc: str, instance_id: str):
    out = subprocess.check_output(
        [yc, "compute", "instance", "get", "--id", instance_id, "--format", "json"],
        stderr=subprocess.DEVNULL,
    )
    data = json.loads(out)
    for iface in data["network_interfaces"]:
        nat = iface.get("primary_v4_address", {}).get("one_to_one_nat", {})
        if "address" in nat:
            return nat["address"]
    return None


def remove_nat(yc: str, instance_id: str, iface_index: int) -> None:
    subprocess.check_call(
        [
            yc,
            "compute",
            "instance",
            "remove-one-to-one-nat",
            "--id",
            instance_id,
            "--network-interface-index",
            str(iface_index),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def add_nat(yc: str, instance_id: str, iface_index: int) -> None:
    subprocess.check_call(
        [
            yc,
            "compute",
            "instance",
            "add-one-to-one-nat",
            "--id",
            instance_id,
            "--network-interface-index",
            str(iface_index),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def roll_instance(
    yc: str,
    instance_id: str,
    networks: list,
    prefix: str,
    iface: int,
    attempts: int,
    delay: float,
    results: dict,
) -> None:
    short_id = instance_id[:7]
    tag = f"[{short_id}]"
    attempt = 0

    while attempt < attempts:
        ip = None
        for _ in range(5):
            try:
                ip = get_current_ip(yc, instance_id)
                break
            except Exception:
                time.sleep(2)

        if ip is None:
            tprint(f"{tag} [{attempt}/{attempts}] не удаётся получить IP, повтор...", flush=True)
            time.sleep(5)
            continue

        attempt += 1
        label = f"{tag} [{attempt}/{attempts}]"

        if prefix and not ip.startswith(prefix):
            tprint(f"{label} {ip}  —  не тот диапазон", flush=True)
        else:
            match = is_in_whitelist(ip, networks)
            if match:
                tprint(f"\n{tag} ✓ Готово! IP: {ip}  подсеть: {match}", flush=True)
                results[instance_id] = ip
                return
            tprint(f"{label} {ip}  —  не в списке", flush=True)

        try:
            remove_nat(yc, instance_id, iface)
        except Exception as e:
            tprint(f"{label}   ошибка remove-nat: {e}", flush=True)
            time.sleep(3)
            continue

        time.sleep(delay)

        try:
            add_nat(yc, instance_id, iface)
        except Exception as e:
            tprint(f"{label}   ошибка add-nat: {e}", flush=True)
            time.sleep(3)
            continue

        time.sleep(delay + 1)

    tprint(f"\n{tag} Не удалось найти подходящий IP за {attempts} попыток.", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Крутит публичный IP на VPS в Яндекс Облаке, пока он не попадёт в вайтлист.\n"
            "При нескольких --instance-id прокрутка идёт параллельно."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--instance-id",
        required=True,
        nargs="+",
        metavar="ID",
        help="ID виртуальной машины (можно указать несколько через пробел)",
    )
    parser.add_argument(
        "--mask",
        type=int,
        default=16,
        metavar="PREFIX",
        help="Минимальная длина префикса подсети (по умолчанию 16)",
    )
    parser.add_argument(
        "--iface",
        type=int,
        default=0,
        metavar="INDEX",
        help="Индекс сетевого интерфейса VM (по умолчанию 0)",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=500,
        metavar="N",
        help="Максимальное количество попыток на каждый инстанс (по умолчанию 500)",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default=None,
        metavar="IP_PREFIX",
        help="Принимать только IP с этим началом (напр. '51.250')",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        metavar="SEC",
        help="Задержка после remove-nat перед add-nat (по умолчанию 2с)",
    )
    args = parser.parse_args()

    yc = find_yc()
    print(f"yc CLI: {yc}", flush=True)
    print(f"Загрузка вайтлиста (маска /{args.mask})...", flush=True)
    networks = fetch_whitelist(args.mask)
    print(f"Итого: {len(networks)} записей\n", flush=True)

    if args.prefix:
        print(f"Фильтр: только IP начинающиеся с '{args.prefix}'\n", flush=True)

    instance_ids = args.instance_id
    results: dict = {}

    if len(instance_ids) == 1:
        roll_instance(
            yc,
            instance_ids[0],
            networks,
            args.prefix,
            args.iface,
            args.attempts,
            args.delay,
            results,
        )
    else:
        print(
            f"Запускаем параллельный прокрут для {len(instance_ids)} инстансов...\n",
            flush=True,
        )
        threads = [
            threading.Thread(
                target=roll_instance,
                args=(
                    yc,
                    iid,
                    networks,
                    args.prefix,
                    args.iface,
                    args.attempts,
                    args.delay,
                    results,
                ),
                daemon=True,
            )
            for iid in instance_ids
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    print("\n" + "=" * 50, flush=True)
    all_ok = True
    for iid in instance_ids:
        if iid in results:
            print(f"  ✓ {iid[:7]}  →  {results[iid]}", flush=True)
        else:
            print(f"  ✗ {iid[:7]}  →  не найден", flush=True)
            all_ok = False
    print("=" * 50, flush=True)

    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
