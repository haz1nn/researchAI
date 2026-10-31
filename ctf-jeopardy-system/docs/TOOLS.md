# Верифицированный инструментарий

Все URL ниже подтверждены WebFetch'ем, дата сверки — 2026-10-31. Если что-то переехало — поправь и обнови дату.

## Reverse

| Инструмент | URL | Назначение | Форма |
|---|---|---|---|
| GhidraMCP | https://github.com/LaurieWired/GhidraMCP | MCP-сервер поверх Ghidra | MCP (Java) |
| radare2 | https://github.com/radareorg/radare2 | фреймворк RE | CLI (C) |
| r2ai | https://github.com/radareorg/r2ai | LLM-ассистент внутри r2 | r2-плагин / CLI |
| capa | https://github.com/mandiant/capa | идентификация capabilities в бинаре | CLI / Python |
| FLARE-emu | https://github.com/mandiant/flare-emu | Unicorn-based emulation helper | Python (IDA-centric, но usable отдельно) |
| angr | https://github.com/angr/angr | symbolic execution | Python |
| qiling | https://github.com/qilingframework/qiling | инструментируемая эмуляция бинарей | Python |

## Pwn

| Инструмент | URL | Назначение | Форма |
|---|---|---|---|
| pwndbg | https://github.com/pwndbg/pwndbg | GDB/LLDB-плагин для exploit-dev (branch `dev`) | GDB plugin |
| GEF (hugsy) | https://github.com/hugsy/gef | альтернативный GDB-плагин | GDB plugin |
| GEF (bata24) | https://github.com/bata24/gef | расширенный форк GEF | GDB plugin |
| pwninit | https://github.com/io12/pwninit | автостарт exploit-pwn-таски | CLI (Rust) |
| one_gadget | https://github.com/david942j/one_gadget | поиск one-gadget RCE в libc | CLI (Ruby) |
| libc-database | https://github.com/niklasb/libc-database | поиск libc по сигнатурам | CLI (shell) |
| Ropper | https://github.com/sashs/Ropper | ROP gadget finder, multi-arch | CLI / Python |

## Forensics

| Инструмент | URL | Назначение | Форма |
|---|---|---|---|
| Volatility3 | https://github.com/volatilityfoundation/volatility3 | memory forensics (branch `develop`) | CLI / Python |
| Sleuthkit | https://github.com/sleuthkit/sleuthkit | disk forensics (TSK) | CLI / C |
| zsteg | https://github.com/zed-0xff/zsteg | stego в PNG/BMP | CLI (Ruby gem) |
| stegseek | https://github.com/RickdeJager/stegseek | brute steghide | CLI (C++) |
| bkcrack | https://github.com/kimci86/bkcrack | known-plaintext атака на legacy zip | CLI (C++) |
| binwalk | https://github.com/ReFirmLabs/binwalk | firmware extraction (Rust rewrite) | CLI (Rust) |
| unblob | https://github.com/onekey-sec/unblob | универсальный распаковщик контейнеров | CLI / Python |
| oletools | https://github.com/decalage2/oletools | анализ MS OLE2 / Office | CLI / Python |

Важно: репозиторий `jbremer/oletools` **не существует** (404). Канонический — `decalage2/oletools`.

## Hardware / Signals

| Инструмент | URL | Назначение | Форма |
|---|---|---|---|
| URH | https://github.com/jopohl/urh | Universal Radio Hacker | GUI/CLI (Python) |
| rtl_433 | https://github.com/merbanan/rtl_433 | декодирование ISM-радиоустройств | CLI (C) |
| sigrok | https://sigrok.org | logic analyzer / scope / DMM suite | много подпроектов (`sigrok-cli`, PulseView, libsigrokdecode) |
| SVD-Loader-Ghidra | https://github.com/leveldown-security/SVD-Loader-Ghidra | подгрузка SVD-периферии в Ghidra | Ghidra script |
| ChipWhisperer | https://github.com/newaetech/chipwhisperer | side-channel + fault injection (branch `develop`) | HW + Python |
| can-utils | https://github.com/linux-can/can-utils | SocketCAN tools | CLI (C) |
| IceStorm | https://github.com/YosysHQ/icestorm | Lattice iCE40 FPGA bitstream RE | CLI toolchain |

## Memo по версиям

- `volatility3` default branch — `develop`, не `master`.
- `sleuthkit` default — `develop-4.1x`.
- `pwndbg` default — `dev`.
- `binwalk` — Rust rewrite, не Python v2. API другой.
- `GEF` имеет две актуальные ветки: `hugsy/gef` (каноничный) и `bata24/gef` (с расширенными командами). Для автоматизации лучше `bata24` — больше встроенных команд `heap-analysis`.

## Только GhidraMCP — MCP-сервер

Из всего списка **MCP-сервером является только GhidraMCP**. Остальное — CLI, которое вызывается через bash-tool. При желании можно поднять MCP-обёртку поверх gdb-mi, но готового production-grade MCP-сервера для gdb на 2026-10 **нет**.
