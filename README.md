# yacloud-ip-roller

Rolls the public IP of a Yandex Cloud VM until it lands in the [russia-mobile-internet-whitelist](https://github.com/hxehex/russia-mobile-internet-whitelist) — useful for VPN/proxy servers that must be reachable through Russian mobile operators.

## How it works

1. Downloads the allowed CIDR list from `hxehex/russia-mobile-internet-whitelist`
2. Checks the current public IP of your VM
3. If the IP is not in the target range — unbinds it and requests a new ephemeral address
4. Repeats until a matching IP is found (or the attempt limit is reached)

Use `--prefix 51.250` to hunt specifically for the `51.250.x.x` range, which has the broadest operator support in Russia.

## Requirements

- macOS / Linux
- Python 3.8+
- [Yandex Cloud CLI (`yc`)](https://yandex.cloud/en/docs/cli/quickstart)
- A Yandex Cloud VM with an ephemeral (dynamic) public IP

## Install

```bash
git clone https://github.com/princeofscale/yacloud-ip-roller.git
cd yacloud-ip-roller
```

No extra dependencies — uses only the Python standard library.

## Usage

```bash
python3 roll_ip.py --instance-id <VM_ID>
```

### Hunt specifically for 51.250.x.x

```bash
python3 roll_ip.py --instance-id <VM_ID> --prefix 51.250
```

### All options

```
--instance-id   VM ID in Yandex Cloud (required)
--prefix        Accept only IPs starting with this prefix (e.g. 51.250)
--mask          Minimum subnet prefix length to accept (default: 16)
                16 = accept /16 and more specific
                24 = accept only /24 and more specific
--iface         Network interface index (default: 0)
--attempts      Max number of attempts (default: 500)
--delay         Pause between remove-nat and add-nat in seconds (default: 2)
```

### Make the IP static after finding it

```bash
# Find the address ID
yc vpc address list

# Reserve it (make static)
yc vpc address update --reserved=true <address_id>
```

## Example output

```
Загрузка вайтлиста (маска /16)...
  Подсетей /16+: 2847  (пропущено /15 и шире: 412)
Итого: 2847 записей

Фильтр: только IP начинающиеся с '51.250'

[1/500] 158.160.121.55  —  не тот диапазон
  меняем IP...
[2/500] 93.77.183.10  —  не тот диапазон
  меняем IP...
[3/500] 51.250.117.6  —  не тот диапазон
  меняем IP...
...
✓ Готово! IP: 51.250.4.23  подсеть: 51.250.4.0/24
```

## Zones that yield 51.250.x.x

From testing, `ru-central1-d` tends to produce `51.250.x.x` addresses. Use that zone when creating your VM for best results.

## License

MIT
