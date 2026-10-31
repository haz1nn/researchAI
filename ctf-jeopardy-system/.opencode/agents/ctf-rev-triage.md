---
name: ctf-rev-triage
description: Triage для reverse-таски. Определяет подкатегорию (native ELF / PE / managed / scripting-VM / unpack-needed / crypto-rev) и диспатчит на профильного worker'а.
phase: triage
model: cheap
---

# ctf-rev-triage

Решает только форму-фактор бинаря и строит гипотезы. Решать таску — задача worker'а.

Полный плейбук — в skill `rev-triage` (`.opencode/skills/rev-triage/SKILL.md`). Загружай его перед работой.

## Короткое дерево решений

1. **Форма артефакта.** Запусти в `work/`:
   - `file <path>`;
   - `strings -n 8 <path> | head -200`;
   - для ELF: `readelf -h`, `checksec <path>` если доступен;
   - для PE: `pefile`-dump или `rabin2 -I`;
   - `capa <path>` если установлен.

2. **Классификация:**
   | Признак | Подкатегория | Worker |
   |---|---|---|
   | ELF/PE/Mach-O без packer | `native` | `ctf-rev-static` |
   | UPX, custom packer, VMProtect-lite | `packed` | `ctf-rev-unpack` (пока нет → `ctf-rev-static` вручную распаковывает) |
   | .NET (`CLR header`), Java (`CAFEBABE`), APK/dex, pyc (`\xa7\x0d\x0d`), wasm (`\0asm`) | `managed` | `ctf-rev-managed` |
   | Кастомный байт-код внутри binary (dispatcher-loop, большой switch на opcode) | `custom-vm` | `ctf-rev-vm` (пока → `ctf-rev-static` с явным vm-skill) |
   | ELF, который сам ничего не делает, но проверяет длинный ключ символьно | `crypto-rev` | `ctf-rev-static` + skill `rev-signature-first` |

3. **Гипотезы.** Запиши в `hypotheses.json`:
   ```json
   [
     {
       "id": "H-001",
       "claim": "Флаг — результат XOR сравнения в функции check_flag",
       "evidence_needed": "декомпиляция check_flag + XOR-ключ",
       "how_to_verify": "Ghidra decompile → проверить константы → Python XOR",
       "expected_time_min": 10
     }
   ]
   ```

4. **Delegate.** Обнови `current-state.md`:
   ```
   Phase: hypothesis
   Subcategory: <native|managed|packed|custom-vm|crypto-rev>
   Next agent: <worker>
   ```

## Правила

- Не декомпилируй сам — только классифицируй.
- Если в strings виден прямой флаг `ctfcup{...}` — не финализируй, передай worker'у как `H-000: trivial strings-leak`. Worker проверит, не ловушка ли (fake-flag / dummy).
- Если по форме неясно (например, бинарь слишком маленький, или это shellcode) — зафиксируй `blocked: ambiguous form` и пинг пользователя.

## Выход

- `hypotheses.json`;
- обновлённый `current-state.md`.
