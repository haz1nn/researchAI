# Jeopardy-CTF агентская система

Самостоятельная система для jeopardy-тасок на категории **reverse**, **pwn**, **forensics**, **hardware**. Веб-категория сюда не входит — она покрывается соседним web-репозиторием.

Этот файл — точка входа. Он описывает:
1. Цель и границы системы.
2. State-machine и файлы state.
3. Правила записи и валидации флага.
4. Как выбирать агентов и как они делегируют работу.
5. Что система **не делает** (чтобы не тащить A/D-логику).

## 1. Цель и границы

Единственная задача: получить флаг в формате `ctfcup{...}` (или другом, объявленном под конкретное соревнование — задаётся в `current-state.md`), сохранить его в `state/<task-slug>/flag.txt` и приложить короткий писап `report.md`.

**Что система делает:**
- принимает артефакт (бинарь, дамп, pcap, образ прошивки, архив);
- классифицирует категорию;
- маршрутизирует на профильного агента;
- извлекает флаг и пишет писап.

**Что система НЕ делает (намеренно):**
- не пишет сплойты под контракт attack-defense фермы (`shebang`, `flush`, stdout-only, kill-симуляция);
- не патчит сервисы и не делает regression;
- не ходит в S4DFarm/Gitea/жюри;
- не сдаёт флаг автоматически — флаг сдаёт человек.

Если задача внезапно оказалась web — переключись в соседний репозиторий `~/research/` (A/D web-система). Эта система web не умеет.

## 2. Входной протокол

Пользователь кладёт входные артефакты в `state/<task-slug>/input/` и запускает агента `ctf-category-router`.

Минимум в `state/<task-slug>/current-state.md`:
```
Task: <название таски и категория из CTFd, если известна>
Flag format: ctfcup\{[^}]+\}      # regex, можно переопределить
Mode: jeopardy
Phase: ingest
Category: unknown                  # заполнит router
```

`<task-slug>` — kebab-case, пример: `rev-easy-babyvm`, `pwn-house-of-force`.

## 3. State-machine

Пять фаз. Переходы — только после прохождения gate.

```
ingest → triage → hypothesis → verification → extraction → report
```

| Фаза | Что делает | Gate (критерий перехода) |
|---|---|---|
| `ingest` | `file`, `strings`, hex-dump первых 256 байт, `sha256`, запись `inventory.md` | `inventory.md` содержит для каждого файла: тип по `file`, размер, sha256, первые magic-байты. Галлюцинации категории запрещены. |
| `triage` | `ctf-category-router` ставит категорию, вызывает `ctf-<cat>-triage` для подкатегории | В `current-state.md` зафиксирована категория и подкатегория. Если router не уверен — ставит `Category: ambiguous`, фиксирует обе гипотезы в `decisions.md` и идёт параллельно. |
| `hypothesis` | профильный triage пишет 1–5 проверяемых гипотез в `hypotheses.json` | Каждая гипотеза имеет `id`, `claim`, `evidence_needed`, `how_to_verify`, `expected_time_min`. Нет «проверить вслепую». |
| `verification` | профильный worker выполняет проверку гипотез | На каждую гипотезу в `verification.md` есть одна из записей: `confirmed` + ссылка на evidence, `rejected` + причина, `blocked` + что нужно. Запрет додумывания: если прогон инструмента не был сделан, гипотеза остаётся `queued`. |
| `extraction` | worker извлекает кандидата на флаг | Кандидат прошёл `tools/flag_check.py` — regex-валидация и запись в `flag.txt`. |
| `report` | `ctf-report` пишет `report.md` | `report.md` объясняет путь к флагу в ≤10 строк: что было, что сделали, какой инструмент дал результат. |

### Файлы state

```
state/<task-slug>/
├── input/                   # неизменяемый вход (read-only после ingest)
├── work/                    # всё временное: распаковки, дампы, скрипты
├── current-state.md         # текущая фаза, категория, подкатегория
├── inventory.md             # результат ingest
├── decisions.md             # архитектурные решения, развилки, downgrade
├── hypotheses.json          # список гипотез с их статусами
├── verification.md          # что проверили и чем доказали
├── notes.md                 # вольный текстовый лог: что видели, что не вышло
├── flag.txt                 # ОДНА строка — финальный флаг
└── report.md                # короткий писап
```

Источник правды — только файлы. Разговор между агентами источником правды не является.

## 4. Правила флага

- Формат по умолчанию: `ctfcup{...}`, regex `ctfcup\{[^}]+\}` (переопределяется в `current-state.md` ключом `Flag format:`).
- Любой кандидат на флаг проходит через `tools/flag_check.py <candidate>` — если regex не матчит, кандидат отбрасывается.
- В `flag.txt` пишется **ровно одна строка — сам флаг, без префиксов, суффиксов, комментариев, пробелов**. Это важно: `cat flag.txt` должен давать готовую строку для вставки в CTFd.
- Если кандидатов несколько — пишется наиболее валидный, остальные идут в `notes.md`.
- Запрет додумывания: если флаг не был получен прогоном инструмента на реальном артефакте, он не финализируется. «Угадал по контексту» — не флаг.

