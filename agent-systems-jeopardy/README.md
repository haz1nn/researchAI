# CTF Jeopardy Agent System

Многоагентная система для решения задач CTF формата **Jeopardy** на базе OpenCode. Цель — получить флаг (`ctfcup{...}` по умолчанию) по выданной таске и зафиксировать воспроизводимый путь к нему.

Это адаптация attack/defense-системы под jeopardy: убраны ферма (S4DFarm/`start_sploit.py`), farm-контракт эксплойтов, патчинг своих сервисов и regression. Оставлены и усилены фазы поиска флага, добавлена маршрутизация по категориям и профильные воркеры.

## Архитектура

Детерминистический конвейер: **один дешёвый классификатор → профильный worker с реальным инструментом**.

```
ingest → triage → hypothesis → solving → extraction → report
```

- `ctf-orchestrator` (primary) держит state-machine, проверяет gates, диспатчит воркеров, доводит до `flag.txt` + `report.md`.
- `ctf-category-router` классифицирует артефакты (`file`/magic/strings/entropy) → категория + worker. Самая важная фаза.
- Профильные воркеры решают инструментами; `ctf-verifier` валидирует флаг regex'ом и пишет `flag.txt`; `ctf-report` собирает writeup; `ctf-escalation` — дорогой арбитр тупиков.

### Агенты (`.opencode/agents/`)

| Агент | Категория |
|---|---|
| `ctf-orchestrator` | primary, state-machine |
| `ctf-category-router` | triage / классификация |
| `ctf-web` | web (IDOR/SSTI/SQLi/XSS/JWT/deser) |
| `ctf-crypto` | crypto (RSA/AES/ECC/PRNG/classical) |
| `ctf-rev-static` | reverse: статика (Ghidra/r2) |
| `ctf-rev-dynamic` | reverse: динамика (gdb/frida/qemu/angr) |
| `ctf-rev-managed` | reverse: .NET/Java/APK/pyc/wasm/lua |
| `ctf-pwn` | pwn: stack/ROP/ret2libc/fmt |
| `ctf-pwn-heap` | pwn: heap (tcache/fastbin/FSOP) |
| `ctf-forensics` | forensics: memory/disk/pcap/fileformat |
| `ctf-stego` | forensics: стего image/audio |
| `ctf-hardware` | hardware: firmware/MCU/signal/protocol/RFID |
| `ctf-misc` | misc/osint/jail/scripting/esoteric |
| `ctf-verifier` | валидация флага, запись `flag.txt` |
| `ctf-report` | writeup |
| `ctf-escalation` | дорогой арбитр (opus) |

### Skills (`.opencode/skills/`)

- `flag-hunter` — grep/strings + рекурсивный декодер обёрток (`scripts/flaghunt.py`).
- `crypto-attacks` — каталог криптоатак + чеклист опознания.
- `rev-triage` — decision tree по формату бинаря.
- `pwn-triage` — checksec/pwninit/libc + `templates/solve.py.tpl` + `references/libc-matrix.md`.
- `forensics-triage` — 60-сек dispatch по магик-байтам.
- `stego` — проверенные последовательности image/audio.
- `hw-triage` — классификация артефакта + decoder-matrix.
- `security-review`, `web-pentest-sample` — переиспользуются `ctf-web`.

### Tools (`tools/`)

- `validate_flag.py` — проверка кандидата по regex (используется `ctf-verifier`).

## Использование

1. Выбери `ctf-orchestrator` основным агентом сессии OpenCode (в каталоге системы).
2. Создай каталог таски:
   ```bash
   cp -r state-template state/<task-slug>
   mkdir -p state/<task-slug>/{input,workspace,work-items}
   # положи артефакты таски в state/<task-slug>/input/
   ```
3. Заполни в `state/<task-slug>/current-state.md` `Allowed targets` (URL/host:port/файлы) и `Flag format`, если он не `ctfcup{...}`.
4. Поставь задачу: «реши таску `state/<task-slug>`, достань флаг». Orchestrator пройдёт фазы сам.
5. Результат: флаг в `state/<task-slug>/flag.txt`, writeup в `report.md`.

## Модели

Дефолт — `zai-coding-plan/glm-5.3`, эскалация — `openrouter/anthropic/claude-opus-4.7`. Reasoning-тяжёлые воркеры (`crypto`, `rev-static`, `pwn`, `pwn-heap`) помечены как кандидаты на сильную модель. Политика — в `.opencode/ROLE_MODEL_MATRIX.md`. Проверь точные slug'и через `/models`.

## Ключевые правила

- Классификация только после прогона инструмента — не угадывай категорию.
- Флаг валиден только если матчит regex; финализирует только `ctf-verifier`.
- `input/` read-only после ingest; эксперименты — в `workspace/`.
- Если стенд/endpoint/инструмент упал — **не sleep**, пинг пользователю.
