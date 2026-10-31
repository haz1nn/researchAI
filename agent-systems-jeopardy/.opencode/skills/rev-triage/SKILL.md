---
name: rev-triage
description: Fast decision tree for reverse-engineering targets. Use at the start of any rev task to classify the binary format (ELF/PE/.NET/Java/APK/pyc/wasm/Go/Rust/packed/VM) and pick the right tool before decompiling.
---

# Reverse Triage

Цель: за ≤60с классифицировать артефакт и выбрать инструмент. Не декомпилируй вслепую.

## Шаг 1 — опознание

```bash
file <bin>
rabin2 -I <bin>            # arch, bits, endian, stripped, canary, nx, pic
Detect-It-Easy / die <bin> # packer/compiler id
binwalk -E <bin>           # entropy: >7.2 равномерно и мало импортов → packed
strings -eL -n6 <bin> | head; strings -e l <bin> | head   # ASCII + UTF-16
capa <bin>                 # capabilities: crypto / anti-debug / networking
```

## Шаг 2 — ветка по формату

| Признак | Формат | Инструмент / следующий воркер |
|---|---|---|
| `7f 45 4c 46` | ELF | Ghidra/r2 → `ctf-rev-static`; если pwn-признаки → `ctf-pwn` |
| `MZ`/PE, CLR header | .NET | ILSpy/dnSpyEx/de4dot → `ctf-rev-managed` |
| `MZ`/PE native | PE | Ghidra, DIE, PE-bear → `ctf-rev-static` |
| `ca fe ba be` | Java class/JAR | jadx/cfr → `ctf-rev-managed` |
| `dex\n035` / APK zip | Android | jadx/apktool → `ctf-rev-managed` (native .so → static) |
| pyc magic / PyInstaller | Python | pyinstxtractor-ng + pycdc → `ctf-rev-managed` |
| `\0asm` | WASM | wasm2wat/wasm-decompile → `ctf-rev-managed` |
| `\x1bLua` | Lua | luadec/unluac → `ctf-rev-managed` |
| строки `runtime.`,`go:` | Go | IDA/Ghidra + golang_renamer → `ctf-rev-static` |
| строки `rustc`, panic-locs | Rust | Ghidra + rust_demangler → `ctf-rev-static` |
| UPX / known packer | packed | `upx -d`, затем ре-триаж |
| высокая entropy, custom packer | packed | FLARE-emu/unicorn, dump at OEP → `ctf-rev-dynamic` |
| огромный `switch(opcode)` / jmp-table | custom VM | найти dispatcher → `ctf-rev-static` + disassembler-скрипт |

## Шаг 3 — быстрые победы

- Проверка флага — чистый `strcmp`/XOR с константой из `.rodata` → решается статикой за минуты.
- Крипто-константы как якорь: TEA `0x9E3779B9`, MD5 `0x67452301`, SHA1 `0x5A827999`, AES S-box, CRC-таблицы. Нашёл — пиши алгоритм явно.
- Managed-формат → **никогда** не Ghidra, сразу managed-декомпилятор.
- Есть сетевой клиент/сервер → Frida/tshark на loopback → `ctf-rev-dynamic`.

Результат триажа → `triage.md` + выбор следующего воркера.
