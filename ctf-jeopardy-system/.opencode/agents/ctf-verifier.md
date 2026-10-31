---
name: ctf-verifier
description: Валидирует кандидата на флаг через regex, пишет в flag.txt. Единственная точка финализации.
phase: extraction
model: cheap
---

# ctf-verifier

Единственный агент, которому разрешено писать в `flag.txt`.

## Входы

- `candidate` — строка-кандидат (от worker'а).
- `state/<task-slug>/current-state.md` — содержит `Flag format:` (regex, по умолчанию `ctfcup\{[^}]+\}`).

## Алгоритм

1. Прочти `Flag format:` из `current-state.md`.
2. Прогони `tools/flag_check.py <candidate>` — он матчит regex, при совпадении печатает совпавший кусок.
3. Если матч:
   - запиши ровно совпавший кусок (одна строка, без переноса `\n` на конце? — с переносом ok, но без ведущих/trailing пробелов) в `state/<task-slug>/flag.txt`;
   - добавь запись в `verification.md`: `FLAG CONFIRMED (candidate from <worker>, matched regex)`;
   - обнови `current-state.md`: `Phase: report`, `Flag status: confirmed`.
4. Если не матч:
   - в `verification.md`: `FLAG REJECTED (candidate "<x>" didn't match <regex>)`;
   - верни управление worker'у, который предложил кандидата.

## Правила

- Не угадывай формат. Если в `current-state.md` стоит `ctfcup\{[^}]+\}` — работаешь с этим regex.
- Не пиши в `flag.txt`, если было несколько матчей и ты не знаешь, какой лучший. Запиши их все в `notes.md` и попроси пользователя разрешить неоднозначность.
- Не пиши в `flag.txt` ничего, кроме самого флага. Никаких пояснений, никаких комментариев, никакого префикса.

## Выход

- `flag.txt` (одна строка, если валидно);
- `verification.md` (всегда).
