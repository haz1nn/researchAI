# skill: pcap-triage

Используется в `ctf-forensics-pcap`.

## Шаг 0. Профиль

```
capinfos <pcap>
tshark -r <pcap> -q -z io,phs             # иерархия протоколов
tshark -r <pcap> -q -z conv,ip            # топ-разговоры
tshark -r <pcap> -q -z endpoints,ip
```

Запись в `work/pcap-profile.md`: какие протоколы, сколько, кто с кем.

## Шаг 1. HTTP(S)

```
# все HTTP запросы
tshark -r <pcap> -Y http -T fields \
  -e http.host -e http.request.method -e http.request.uri \
  -e http.response.code \
  -E separator=' ' -E occurrence=f

# все HTTP объекты вытащить файлами
mkdir -p work/http_objs
tshark -r <pcap> --export-objects "http,work/http_objs/"
```

Если HTTPS и есть TLS keylog:
```
tshark -r <pcap> -o 'tls.keylog_file:keylog.txt' -V ...
```

## Шаг 2. DNS

```
tshark -r <pcap> -Y dns -T fields -e dns.qry.name | sort -u | tee work/dns-queries.txt
# Если видишь длинные base32/base64-looking labels → DNS tunnel
```

Классика: имя `aGVsbG8=.evil.com` → base64-кодированный "hello".

## Шаг 3. USB

Класс устройства:
```
tshark -r <pcap> -V -c 20 | grep -i "bInterfaceClass"
```

Если HID keyboard (`0x03`, subclass `0x01`, protocol `0x01`):
```
tshark -r <pcap> -Y 'usb.capdata' -T fields -e usb.capdata | tr ':' ' ' > work/hid.hex
```

Парсер HID keyboard → keystrokes:
```python
# work/hid_decode.py
# Простой парсер HID report descriptor (8 байт): modifier, reserved, 6 keycodes
MAP = {
  0x04:'a',0x05:'b',0x06:'c',0x07:'d',0x08:'e',0x09:'f',0x0A:'g',0x0B:'h',
  0x0C:'i',0x0D:'j',0x0E:'k',0x0F:'l',0x10:'m',0x11:'n',0x12:'o',0x13:'p',
  0x14:'q',0x15:'r',0x16:'s',0x17:'t',0x18:'u',0x19:'v',0x1A:'w',0x1B:'x',
  0x1C:'y',0x1D:'z',
  0x1E:'1',0x1F:'2',0x20:'3',0x21:'4',0x22:'5',0x23:'6',0x24:'7',0x25:'8',
  0x26:'9',0x27:'0',
  0x2C:' ',0x2D:'-',0x2E:'=',0x2F:'[',0x30:']',0x31:'\\',0x33:';',0x34:"'",
  0x36:',',0x37:'.',0x38:'/',
  0x28:'\n',0x2A:'<BS>',0x2B:'<TAB>',
}
import sys
out = []
with open(sys.argv[1]) as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) < 8: continue
        shift = int(parts[0],16) & 0x22
        for b in parts[2:8]:
            k = int(b,16)
            if k == 0: continue
            ch = MAP.get(k, f'<{k:02x}>')
            if shift and ch.isalpha(): ch = ch.upper()
            out.append(ch)
print(''.join(out))
```

Если HID mouse — вытащи XY-дельты и нарисуй matplotlib'ом; флаг часто рисуется мышью.

## Шаг 4. Kerberos / NTLM

```
tshark -r <pcap> -Y 'kerberos.msg_type == 11' -V       # AS-REQ
tshark -r <pcap> -Y 'kerberos.msg_type == 13' -V       # TGS-REP

# NTLMSSP
tshark -r <pcap> -Y 'ntlmssp' -V
```

Если нашёл AS-REP с etype RC4 (`etype=23`) — экспорт в `john/hashcat`-формат:
`$krb5asrep$23$user@realm:<cipher>:<cipher-tail>` (hashcat mode `18200`).

## Шаг 5. Zeek для кастомного

```
mkdir -p work/zeek && cd work/zeek
zeek -r ../../input/<pcap>
# conn.log, dns.log, http.log, files.log, ssl.log, …
```

Для кастомного binary-протокола — писать `.zeek`-плагин с полями по вручную-реверсенному формату.

## Шаг 6. TLS raw

Без keylog TLS-content декодировать нельзя. Но:
- SNI в ClientHello (`tls.handshake.extensions_server_name`) часто содержит интересное имя;
- JA3-fingerprint — если нужно определить клиентскую библиотеку.

## Шаг 7. Пароли/хэши открытым текстом

```
tshark -r <pcap> -Y 'ftp or telnet or smtp or pop or imap' -T fields -e _ws.col.Info
```

## Выход

- `work/pcap-notes.md`;
- `work/extracted/` с вытащенными файлами / keystrokes.txt / xy-plot.png;
- кандидат-флаг через `ctf-verifier`.
