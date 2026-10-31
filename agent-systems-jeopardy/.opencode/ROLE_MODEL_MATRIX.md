# CTF Jeopardy — Roles And Model Policy

Проверяй точные model id через `/models` в OpenCode после авторизации провайдеров. Ниже — целевая политика маршрутизации; если slug отличается, замени его в frontmatter соответствующего agent-файла.

## Принципы

- Выигрыш даёт не «умный промпт», а детерминистический **triage → router → профильный worker** с настоящим инструментом в руках (Ghidra, gdb, Volatility, sage, sigrok), а не абстрактными советами.
- Дешёвый классификатор (`ctf-category-router`) маршрутизирует, дорогие воркеры решают. Один router на таску, затем прямой dispatch в worker.
- `ctf-orchestrator` настроен как `mode: primary`: его выбирают основным агентом сессии. Он может не отображаться в списке subagents у другого primary — это нормально и не повод уходить в single-agent.

## Дефолт и сильная модель

По умолчанию стандартные роли используют `zai-coding-plan/glm-5.3` (обычно привязан к GLM Coding Plan). Reasoning-тяжёлые категории (crypto, reverse-static, pwn, pwn-heap) выигрывают от более сильной модели — они помечены как **кандидаты на bump**. Эскалация идёт на `openrouter/anthropic/claude-opus-4.7`.

Чтобы поднять модель воркера — замени `model:` в его frontmatter на сильный slug (подтверди доступность через `/models`). Рекомендованные сильные кандидаты (проверь, что доступны в аккаунте): `openrouter/anthropic/claude-opus-4.7`, `openrouter/anthropic/claude-sonnet-4.5` или аналог, доступный провайдеру.

## Лимиты по умолчанию в `budget.md`

- `Max parallel solving workers: 3`
- `Max expensive calls: 0` или явное число только для controlled escalation

## Таблица ролей

| Agent | Role | Default model | Bump? | Why |
| --- | --- | --- | --- | --- |
| `ctf-orchestrator` | State-machine, dispatch, gates, stop conditions | `zai-coding-plan/glm-5.3` | — | Стабильность рассуждения без цены Opus. |
| `ctf-category-router` | Классификация артефактов → категория + worker | `zai-coding-plan/glm-5.3` | — | Детерминистический triage, дешёвая модель. |
| `ctf-web` | Web-эксплуатация (IDOR/SSTI/SQLi/XSS/JWT/deser) | `zai-coding-plan/glm-5.3` | опц. | Много инструментального потока, умеренный reasoning. |
| `ctf-crypto` | Crypto-атаки (RSA/AES/ECC/PRNG/classical) | `zai-coding-plan/glm-5.3` | **да** | Математика и выбор атаки — сильный reasoning окупается. |
| `ctf-rev-static` | Статика: Ghidra/r2, декомпиляция, алгоритмы | `zai-coding-plan/glm-5.3` | **да** | Чтение декомпиляции и опознание алгоритмов. |
| `ctf-rev-dynamic` | Динамика: gdb/frida/qemu/strace, трассы | `zai-coding-plan/glm-5.3` | опц. | Инструментальный поток, умеренный reasoning. |
| `ctf-rev-managed` | .NET/Java/APK/pyc/wasm/Lua | `zai-coding-plan/glm-5.3` | опц. | Managed-декомпиляторы дают чистый код. |
| `ctf-pwn` | stack/ROP/ret2libc/format string + gdb-driver | `zai-coding-plan/glm-5.3` | **да** | Цепочки гаджетов и отладка под давлением. |
| `ctf-pwn-heap` | Heap: tcache/fastbin/FSOP по версии libc | `zai-coding-plan/glm-5.3` | **да** | Большой контекст how2heap + точность layout. |
| `ctf-forensics` | memory/disk/pcap/fileformat | `zai-coding-plan/glm-5.3` | опц. | Инструментальный поток (Volatility/tshark/sleuthkit). |
| `ctf-stego` | Стего image/audio | `zai-coding-plan/glm-5.3` | — | Последовательность инструментов, мало reasoning. |
| `ctf-hardware` | firmware/MCU/signal/protocol/RFID | `zai-coding-plan/glm-5.3` | опц. | Инструментальный поток + классификация. |
| `ctf-misc` | misc/osint/jail/scripting/esoteric | `zai-coding-plan/glm-5.3` | опц. | Широкий, но обычно короткий reasoning. |
| `ctf-verifier` | Валидация кандидата regex'ом, запись `flag.txt` | `zai-coding-plan/glm-5.3` | — | Узкая детерминистическая проверка. |
| `ctf-report` | Короткий writeup по state | `zai-coding-plan/glm-5.3` | — | Оформление итогов. |
| `ctf-escalation` | Дорогой арбитр тупиков и сложной логики | `openrouter/anthropic/claude-opus-4.7` | — | Только по escalation policy. |

## Escalation policy

Escalate на `ctf-escalation` только если:

- две попытки дефолтной модели упёрлись в один и тот же blocker;
- воркеры дали противоречивые выводы по одной гипотезе;
- solve/exploit работает нестабильно, но путь к флагу выглядит реалистично;
- reverse/pwn/crypto требует более сильного reasoning (кастомная VM, нетривиальная криптоатака, heap под новой libc).

Не escalate только потому, что дешёвая модель не успела закончить фазу. Сначала проверь `current-state.md`, `progress.md`, `decisions.md`, `notes.md` и причину остановки.
