#!/usr/bin/env python3
"""
Крутит публичный IP на VPS в Яндекс Облаке до попадания в вайтлист
russia-mobile-internet-whitelist.

Улучшения v2:
- Тихий режим: yc-вывод подавлен, прогресс чистый
- --prefix: фильтрует только нужный диапазон (напр. 51.250)
- Меньше задержек между remove/add
- JSON-формат для парсинга VM (быстрее чем YAML)
- --mask 16 по умолчанию — принимает /16–/24 диапазоны
"""
import argparse, subprocess, urllib.request, ipaddress, time, json, sys, os

CIDR_URL = "https://raw.githubusercontent.com/hxehex/russia-mobile-internet-whitelist/main/cidrwhitelist.txt"
YC = os.path.expanduser("~/yandex-cloud/bin/yc")


def fetch_whitelist(min_prefix):
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
    print(f"  Подсетей /{min_prefix}+: {len(networks)}  (пропущено /{min_prefix - 1} и шире: {skipped})", flush=True)
    return networks


def is_in_whitelist(ip_str, networks):
    addr = ipaddress.ip_address(ip_str)
    for net in networks:
        if addr in net:
            return net
    return None


def get_current_ip(instance_id):
    out = subprocess.check_output(
        [YC, "compute", "instance", "get", "--id", instance_id, "--format", "json"],
        stderr=subprocess.DEVNULL
    )
    data = json.loads(out)
    for iface in data["network_interfaces"]:
        nat = iface.get("primary_v4_address", {}).get("one_to_one_nat", {})
        if "address" in nat:
            return nat["address"]
    return None


def remove_nat(instance_id, iface_index):
    subprocess.check_call(
        [YC, "compute", "instance", "remove-one-to-one-nat",
         "--id", instance_id, "--network-interface-index", str(iface_index)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def add_nat(instance_id, iface_index):
    subprocess.check_call(
        [YC, "compute", "instance", "add-one-to-one-nat",
         "--id", instance_id, "--network-interface-index", str(iface_index)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def main():
    parser = argparse.ArgumentParser(
        description="Крутит публичный IP на VPS в Яндекс Облаке, пока он не попадёт в вайтлист."
    )
    parser.add_argument("--instance-id", required=True,
        help="ID виртуальной машины (пример: fhm2lbhmnagc4ec6u6me)")
    parser.add_argument("--mask", type=int, default=16, metavar="PREFIX",
        help="Минимальная длина префикса подсети (по умолчанию 16). "
             "Чем больше — точнее. 24 = только /24+, 16 = принимает /16 и точнее.")
    parser.add_argument("--iface", type=int, default=0, metavar="INDEX",
        help="Индекс сетевого интерфейса VM (по умолчанию 0)")
    parser.add_argument("--attempts", type=int, default=500, metavar="N",
        help="Максимальное количество попыток (по умолчанию 500)")
    parser.add_argument("--prefix", type=str, default=None, metavar="IP_PREFIX",
        help="Принимать только IP с этим началом (напр. '51.250'). "
             "По умолчанию — любой IP из вайтлиста.")
    parser.add_argument("--delay", type=float, default=2.0, metavar="SEC",
        help="Задержка после remove-nat перед add-nat (по умолчанию 2с)")
    args = parser.parse_args()

    print(f"Загрузка вайтлиста (маска /{args.mask})...", flush=True)
    networks = fetch_whitelist(args.mask)
    print(f"Итого: {len(networks)} записей\n", flush=True)

    if args.prefix:
        print(f"Фильтр: только IP начинающиеся с '{args.prefix}'\n", flush=True)

    for attempt in range(1, args.attempts + 1):
        # Получаем текущий IP
        ip = None
        for _ in range(5):
            try:
                ip = get_current_ip(args.instance_id)
                break
            except Exception:
                time.sleep(2)

        if not ip:
            print(f"[{attempt}/{args.attempts}] IP недоступен, пропускаем...", flush=True)
            time.sleep(3)
            continue

        # Проверяем prefix-фильтр
        if args.prefix and not ip.startswith(args.prefix):
            match = is_in_whitelist(ip, networks)
            status = f"не тот диапазон ({ip})"
            print(f"[{attempt}/{args.attempts}] {ip}  —  {status}", flush=True)
        else:
            match = is_in_whitelist(ip, networks) if ip else None
            if ip and match:
                print(f"\n✓ Готово! IP: {ip}  подсеть: {match}", flush=True)
                return
            status = "не в списке" if not match else f"В ВАЙТЛИСТЕ ({match})"
            print(f"[{attempt}/{args.attempts}] {ip}  —  {status}", flush=True)

        print(f"  меняем IP...", flush=True)
        try:
            remove_nat(args.instance_id, args.iface)
        except Exception as e:
            print(f"  ошибка remove-nat: {e}", flush=True)
            time.sleep(3)
            continue

        time.sleep(args.delay)

        try:
            add_nat(args.instance_id, args.iface)
        except Exception as e:
            print(f"  ошибка add-nat: {e}", flush=True)
            time.sleep(3)
            continue

        time.sleep(args.delay + 1)

    print(f"\nНе удалось найти подходящий IP за {args.attempts} попыток", flush=True)
    sys.exit(1)


if __name__ == "__main__":
    main()
