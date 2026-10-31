# skill: firmware-linux

Прошивки с Linux rootfs (роутеры, камеры, IoT). Применяет `ctf-hw-firmware`.

## Шаг 1. Безопасная распаковка

Downloaded files are untrusted. Распаковывай в отдельную подпапку и не запускай интерпретатор ИЗ неё (защита от planted-`json.py` при `import json`).

```
mkdir -p work/extracted
cd work/extracted
binwalk -Me ../../input/fw.bin        # Rust binwalk 2026+; -M рекурсивно
```

Альтернатива — unblob (https://github.com/onekey-sec/unblob), предсказуемее для редких форматов:
```
unblob -o work/extracted input/fw.bin
```

## Шаг 2. Инвентаризация rootfs

```
# найди корень squashfs/ubifs/jffs2 внутри extracted/
find work/extracted -name 'etc' -type d
# первый найденный корень:
ROOT=work/extracted/.../squashfs-root
ls -la "$ROOT/etc/" "$ROOT/bin/" "$ROOT/usr/bin/"
```

Чек-лист интересных мест:

| Путь | Что искать |
|---|---|
| `/etc/passwd` | захардкоженные пользователи |
| `/etc/shadow` | хэши паролей (`john --format=sha512crypt` / hashcat mode `1800`) |
| `/etc/init.d/`, `/etc/rc.local`, `/etc/rcS` | что стартует |
| `/etc/dropbear/`, `/root/.ssh/` | SSH ключи |
| `/bin/busybox` | кастомные апплеты |
| `/opt/*`, `/usr/local/*`, `/usr/sbin/*` | кастомные бинари |
| `/www/`, `/htdocs/`, `/web/` | веб-морда роутера — часто захардкоженные креды в CGI |
| `/etc/config/*` (OpenWRT) | конфигурация |
| `/tmp/` в rootfs | иногда забытые дампы/логи |

## Шаг 3. Прямой поиск флага

```
grep -r 'ctfcup{' "$ROOT" 2>/dev/null
grep -rE '[Ff]lag|SECRET|TOKEN|CTFCUP' "$ROOT" | head -50

# И на незамаунтированных блобах тоже:
rg -oP 'ctfcup\{[^}]+\}' -a work/extracted/
```

## Шаг 4. Реверс кастомных бинарей

Любой `>50KB` бинарь в `/usr/sbin/` или `/opt/` — потенциальный target. Передай каждого в `ctf-rev-static` отдельным work-item'ом.

## Шаг 5. Эмуляция

Для одного бинаря (user-mode):
```
# статически слинкован
qemu-mipsel-static ./target     # или -arm, -aarch64 — зависит от архитектуры

# динамически (с rootfs)
qemu-arm -L work/extracted/.../squashfs-root ./target
```

qiling для сложных случаев (где нужны сетевые/filesystem моки):
```python
# work/emu.py
from qiling import Qiling
ql = Qiling(['./target'], 'work/extracted/.../squashfs-root', verbose=1)
ql.run()
```

Для прошивки целиком (board emulation) — `qemu-system-arm -M <machine>` с соответствующей dtb/kernel. Это редкая ветка в CTF — обычно хватает user-mode.

## Шаг 6. Веб-морда

Если в `/www` есть `.cgi` / `*.lua` — часто таска сводится к auth-bypass или command injection:
- `strings cgibin | grep -E "sprintf|system|popen"` — быстрый поиск command injection;
- `grep -r 'admin' /www` — захардкоженные логины.

## Правила

- Не монтируй образ в root. Используй `unsquashfs` / `fls` / `icat`.
- Не запускай cross-arch бинарники нативно — qemu-user или qiling.
- Если прошивка подписана (uImage, FIT image) — не ломай подпись, работай с распакованным rootfs.
