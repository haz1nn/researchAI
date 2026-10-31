# State template

Скопируй этот каталог в `state/<task-slug>/` при старте новой таски:

```bash
cp -r state-template state/<task-slug>
mkdir -p state/<task-slug>/{input,workspace,work-items}
```

Файлы:

- `current-state.md` — фаза, категория, разрешённые цели, формат флага, следующий шаг.
- `inventory.md` — входные файлы и их типы, endpoint, что дано в условии.
- `triage.md` — классификация: категория/подкатегория, confidence, выбранный worker.
- `hypotheses.json` — проверяемые гипотезы (`unverified`/`testing`/`confirmed`/`rejected`/`blocked`).
- `notes.md` — рабочие заметки, команды, evidence, кандидаты на флаг.
- `decisions.md` — важные решения, отвергнутые гипотезы, false positives.
- `progress.md` — журнал действий для продолжения после обрыва контекста.
- `flag.txt` — финальный флаг (пишет только `ctf-verifier`).
- `report.md` — итоговый writeup (пишет `ctf-report`).
- `input/` — входные артефакты (read-only после ingest).
- `workspace/` — скретч: распаковка, solve-скрипты, дампы.
- `work-items/H-XXX/` — изолированные задачи для параллельной работы.
