# state-template

Шаблон содержимого `state/<task-slug>/`.

## Как использовать

```
mkdir -p state/<task-slug>/{input,work}
cp state-template/current-state.md state/<task-slug>/current-state.md
cp state-template/hypotheses.json state/<task-slug>/hypotheses.json
# положить артефакты в state/<task-slug>/input/
# запустить ctf-category-router с аргументом state/<task-slug>/
```

## Структура

```
state/<task-slug>/
├── input/              # read-only после ingest
├── work/               # всё временное
├── current-state.md    # текущая фаза
├── inventory.md        # результат ingest
├── decisions.md        # развилки и причины выбора
├── hypotheses.json     # список гипотез
├── verification.md     # результаты verification
├── notes.md            # вольный лог
├── flag.txt            # пишет только ctf-verifier
└── report.md           # пишет ctf-report
```
