# ctf-jeopardy-system

Отдельная агентская система под jeopardy-CTF. Категории: **reverse**, **pwn**, **forensics**, **hardware**. Web не входит — для него другой репозиторий.

Точка входа — [AGENTS.md](AGENTS.md). Запуск начинается с `ctf-category-router`.

## Запуск одной таски

```
# 1. Создать state для таски
mkdir -p state/babyrev/{input,work}
cp state-template/current-state.md state/babyrev/current-state.md
cp state-template/hypotheses.json  state/babyrev/hypotheses.json

# 2. Положить артефакты
cp ~/Downloads/babyrev.elf state/babyrev/input/

# 3. Запустить router
#   (в OpenCode выбрать primary agent "ctf-category-router", передать путь state/babyrev/)
```

## Структура репозитория

```
ctf-jeopardy-system/
├── AGENTS.md                       # главная спецификация
├── README.md                       # этот файл
├── .opencode/
│   ├── agents/                     # агенты системы (12 штук)
│   │   ├── ctf-category-router.md
│   │   ├── ctf-rev-triage.md
│   │   ├── ctf-pwn-triage.md
│   │   ├── ctf-forensics-triage.md
│   │   ├── ctf-hw-triage.md
│   │   ├── ctf-rev-static.md
│   │   ├── ctf-rev-managed.md
│   │   ├── ctf-pwn-gdb-driver.md
│   │   ├── ctf-forensics-stego-img.md
│   │   ├── ctf-forensics-pcap.md
│   │   ├── ctf-hw-firmware.md
│   │   ├── ctf-verifier.md
│   │   └── ctf-report.md
│   └── skills/                     # переиспользуемые плейбуки
│       ├── flag-hunter/
│       ├── forensics-triage/
│       ├── rev-triage/
│       ├── pwn-rop/
│       ├── pwn-heap/
│       ├── pwn-fmt/
│       ├── pwn-libc-matrix/
│       ├── stego-image/
│       ├── pcap-triage/
│       ├── hw-protocols/
│       └── hw-mcu-reversing/
├── state-template/                 # шаблон state/<slug>/
├── docs/
│   ├── TOOLS.md                    # верифицированный инструментарий
│   └── ROADMAP.md                  # что добавить после MVP
├── tools/
│   └── flag_check.py               # regex-валидатор флага
└── state/                          # (создаётся при работе) рабочие state'ы по таскам
```

## Чем отличается от A/D-системы

| Аспект | A/D (соседний репо) | jeopardy (этот) |
|---|---|---|
| Цель | Удержать свои флаги + красть чужие | Получить флаг |
| Выход | `exploit.py` для фермы | `flag.txt` + `report.md` |
| Фазы | ingest → recon → … → patching → regression → report | ingest → triage → hypothesis → verification → extraction → report |
| Строгие контракты | shebang + `flush`, kill-симуляция, stdout-only | regex-валидация флага, одна строка в `flag.txt` |
| Параллельность | work-items, farm concurrency | опциональная, по гипотезам |
| Web | да, основной фокус | нет |

## Статус

MVP готов — покрывает большинство easy/medium jeopardy-тасок во всех четырёх категориях. Расширение — по мере встречающихся задач, см. [docs/ROADMAP.md](docs/ROADMAP.md).
