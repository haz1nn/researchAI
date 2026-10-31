# skill: pwn-heap

Heap — отдельная вселенная. Используй вместе со skill `pwn-libc-matrix`.

## Железные правила

1. **Bins ASCII до и после каждой операции.** Да, рисуешь прямо в `verification.md`:
   ```
   tcache[0x20]: head -> A -> B
   fastbin[0x20]: empty
   unsorted:     empty
   ```
   Если не рисуешь — на 3-й операции потеряешься.

2. **Всегда `telescope &chunk` после каждого `malloc/free`.** Это одноразовый ход, но дешевле, чем 20 минут гадать.

3. **Не писать эксплойт, пока нет leak heap base.** На 2.32+ с safe-linking tcache-указатели шифруются `((heap_base >> 12) ^ fd)`. Без heap base ты не сможешь посчитать подделку.

## Матрица техник по версии libc

См. `pwn-libc-matrix`. Короткая выжимка:

- **≤ 2.25:** fastbin dup, House of Spirit, unsorted-bin-attack, FSOP, `__free_hook`.
- **2.26 – 2.31:** tcache poisoning (мощнейший trick: `malloc(sz); malloc(sz); free(A); free(A);` → tcache dup).
- **2.32+:** tcache poisoning + safe-link reveal (`fd ^ (heap_base >> 12)`); `__free_hook` ещё есть до 2.33.
- **2.34+:** `__free_hook` **умер**. Переключаемся на `house-of-apple-2`, `_IO_file_jumps`, `__exit_funcs`.

## Шаблон tcache poisoning (2.26 — 2.33)

```python
# 1. Освободи дважды одну и ту же chunk — tcache dup
free(A)
free(A)
# 2. Выдели столько же, запиши target в fd
B = malloc(sz)
write(B, p64(TARGET))        # 2.32+: p64(TARGET ^ (heap_base >> 12))
# 3. Два последовательных malloc — второй возвращает TARGET
malloc(sz)                   # дубль из tcache
X = malloc(sz)               # вот это TARGET
write(X, payload)
```

TARGET-кандидаты по версии:
- 2.26–2.33: `__free_hook`, `__malloc_hook`;
- 2.32+ (без hooks): `_IO_2_1_stdout_` + house-of-apple-2;
- Любая: подмена структуры в `.bss` программы (если symbol экспортирован).

## house-of-apple-2 (краткое напоминание)

Нужны: write-what-where на `_IO_FILE_plus`, leak libc, leak heap, возможность вызвать `exit` или `_IO_flush_all_lockp`.

Shape:
```c
fp->vtable = &_IO_wfile_jumps;
fp->_wide_data = &fake_wide_data;    // _wide_data pointing to fake vtable
fake_wide_data._wide_vtable->__doallocate = system
fp->_lock = pointer-to-writable-zero
```

Трансляция в payload — через pwntools-helper `pwntools-FileStructure` в pwntools 4.11+.

## Правила

- Не используй `pwndbg heap`'s автодекод вместо реального понимания. Он врёт на corrupt'нутых chunk'ах.
- Для race-условий в heap (конкурентные threads) — отдельная ветка; обычно не нужна в jeopardy.
- how2heap (https://github.com/shellphish/how2heap) — reference-реализации по версии libc. Открой нужный примерами перед написанием solve'а.
