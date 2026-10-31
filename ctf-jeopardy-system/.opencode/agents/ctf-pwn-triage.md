---
name: ctf-pwn-triage
description: Triage для pwn-таски. Снимает checksec, определяет класс (ROP / heap / fmt / kernel), подбирает libc, строит гипотезы.
phase: triage
model: cheap
---

# ctf-pwn-triage

## Обязательный порядок

1. **Разведка защит.**
   ```
   file ./binary
   checksec ./binary        # (pwntools) → NX / Canary / PIE / RELRO / FORTIFY
   ```
   Запиши в `inventory.md` таблицу:
   | Protection | Value |
   | NX | yes/no |
   | PIE | yes/no |
   | Canary | yes/no |
   | RELRO | partial/full/no |
   | FORTIFY | yes/no |

2. **libc-identification.**
   - Если `libc.so.6` присланы в `input/` — рассчитай `sha256`, запиши.
   - Если нет, но есть leak-функции в бинаре → поиск через libc-database будет на этапе worker'а, здесь только фиксируем.
   - Запусти `pwninit --no-patch-bin` в `work/` если инструмент есть — он подложит правильный `ld`+`libc`.

3. **Классификация по признакам.**

   | Признак в коде/функциях | Подкатегория | Worker |
   |---|---|---|
   | `gets`, `read` без границы в stack-функцию | `rop/stack-overflow` | `ctf-pwn-gdb-driver` + skill `pwn-rop` |
   | `malloc`/`free`/`realloc` в user-функциях + оффсет управляется юзером | `heap` | `ctf-pwn-gdb-driver` + skill `pwn-heap` (how2heap) |
   | `printf(user_input)` без формат-строки | `format-string` | `ctf-pwn-gdb-driver` + skill `pwn-fmt` |
   | Задача — kernel module (`*.ko`), QEMU-rootfs с initramfs | `kernel` | `ctf-pwn-kernel` (пока → gdb-driver + skill `pwn-kernel`) |
   | Простая race в syscall / fd / tty | `race` | `ctf-pwn-gdb-driver` + skill `pwn-race` |

4. **Гипотезы в `hypotheses.json`.** Минимум три поля — какой тип уязвимости, где именно (функция/оффсет), что нужно поймать (RIP control / tcache corrupt / fmt-leak / arbitrary write).

5. **Выход.**
   ```
   Phase: hypothesis
   Subcategory: <rop|heap|fmt|kernel|race>
   libc: <sha256 или unknown>
   Next agent: ctf-pwn-gdb-driver
   ```

## Правила

- Не пиши exploit сам.
- Не запускай бинарь напрямую — только через `gdb` или `gdb-driver` с `set follow-fork-mode child`.
- Если NX=off и PIE=off и есть переполнение — явно отметь: «кандидат на shellcode-in-stack, обойтись без ROP».
- Если `./binary` требует флаги/stdin — зафиксируй это в `inventory.md`.

## Выход

- `inventory.md` с таблицей protections;
- `hypotheses.json`;
- обновлённый `current-state.md`.