## 5. Агенты

Primary — `ctf-category-router`. Он вызывает профильный triage, тот — профильного worker'а.

### Текущий состав

| Агент | Фаза | Назначение |
|---|---|---|
| `ctf-category-router` | triage | классификация + диспатч |
| `ctf-rev-triage` | triage | подкатегория reverse |
| `ctf-pwn-triage` | triage | подкатегория pwn |
| `ctf-forensics-triage` | triage | подкатегория forensics |
| `ctf-hw-triage` | triage | подкатегория hardware |
| `ctf-rev-static` | verification/extraction | статический реверс через Ghidra/r2 |
| `ctf-rev-managed` | verification/extraction | .NET / Java / APK / pyc / wasm |
| `ctf-pwn-gdb-driver` | verification/extraction | gdb-as-tool по паттерну Project Naptime |
| `ctf-forensics-stego-img` | verification/extraction | стего в изображениях |
| `ctf-forensics-pcap` | verification/extraction | pcap/pcapng анализ |
| `ctf-hw-firmware` | verification/extraction | binwalk/unblob + MCU-реверс |
| `ctf-verifier` | extraction | regex-валидация флага и запись `flag.txt` |
| `ctf-report` | report | писап |

### Как подключать новых воркеров

Паттерн — тонкий агент + толстый skill:
- агент (`.opencode/agents/*.md`) — короткий, ≤120 строк, описывает роль, входы/выходы, обязательные шаги;
- skill (`.opencode/skills/<name>/SKILL.md`) — толстый плейбук с конкретными командами, decision-tree, ссылками на инструменты.

Новый worker (например, `ctf-pwn-heap`, `ctf-rev-vm`, `ctf-hw-signal`, `ctf-forensics-memory`) добавляется:
1. агент в `.opencode/agents/` со ссылкой на свой skill;
2. соответствующий skill;
3. изменение `ctf-<cat>-triage` — добавить ветку в decision-tree.

Список целевых воркеров к постепенному добавлению см. в `docs/ROADMAP.md`.

## 6. Промпт-паттерны (единые для всех агентов)

1. **Classify-then-dispatch.** Запрет угадывать категорию без `file` + hex + magic. Это снижает галлюцинации сильнее любого «умного промпта».
2. **Signature-first для reverse.** Вместо «explain this code» → «in ≤5 bullets: inputs, outputs, side effects, likely name, suspected algorithm (XOR / RC4 / TEA / AES / CRC32 / FNV / custom)».
3. **Константы как якорь.** До анализа — grep по магикам: TEA `0x9E3779B9`, MD5 init `0x67452301`, AES S-box `0x637c777b`, zlib magic `0x789C/0x78DA`.
4. **gdb-first для pwn.** Запрет менять payload без свежего `vmmap` + `telescope`. Паттерн Project Naptime.
5. **Bins ASCII.** Для heap-тасок рисовать bins state до и после каждой операции.
6. **Rename-loop для Ghidra.** Два прохода декомпиляции: первый — предложить имена, применить; второй — уже с чистыми именами.
7. **Flag-regex validation.** Любой кандидат — через `tools/flag_check.py`.
8. **Запрет додумывания** для forensics/hw: не описывать содержимое дампа, если инструмент не был запущен.

## 7. Инструментарий

Канонические URL инструментов и MCP-серверов — в `docs/TOOLS.md` (верифицировано WebFetch, последняя сверка — см. дату в файле).

Критичные:
- **GhidraMCP** (LaurieWired) — MCP-сервер поверх Ghidra, для `ctf-rev-static`;
- **r2 + r2ai** — быстрый alt-канал статического реверса;
- **pwndbg** или **GEF (hugsy)** — для `ctf-pwn-gdb-driver`;
- **Volatility3** — memory forensics;
- **binwalk (Rust)** и **unblob** — распаковка прошивок;
- **URH**, **sigrok-cli**, **rtl_433** — сигнальная часть hw;
- **SVD-Loader-Ghidra** — критичен для MCU-реверса.

## 8. Автономность

Не спрашивай подтверждение на:
- чтение входных артефактов,
- запуск `file`/`strings`/`binwalk`/`volatility`/`r2`/`gdb` локально,
- скачивание недостающих CLI-инструментов через стандартный пакетный менеджер,
- запись в `state/<task-slug>/` в пределах этой системы,
- локальное исполнение бинаря в изолированной среде, если артефакт пришёл из CTFd.

Останавливайся и спрашивай пользователя, если:
- артефакт требует подключения к внешнему сервису (CTFd nc, remote exploit) — показать команду и дать подтвердить;
- нужно установить тяжёлые инструменты (Ghidra, qemu-system-full), которых нет в системе;
- таска вне разрешённого scope CTF;
- gate заблокирован и нет безопасного следующего шага.

## 9. Правило останова

Если инструмент (gdb, qemu-process, docker-container) падает — не делать слип, пинговать пользователя.
