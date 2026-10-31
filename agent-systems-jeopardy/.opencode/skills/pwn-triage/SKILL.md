---
name: pwn-triage
description: Deterministic first-pass for binary exploitation (checksec, pwninit, libc identification) plus a pwntools solver template and a glibc technique matrix. Use at the start of any pwn task to classify protections and pick the technique.
---

# Pwn Triage

Детерминистический первый проход. Выбор техники зависит от защит и версии libc — определи их до написания эксплойта.

## Шаг 1 — всегда

```bash
checksec --file=<bin>        # NX, PIE, canary, RELRO, Fortify
file <bin>; rabin2 -I <bin>
strings <bin> | grep -iE 'flag|/bin/sh|system|cat'
pwninit                      # если дан libc: patchelf + скелет solve.py
seccomp-tools dump ./<bin>   # если подозрение на seccomp
```

Определи libc-версию: из `input/libc.so.6` (`strings libc.so.6 | grep 'GNU C Library'`) или через leak → libc-database/libc.rip. **Зафиксируй её** — она определяет heap-техники.

## Шаг 2 — ветвление по защитам

| Профиль | Техника |
|---|---|
| no canary, no PIE, NX, Partial RELRO, есть `main` | stack bof → ret2plt → ret2libc (easy) |
| canary + NX + PIE, нет fmt | нужен info-leak (printf, OOB read, uninit) до control |
| `printf(user)` | format string: leak → `%n`/`%hn` write (multi-stage) |
| static (musl/go/rust) | syscall ROP / ret2csu, нет libc-гаджетов |
| seccomp | ORW ROP (open/read/write флага), SROP |
| меню malloc/free/edit/show | heap → `ctf-pwn-heap` + `references/libc-matrix.md` |
| `.ko` + bzImage + initramfs | kernel pwn (эскалация): modprobe_path/core_pattern/cred |

## Шаг 3 — правила

- RIP-control только через `cyclic`/de Bruijn, вычисли точный offset.
- Гаджеты: `ropper --search 'pop rdi; ret'`, `ROPgadget`; `one_gadget libc.so.6`.
- gdb-first: перед каждым изменением payload — `vmmap` + `telescope $rsp 40`. Не угадывай layout.
- Арифметику оффсетов/символов — скриптом; выбор техники — reasoning.

## Файлы

- Шаблон solver: `templates/solve.py.tpl` — скопируй в `workspace/solve.py`.
- Heap-матрица техник по версии glibc: `references/libc-matrix.md`.
