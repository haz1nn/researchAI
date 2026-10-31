# skill: pwn-libc-matrix

Матрица «версия libc → доступные heap-техники». После libc-identification смотри сюда — не трать время на технику, зарезанную в этой версии.

## Как определить libc

1. Если `libc.so.6` присланы: `strings libc.so.6 | grep "GNU C Library"`.
2. Если leak-функция в бинаре → leak одной GOT-записи (обычно `puts` или `read`) → поиск в libc-database:
   ```
   # Local libc-database (https://github.com/niklasb/libc-database)
   ./find puts <leaked_addr_last_12_bits>
   # Online: libc.rip, libc.blukat.me
   ```

## Матрица техник

| Версия glibc | tcache | safe-linking | hook disabling | Что работает |
|---|---|---|---|---|
| ≤ 2.25 | нет | нет | hooks живы | fastbin dup, unsorted bin attack, House of Spirit, FSOP (file stream exploit через `_IO_FILE`), `__free_hook`/`__malloc_hook` |
| 2.26 – 2.28 | **да** | нет | hooks живы | tcache dup, tcache poisoning, double free; из FSOP ещё работает старый `vtable overwrite` |
| 2.29 – 2.31 | да | нет | hooks живы | tcache + safe-link tcache (CVE-2017), FSOP через `_IO_str_jumps` или house-of-apple variants |
| 2.32 – 2.33 | да | **да (CVE-mitigation)** | hooks живы | tcache + protect-ptr/reveal-ptr обход (нужен leak heap base) |
| 2.34+ | да | да | **hooks удалены** | `__free_hook`/`__malloc_hook` **НЕ существуют** — остаются house-of-apple-{1,2}, `_IO_file_jumps` → `exit`, `__exit_funcs` corruption, FSOP, `environ` leak для stack-pivot |
| 2.35+ | да | да | hooks удалены | то же + отдельные CVE на `strftime`/`setlocale` в контексте вызова `__run_exit_handlers` |

## Правила

- Нет точного `glibc X.YY` → не выбирай технику. Сделай сначала leak + identify.
- Если версия ≥ 2.34 и в коде `__free_hook` — это сразу `rejected`. Переключайся на house-of-apple или `__exit_funcs`.
- Для `__exit_funcs` поверх 2.34+ нужен write-what-where внутри `.data` libc. Запомни: `__exit_funcs` защищён `PTR_MANGLE`, обход — через leak одной из уже-зарегистрированных функций и XOR'ом по cookie.

## one_gadget

Для любой libc, где ты получил base-leak:
```
one_gadget ./libc.so.6
```

Условия (constraints) — проверяй по текущему стеку: `rsp+0x30==NULL`, `rsp+0x40==NULL` и т.п. Если ни один не удовлетворяется — классический `ret2libc` на `system("/bin/sh")` с выравниванием стека.

## FSOP cheat-sheet

- 2.23–2.27: `_IO_FILE_plus` → overwrite `vtable` → управление через `_IO_jump_t`.
- 2.28+: vtable проверяется на bounds — нужно использовать уже существующие таблицы (`_IO_str_jumps`, `_IO_wstrn_jumps`).
- 2.32+ (safe-link): дополнительно шифруются указатели в tcache — обойти через leak heap base.
