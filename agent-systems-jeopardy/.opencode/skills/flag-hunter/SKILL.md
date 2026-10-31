---
name: flag-hunter
description: Find a CTF flag hidden behind encoding/compression wrappers or scattered in files, dumps and tool output. Use whenever you have a blob, response, memory dump, or decoded stream and need to extract a flag matching the competition regex, including multi-layer base/hex/rot/zlib wrappers.
---

# Flag Hunter

Универсальный поиск флага под обёртками кодировок/сжатия и в сыром выводе инструментов. Применяется во всех категориях.

## Правило валидности

Флаг валиден **только** если матчит regex соревнования. Дефолт: `ctfcup\{[^}]+\}` (переопредели из `current-state.md`). Любого кандидата финализирует `ctf-verifier`, не воркер.

## Быстрый grep (первым делом)

```bash
# по распакованному дереву, во всех кодировках
grep -R -a -oP 'ctfcup\{[^}]+\}' .
strings -a -n 6 <art> | rg -oP 'ctfcup\{[^}]+\}'
strings -a -e l <art> | rg -oP 'ctfcup\{[^}]+\}'   # UTF-16LE
strings -a -e b <art> | rg -oP 'ctfcup\{[^}]+\}'   # UTF-16BE
```

Многие forensics/misc-таски решаются именно recursive grep'ом по `binwalk -Me` выхлопу.

## Рекурсивный декодер обёрток

Если флага нет в открытом виде, но есть «подозрительная строка» (длинный base64/hex, высокая энтропия) — прогоняй через рекурсивный декодер: он снимает вложенные base64/base32/base85/hex/rot13/zlib/gzip/bz2 и грепает флаг на каждом уровне.

```bash
python3 skill/scripts/flaghunt.py <file_or_->              # stdin или файл
python3 skill/scripts/flaghunt.py --regex 'FLAG\{[^}]+\}' blob.txt
echo "<suspicious string>" | python3 skill/scripts/flaghunt.py -
```

## Чеклист обёрток (распознавание по виду)

| Признак | Кодировка | Декод |
|---|---|---|
| `[A-Za-z0-9+/=]`, кратно 4 | base64 | `base64 -d` |
| `[A-Z2-7=]` | base32 | `base32 -d` |
| `<~ ... ~>` или ASCII85 | base85/ascii85 | `python -c 'import base64,sys;print(base64.a85decode(...))'` |
| только hex-пары | hex | `xxd -r -p` |
| сдвиг букв | rot13/rotN/caesar | перебор 25 сдвигов |
| `78 9c`/`78 01`/`78 da` | zlib | `python zlib.decompress` |
| `1f 8b` | gzip | `gunzip` |
| `BZh` | bzip2 | `bunzip2` |
| реверс/по словам | reverse | `rev` |

## Правила

- Декодируй максимум ~6 уровней вглубь, грепая флаг после каждого (скрипт делает это сам).
- Не принимай подстроку лог-мусора за флаг — проверь баланс скобок и осмысленность.
- Нашёл — положи кандидата в `notes.md`, финализирует `ctf-verifier`.
