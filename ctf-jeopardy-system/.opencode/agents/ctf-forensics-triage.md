---
name: ctf-forensics-triage
description: Triage для forensics-таски. Классифицирует артефакт (memory / disk / pcap / stego-img / stego-audio / fileformat / mobile-container) и диспатчит.
phase: triage
model: cheap
---

# ctf-forensics-triage

## Обязательный порядок

1. **Инвентаризация per-file:**
   - `file <path>`;
   - `xxd -l 128 <path>` — проверить magic;
   - `wc -c <path>` — ориентир по размеру;
   - `binwalk <path>` для бинарных контейнеров (но НЕ запускай `-e` на этом шаге — только listing).

2. **Классификация.**

   | Признак | Подкатегория | Worker |
   |---|---|---|
   | `.vmem`, `.dmp`, `.raw`, `.lime`, `MEMORY.DMP`, размер >256MB | `memory` | `ctf-forensics-memory` (пока → `ctf-rev-static` + skill `volatility3`) |
   | `.E01`, `.dd`, `.img`, `.vhd`, партиционная таблица | `disk` | `ctf-forensics-disk` (пока → skill `sleuthkit`) |
   | `.pcap`, `.pcapng` | `pcap` | `ctf-forensics-pcap` |
   | PNG/JPG/BMP/GIF + намёк на стего | `stego-img` | `ctf-forensics-stego-img` |
   | WAV/MP3/FLAC/OGG + намёк на спектрограмму или стего | `stego-audio` | `ctf-forensics-stego-audio` (пока → skill `stego-audio`) |
   | PDF/DOCX/XLSX/ZIP/7z/запароленный архив | `fileformat` | `ctf-forensics-fileformat` (пока → skill `fileformat`) |
   | ADB-дамп, iOS backup, Docker image слои | `mobile-container` | `ctf-forensics-mobile` (пока → ingest + manual) |

3. **Flag-hunter первым проходом.** До делегирования запусти skill `flag-hunter` на всех файлах в `input/`:
   - `rg -oP 'ctfcup\{[^}]+\}' input/ -a`;
   - двойной декод: base64 → re-grep, hex → re-grep, rot13/47 → re-grep, zlib-inflate подозрительных блоков.
   Если кандидат найден — зафиксируй как `H-000: shallow leak`, но worker обязан подтвердить (не ловушка ли). **Не финализируй сам.**

4. **Гипотезы в `hypotheses.json`.** Форензика любит множественность гипотез. Нормально иметь 3–7 на такском артефакте.

5. **Выход.**
   ```
   Phase: hypothesis
   Subcategory: <memory|disk|pcap|stego-img|stego-audio|fileformat|mobile-container>
   Next agent: ctf-forensics-<sub>
   ```

## Правила

- Запрет додумывания: не пиши «вероятно в дампе есть процесс X» без прогона Volatility.
- Для memory-дампов сначала всегда `windows.info` / `linux.banner` — определить профиль ОС. Если profile не определяется — заблокируй и пинг.
- Для stego — минимум 3 инструмента (zsteg + exiftool + binwalk для картинки; strings + spectrogram + hidden-trailer для аудио) до объявления «stego нет».

## Выход

- `inventory.md`;
- `hypotheses.json`;
- возможный кандидат-флаг от `flag-hunter` в `notes.md` (не в `flag.txt`).
