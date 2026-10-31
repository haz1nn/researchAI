# skill: flag-hunter

Переиспользуемый плейбук для первичного и финального поиска флага в произвольном наборе файлов. Работает одинаково для всех категорий.

## Когда использовать

- на этапе ingest, когда ты впервые видишь артефакты;
- на этапе extraction, когда у тебя есть распакованные/декодированные данные и нужно подтвердить, что в них нет флага прямым поиском.

## Инвариант

Формат флага берётся из `current-state.md` (`Flag format:`). По умолчанию `ctfcup\{[^}]+\}`. Все команды ниже используют этот regex — заменяй, если формат другой.

## Железный порядок

1. **Прямой grep (recursive, binary-safe).**
   ```
   rg -oP 'ctfcup\{[^}]+\}' -a <dir>
   # -a: обрабатывать бинарные как текст
   # -o: печатать только совпадение
   # -P: PCRE
   ```

2. **Один слой base64.** Base64-encoded флаг — классика. Прогон:
   ```
   # Вытащи все похожие base64-блоки длиной 20+ и попробуй декодировать.
   rg -oE '[A-Za-z0-9+/]{20,}={0,2}' -a <dir> | sort -u > /tmp/b64cands.txt
   while read -r L; do
     printf '%s' "$L" | base64 -d 2>/dev/null | grep -aoP 'ctfcup\{[^}]+\}' && echo "---in $L"
   done < /tmp/b64cands.txt
   ```

3. **Hex-encoded.**
   ```
   rg -oiE '([0-9a-f]{2}){8,}' -a <dir> | sort -u | while read -r L; do
     printf '%s' "$L" | xxd -r -p 2>/dev/null | grep -aoP 'ctfcup\{[^}]+\}'
   done
   ```

4. **ROT-семейство.** `ctfcup{` под ROT13 превращается в `pgspghc{`, под ROT47 — в `apsph2n`. Прогон:
   ```
   rg -oP '(pgspghc|apsph2|6pMp:A)' -a <dir>     # ROT13 / ROT47 / Atbash
   ```
   При матче — дешифруй окружающий контекст.

5. **zlib / gzip inflate.** В файлах с смешанным содержимым (pcap bodies, firmware blobs) могут быть сжатые куски:
   ```
   rg -obU --multiline --pcre2 '\x78\x9c|\x78\xda' -a <dir>
   ```
   При матче — попробуй `python3 -c "import zlib,sys; sys.stdout.buffer.write(zlib.decompress(open(sys.argv[1],'rb').read()[OFFSET:]))" <file> | grep -aoP 'ctfcup\{[^}]+\}'`.

6. **XOR одним байтом.** Для коротких блобов (<10 МБ):
   ```python
   # work/xor_sweep.py
   import sys, re
   data = open(sys.argv[1],'rb').read()
   pat = re.compile(rb'ctfcup\{[^}]+\}')
   for k in range(1, 256):
       dec = bytes(b ^ k for b in data)
       m = pat.search(dec)
       if m:
           print(f"key=0x{k:02x} match={m.group(0)!r}")
   ```

7. **Reverse-byte / endian swap.** Если флаг хранится word-swapped (например, little-endian 4-байтовые куски):
   ```python
   import struct, re
   data = open(sys.argv[1],'rb').read()
   # групп по 4 байта reverse
   swapped = b''.join(data[i:i+4][::-1] for i in range(0, len(data)-3, 4))
   print(re.findall(rb'ctfcup\{[^}]+\}', swapped))
   ```

## Правила

- Этот skill **не финализирует флаг**. Все попавшие кандидаты идут в `notes.md` с указанием слоя (base64/hex/rot13/xor-0xNN) и инструмента. Финализация — только через `ctf-verifier` и `tools/flag_check.py`.
- На `A-Za-z0-9+/{25,}=0,2` ругайся на false-positive — не прогоняй дольше 60 секунд. Если ничего не нашёл за минуту grep'ом — пора применять контекст таски.
- Не пропускай шаг 1 никогда. Удивительное количество тасок решается на шаге 1.
