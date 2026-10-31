---
name: ctf-forensics-stego-img
description: Стего в изображениях (PNG/JPG/BMP/GIF). Минимум три инструмента до объявления «stego нет».
phase: verification + extraction
model: medium
---

# ctf-forensics-stego-img

Плейбук — `.opencode/skills/stego-image/SKILL.md`.

## Железный порядок (до «stego нет» — все 7 шагов)

1. **Метаданные.**
   ```
   exiftool <img>
   # ищи: UserComment, Software, Copyright, author, dc:description, 
   # необычные chunks tEXt/zTXt/iTXt в PNG, APP markers в JPG, 
   # IPTC/XMP с base64 внутри.
   ```

2. **Trailer-данные.**
   ```
   binwalk <img>              # listing, НЕ extract
   # если > one entry — есть trailer. Внутри часто ZIP/7z/PK.
   # Проверь ручным split'ом по offset'у, не только -e.
   ```

3. **LSB-stego (PNG/BMP).**
   ```
   zsteg -a <png|bmp>
   # Пробуй все битплейны и порядки, а не только default.
   ```

4. **steghide (JPG/BMP/WAV).**
   ```
   stegseek <img> /usr/share/wordlists/rockyou.txt
   # Быстрый brute. Если пароль из вселенной таски — попробуй его вручную.
   ```

5. **Spectral-related только для JPG.** `jsteg`, `outguess` — отдельные инструменты.

6. **Визуальное.**
   - `convert <img> -separate work/channels_%d.png` — посмотри каналы;
   - `convert <img> -auto-level work/stretched.png` — выровняй гистограмму;
   - открыть в HexFiend/010 Editor и глазом искать PNG/ZIP magic в середине.

7. **Файл-полиглот.**
   - PNG с валидным ZIP после IEND (многие CTF любят это);
   - JPEG с данными после FFD9;
   - GIF с данными после `3B` trailer.
   ```
   # Пример извлечения trailer после PNG:
   python3 -c "d=open('f.png','rb').read(); i=d.find(b'IEND')+8; open('trailer.bin','wb').write(d[i:])"
   ```

## Правила

- Не объявляй «stego нет», пока не прошёл шаги 1–6 (шаг 7 — проверять, если видно что-то за концом файла).
- Для PNG запрещено пропускать zsteg. zsteg быстрый.
- Для JPG запрещено пропускать stegseek с rockyou.
- Если нашёл base64 внутри tEXt — декодируй и проверь, не ZIP/PNG/флаг.

## Выход

- `work/stego-notes.md` — что найдено на каждом шаге;
- если извлекли файл — положить в `work/extracted/` и, если это сам флаг-носитель, зафиксировать в `verification.md`;
- флаг через `ctf-verifier` → `flag.txt`.
