---
name: crypto-attacks
description: Catalog of CTF cryptography attacks and an identification checklist. Use for RSA, AES block-mode, stream/PRNG, (EC)DSA, hash and classical-cipher challenges to pick the correct attack instead of guessing.
---

# Crypto Attacks

Каталог атак и чеклист опознания. Сначала **прочитай challenge-скрипт целиком**: какие примитивы, где утечка, что подаёт oracle, что именно восстанавливать. Не угадывай — считай.

## RSA

| Условие | Атака |
|---|---|
| `e=3` (или малый), короткое сообщение | кубический корень из `c` (нет модуля при `m^e < n`) |
| одно `m` под несколькими `(n_i, e=3)` | Håstad broadcast (CRT + корень) |
| общий модуль `n`, разные `e1,e2`, `gcd(e1,e2)=1` | common modulus (Bézout) |
| два модуля с общим фактором | `gcd(n1,n2)` → p |
| `p,q` близки | Fermat factorization |
| очень малый `d` | Wiener (continued fractions); Boneh-Durfee для `d < n^0.292` |
| известны старшие биты `p` или часть `m` | Coppersmith / stereotyped (sage `small_roots`) |
| `n` маленький / известный | factordb, `yafu`, `cado-nfs` |
| утечка `dp`,`dq` | восстановление d / частичный CRT-leak |

Инструменты: `RsaCtfTool`, `gmpy2`, `sympy`, sage.

## AES / блочные режимы

- **ECB**: одинаковые 16-байтовые блоки шифртекста при одинаковом открытом → детект. Byte-at-a-time decryption (если дописывают наш ввод перед секретом), cut-and-paste.
- **CBC padding oracle**: сервер отличает валидный padding → decrypt целиком побайтно. Инструмент: `padbuster`-логика / свой скрипт.
- **CBC bit-flipping**: управляемая порча предыдущего блока меняет расшифровку следующего (обход admin=0→1).
- **IV = key** / фиксированный IV — отдельные классы.
- **CTR/GCM reused nonce**: `C1 ^ C2 = P1 ^ P2` → восстановление по known-plaintext/crib-drag. Для GCM reused nonce — forbidden attack (восстановление H → подделка тега).

## Поток / PRNG

- Reused keystream (OTP/stream): XOR двух шифртекстов, crib-dragging.
- **Mersenne Twister**: 624 последовательных 32-бит выхода → клонирование состояния (`randcrack`).
- **LCG**: восстановление `a,c,m` по нескольким выходам (разности + gcd).

## (EC)DSA

- Reused `k` в двух подписях → восстановление приватного ключа.
- Biased/partial `k` (несколько бит) → lattice (HNP, `lattice`/`sage`).
- Невалидная кривая / малый порядок точки → восстановление скаляра (Pohlig-Hellman).

## Хеши

- Length extension для `H(secret || msg)` (MD5/SHA1/SHA256) → `hashpump`/`hashpumpy`.
- Усечённый/слабый хеш → brute (`hashcat`/`john`), rainbow.
- Коллизии (MD5 chosen-prefix) — редко в jeopardy, но бывает.

## Классика

- Частотный анализ (substitution/Caesar), Kasiski/индекс совпадений (Vigenère), single-byte XOR (брут 256), railfence/transposition. Обёртки base/rot — через skill `flag-hunter`.

## Общий порядок

1. Идентифицируй примитив и параметры (распарси вход).
2. Сопоставь с таблицей → выбери атаку.
3. Напиши `workspace/solve.py` (или `.sage`), печатающий флаг детерминистически.
4. Для remote-oracle — `pwntools`, короткие таймауты, устойчивость к обрыву.
5. Проверь результат regex'ом, кандидата — в `notes.md`.
