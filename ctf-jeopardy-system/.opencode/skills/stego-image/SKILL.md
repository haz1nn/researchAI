# skill: stego-image

Полный плейбук для стего в картинках. Применять в `ctf-forensics-stego-img`.

## Железный порядок

### 1. Метаданные

```
exiftool <img> | tee work/exif.txt
```

Смотри:
- `UserComment`, `Software`, `Copyright`, `XMP`, `IPTC`, `dc:description`;
- в PNG — `tEXt`/`zTXt`/`iTXt` chunks (часто туда прячут base64/hex).

### 2. Hidden trailer / append

```
binwalk <img>             # listing only
# если entries > 1 — есть что-то после основного файла
```

Для PNG — всё после `IEND` (`49 45 4E 44 AE 42 60 82`) — append:
```
python3 - <<'PY'
d = open("input/f.png","rb").read()
end = d.index(b'IEND') + 8
if end < len(d):
    open("work/trailer.bin","wb").write(d[end:])
    print(f"trailer: {len(d)-end} bytes")
PY
```

Для JPEG — всё после `FF D9`:
```
python3 - <<'PY'
d = open("input/f.jpg","rb").read()
end = d.rindex(b'\xff\xd9') + 2
if end < len(d):
    open("work/trailer.bin","wb").write(d[end:])
PY
```

### 3. LSB-stego (PNG/BMP)

```
zsteg -a input/f.png | tee work/zsteg.txt
```

zsteg проверяет все битплейны, порядки обхода и каналы. Если нашёл что-то похожее на текст / файл — вытащи напрямую:
```
zsteg --extract b1,rgb,lsb,xy input/f.png > work/lsb.bin
```

### 4. steghide (JPG/BMP/WAV/AU)

```
stegseek input/f.jpg /usr/share/wordlists/rockyou.txt
# или с небольшим кастомным словарём, если тема таски даёт подсказки
```

### 5. Выравнивание / каналы

Иногда данные видны глазом после выравнивания:
```
convert input/f.png -auto-level work/stretched.png
convert input/f.png -separate work/channel_%d.png
convert input/f.png -negate work/negate.png
```

### 6. jsteg / outguess (JPG)

```
jsteg reveal input/f.jpg work/jsteg.out
outguess -r input/f.jpg work/outguess.out
```

### 7. Полиглот и мусор

- Открой в HexFiend/010 — ищи PNG/ZIP/PK в середине;
- попробуй `foremost -i input/f.jpg -o work/foremost` — иногда вытаскивает вложенные файлы;
- если видишь pixel-mapped data — попробуй `python3 -c "from PIL import Image; i=Image.open('f.png'); i.save('f.bmp')"` и посмотри raw.

## Что НЕ запускать

- `strings` — почти бесполезен для картинок, кроме как найти trailer по-быстрому.
- Не прогоняй stegseek без wordlist — он тогда просто crack-with-empty-dict.
- Не трать время на одинокий `exiftool`, если первые 6 шагов не дали ничего — вернись к `ctf-forensics-triage`, возможно таска вообще не stego.

## Выход

- `work/stego-notes.md` с тем, что сделано и что найдено;
- `work/extracted/*` — найденные полезные файлы;
- кандидат-флаг — через `ctf-verifier`.
