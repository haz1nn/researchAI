# glibc heap technique matrix

Определи точную версию glibc **перед** выбором техники. Это главный фактор.

| glibc | Ключевые факты | Доступные техники |
|---|---|---|
| 2.23–2.26 | нет tcache; `__malloc_hook`/`__free_hook` есть | fastbin dup, unsorted bin attack, House of Spirit/Einherjar/Force, hook overwrite |
| 2.27 | введён tcache, без double-free счётчика | tcache dup (double-free), tcache poisoning, fastbin dup |
| 2.28–2.30 | tcache без key-защиты | tcache poisoning → `__free_hook` = system |
| 2.31 | tcache key добавлен ранее (2.29) | tcache poisoning, нужен контроль размера; `__free_hook` ещё есть |
| 2.32–2.33 | **safe-linking**: fd маскируется `(addr>>12) ^ ptr` | нужен **heap-leak** для демаскировки; обход через key-corruption для double-free |
| 2.34 | `__malloc_hook`/`__free_hook`/`__realloc_hook` **удалены** | **FSOP**: `_IO_2_1_stdout_`, House of Apple2, House of Cat; `__exit_funcs`/tls-dtor; ROP через environ-leak |
| 2.35+ | то же + усиления | House of Apple2/Cat (wide stdout vtable), `_IO_wfile_jumps`, pointer guard для tls-dtor |

## Опорные примитивы

- **UAF** → tcache poisoning (запись fd освобождённого chunk → выдать произвольный адрес).
- **double-free** → tcache dup (≤2.33 через key-bypass), fastbin dup (≤2.26 / fastbin-size).
- **off-by-one / null-byte** → chunk overlap через подмену size, consolidate.
- **heap overflow** → затереть size соседа → unsorted/largebin attack или overlap.

## Leak'и

- libc base: освободить chunk в unsorted bin → `show` → main_arena offset.
- heap base: нужен для safe-linking (2.32+) — leak любого heap-указателя.

## Поток управления

- ≤2.33: перезаписать `__free_hook`/`__malloc_hook` = `system`/one_gadget, затем `free("/bin/sh")`.
- ≥2.34: FSOP — подделать `_IO_2_1_stdout_`/FILE vtable (House of Apple2), сработает на `exit`/`puts`/буферизации; либо ROP через stack-leak.
- seccomp → ORW-цепочка вместо `system`.
