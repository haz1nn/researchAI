# skill: forensics-triage

60-секундный диспатч forensics-артефакта.

## Шаг 0. Flag-hunter первым проходом

Всегда. См. skill `flag-hunter`. Да, это может решить таску за 10 секунд.

## Шаг 1. Классификация по magic

| Первые байты | Расшифровка | Ветка |
|---|---|---|
| `4D 5A` (`MZ`) | Windows PE — не forensics, это rev | → `ctf-category-router` вернуть |
| `7F 45 4C 46` (`\x7fELF`) | ELF — тоже rev | → `ctf-category-router` вернуть |
| `D4 C3 B2 A1` или `A1 B2 C3 D4` (le/be) | pcap classic | → `ctf-forensics-pcap` |
| `0A 0D 0D 0A` + `pcapng` | pcapng | → `ctf-forensics-pcap` |
| `45 56 46` (`EVF`) | EnCase E01 (ewf) | → `ctf-forensics-disk` |
| `01 00 00 00` + partition table / FAT boot sector `55 AA` в конце 512-блока | raw disk image | → `ctf-forensics-disk` |
| `50 41 47 45 44 55 36 34` (`PAGEDU64`) или `44 55 4D 50` (`DUMP`) | Windows memory dump (crashdump) | → `ctf-forensics-memory` |
| LiME magic `EMiL` | Linux memory | → `ctf-forensics-memory` |
| `89 50 4E 47` | PNG | → `ctf-forensics-stego-img` |
| `FF D8 FF` | JPEG | → `ctf-forensics-stego-img` |
| `47 49 46 38` | GIF | → `ctf-forensics-stego-img` |
| `42 4D` + 2 reasonable bytes | BMP | → `ctf-forensics-stego-img` |
| `52 49 46 46` + `WAVE` | WAV | → `ctf-forensics-stego-audio` |
| `49 44 33` или `FF FB` / `FF F3` | MP3 | → `ctf-forensics-stego-audio` |
| `66 4C 61 43` (`fLaC`) | FLAC | → `ctf-forensics-stego-audio` |
| `25 50 44 46` (`%PDF`) | PDF | → `ctf-forensics-fileformat` |
| `50 4B 03 04` | ZIP / docx / xlsx / pptx / APK / jar | → разобрать: `unzip -l`; если `AndroidManifest.xml` — это rev-managed |
| `37 7A BC AF 27 1C` | 7z | → `ctf-forensics-fileformat` |

## Шаг 2. Контейнеры

Для zip/7z/rar/pdf:
- `unzip -l` / `7z l` / `pdfinfo` для содержимого;
- если запаролен — `fcrackzip -D -p rockyou.txt`, `bkcrack` при известном plaintext.

## Шаг 3. Memory dump — profile detection

```
vol -f <dump> windows.info          # Windows
vol -f <dump> banners.Banners       # Linux: достать строку kernel banner
```

Если профиль не найден — скачать подходящую symbols-таблицу (ссылка — в skill `volatility3-plugins`).

## Шаг 4. Disk image

```
mmls <image>                        # layout разделов
fsstat -o <offset> <image>          # inspect FS
fls -r -o <offset> <image>          # recursive file list
icat -o <offset> <image> <inode> > work/extracted-file.bin
```

TSK (sleuthkit) — быстрее монтирования, безопаснее.

## Шаг 5. PCAP — см. `ctf-forensics-pcap` агента

Там detailed. Здесь только: `tshark -r <pcap> -q -z io,phs` для профиля.

## Шаг 6. Решение

- Записать в `current-state.md` `Subcategory:` + `Next agent:`.
- Создать гипотезы в `hypotheses.json`. Для forensics нормально 3–7 параллельных гипотез.
