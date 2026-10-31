---
name: stego
description: Proven multi-tool sequences for image and audio steganography. Use for PNG/JPG/GIF/BMP and WAV/MP3 challenges; enforces running at least three approaches before concluding there is no stego.
---

# Steganography

Проверенные последовательности. **Не объявляй «стего нет», пока не прогнал ≥3 разных подхода.**

## Всегда сначала

```bash
file <art>; exiftool <art>; xxd <art> | head
binwalk -Me <art>                 # вложенные файлы / данные после EOF (очень часто)
strings -a -n 6 <art> | rg -i 'ctfcup\{|flag'
```
Проверь: аномальный размер, лишние чанки, данные после маркера конца (PNG `IEND`, JPEG `FFD9`), подозрительные метаданные/комментарии.

## Image

### PNG / BMP / GIF (LSB-дружелюбные)
```bash
zsteg -a <png>                    # LSB по всем каналам/битам/порядкам
pngcheck -v <png>                 # битые/лишние/дублирующиеся чанки
```
- stegsolve-логика: плоскости бит, XOR/ADD каналов, цветовые фильтры.
- Палитра/прозрачность (GIF), LSB вручную через PIL/numpy.
- Сравнение визуально идентичных картинок: `compare a.png b.png diff.png`.

### JPEG (НЕ LSB — не трать zsteg)
```bash
steghide extract -sf <jpg> -p ''  # пустой пароль и пароль из условия
stegseek <jpg> rockyou.txt        # brute пароля steghide
```
- `jsteg`, `outguess`, анализ DCT. Appended data после `FFD9` → carve.

## Audio

```bash
sox <a.wav> -n spectrogram -o spec.png   # спектрограмма ОБЯЗАТЕЛЬНА
multimon-ng -t wav <a.wav>               # DTMF / морзе / пейджинг
```
- Открой в Audacity/Sonic Visualiser: спектрограмма (флаг часто виден картинкой), замедление/реверс, LSB-аудио.
- Стерео: разница/сумма каналов, скрытый канал. SSTV → `qsstv`.

## Правила

- Фиксируй, какие инструменты прогнаны (чтобы не повторяться).
- Внутри оказался другой артефакт (zip/бинарь/pcap) → профильному воркеру.
- Флаг валиден только по regex; кандидат — в `notes.md` для `ctf-verifier`.
