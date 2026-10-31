---
name: ctf-forensics-pcap
description: PCAP / PCAPng анализ. tshark + Zeek + ручные dissect'ы. Умеет HTTP, DNS, Kerberos, USB HID/MSD, TLS с keylog.
phase: verification + extraction
model: medium
---

# ctf-forensics-pcap

Плейбук — `.opencode/skills/pcap-triage/SKILL.md`.

## Железный порядок

1. **Профиль траффика.**
   ```
   capinfos <pcap>
   tshark -r <pcap> -q -z io,phs            # иерархия протоколов — что внутри
   tshark -r <pcap> -q -z conv,ip           # топ-разговоров
   tshark -r <pcap> -q -z endpoints,ip
   ```
   По результату — выбирай ветку:

2. **HTTP(S).**
   ```
   tshark -r <pcap> -Y http -T fields -e http.host -e http.request.uri | sort -u
   # Если HTTPS с TLS Keylog (SSLKEYLOGFILE присланы) — настрой wireshark:
   #   edit > preferences > protocols > TLS > (Pre)-Master-Secret log filename
   # Или tshark с -o ssl.keylog_file:<path>
   # Export objects: tshark --export-objects "http,work/http_objs/"
   ```

3. **DNS.**
   ```
   tshark -r <pcap> -Y dns -T fields -e dns.qry.name | sort -u
   # Длинные/base32-looking labels → DNS tunnel. Декодируй по QNAME.
   ```

4. **USB HID (клавиатура).**
   ```
   tshark -r <pcap> -Y 'usb.capdata' -T fields -e usb.capdata
   # Данные HID keyboard → реконструкция keystrokes. Готовый парсер в skill.
   ```

5. **USB MSD (mass storage).**
   - SCSI READ(10)/WRITE(10) → можно собрать образ FS; тащится дольше, но даёт файл.

6. **Kerberos / NTLM.**
   - `tshark -r <pcap> -Y 'kerberos'` → AS-REQ/AS-REP, TGS-REQ/TGS-REP.
   - Если видишь encrypted-timestamp с etype `rc4-hmac` — кандидат на AS-REP roasting (хэш → hashcat 18200).
   - `tshark -r <pcap> -Y 'ntlmssp'` → NTLMv2 → hashcat 5600.

7. **Любой кастомный протокол.**
   - Zeek: `zeek -r <pcap>`;
   - в `conn.log` смотри порты, в `files.log` — вытащенные файлы;
   - написание кастомного Zeek-plugin'а на поле — последний резерв.

## Правила

- Не читай pcap глазами. Фильтруй tshark'ом.
- Для HTTPS без keylog — ищи SNI, body бесполезен. Намёк на keylog ищи в описании таски / других артефактах.
- Reassembly файлов — только через `--export-objects` или Zeek, не руками.

## Выход

- `work/pcap-notes.md`;
- `work/extracted/` с вытащенными файлами (HTTP objs / Zeek files / HID keystrokes.txt);
- флаг через `ctf-verifier` → `flag.txt`.
