---
name: forensics-triage
description: 60-second deterministic dispatch for forensics artifacts. Use at the start of any forensics task to classify memory/pcap/disk/stego/office/zip by magic bytes and route to the right tool before deep analysis.
---

# Forensics Triage

Цель: за ≤60с классифицировать входной файл и выбрать ветку. Классифицируй по инструменту, не угадывай.

## Шаг 1

```bash
file <input>; ls -la <input>; xxd <input> | head
grep -R -a 'ctfcup{' .                 # по уже распакованному — решает многие таски
binwalk -Me <input>                    # carve вложенных файлов
strings -a -n 8 <input> | rg -i 'ctfcup\{|flag|password'
```

## Шаг 2 — магик-байты → ветка

| Магик / признак | Класс | Ветка (worker) |
|---|---|---|
| `MDMP`, Windows pool-tags, `HIBR`/`PAGEDUMP`, большой `.raw`/`.vmem`/`.lime`/`.dmp` | memory dump | `ctf-forensics` (Volatility3) |
| `d4 c3 b2 a1` / `0a 0d 0d 0a` | pcap/pcapng | `ctf-forensics` (tshark/Zeek) |
| `EVTX` | Windows event log | EvtxECmd/python-evtx |
| `EWF`/`evf`, MBR/GPT, `.E01`/`.dd`/`.img` | disk image | `ctf-forensics` (Sleuthkit) |
| `PK\x03\x04` c `word/`,`xl/`,`ppt/` | Office | `ctf-forensics` (olevba) |
| `PK\x03\x04` c `META-INF/`/`classes.dex` | JAR/APK | → rev (`ctf-rev-managed`) |
| `PK\x03\x04` прочее | ZIP (возможно запаролен) | `ctf-forensics` (zip crack) |
| `%PDF-` | PDF | `ctf-forensics` (pdf-parser) |
| `d0 cf 11 e0` | OLE/legacy Office | `ctf-forensics` (oledump) |
| `\x89PNG`,`\xff\xd8\xff`,`GIF8`,BMP | image | → `ctf-stego` |
| `RIFF…WAVE`, MP3, FLAC | audio | → `ctf-stego` |
| `7f 45 4c 46`/`MZ` | executable | → rev/pwn (эскалировать категорию) |

## Шаг 3 — если магик не бьёт

- `binwalk -Me` → рекурсивный carve, затем `grep -R 'ctfcup{'`.
- `exiftool`, `trid`, `yara -r rules/ file`.
- Если dump > 500MB и не классифицируется — считай memory → `vol windows.info`/`banners.Banners`.

## Правила

- Для memory **запрещено** запускать Volatility-плагины до `windows.info`/`banners` (иначе падают молча).
- Для stego — минимум 3 инструмента до вывода «стего нет».
- Флаг валиден только по regex; кандидат — в `notes.md` для `ctf-verifier`.
