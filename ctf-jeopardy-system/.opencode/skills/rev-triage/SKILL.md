# skill: rev-triage

Decision tree для первой минуты работы с reverse-таской.

## Шаг 0. Прямой strings-leak

```
rg -oP 'ctfcup\{[^}]+\}' -a <bin>
```

Если нашлось — передай worker'у как `H-000: trivial strings-leak`. Worker обязан проверить, не fake-flag:
- флаг рядом с другим флагом → один из них ложный;
- `ctfcup{this_is_not_the_flag}` → явный fake;
- флаг в секции `.rodata` без ссылок на него из кода → подозрительно, запусти `rabin2 -X <bin>` для xref.

## Шаг 1. Форма артефакта

```
file <bin>
rabin2 -I <bin>      # format info
rabin2 -i <bin>      # imports
rabin2 -z <bin>      # strings из data-секций
```

## Шаг 2. Матрица форма → ветка

| Форма (из `file`/`rabin2 -I`) | Ветка |
|---|---|
| ELF 32/64, PE32[+], Mach-O, нет упаковки | `native` → `ctf-rev-static` |
| ELF/PE с entry выше нормального, странная секция, маленький IAT | `packed` |
| `.NET assembly`, magic `BSJB` | `managed-dotnet` → `ctf-rev-managed` |
| `Zip archive data` + `AndroidManifest.xml` | `managed-apk` → `ctf-rev-managed` |
| Начинается с `CAFEBABE` | `managed-java` → `ctf-rev-managed` |
| `python 3.X byte-compiled` | `managed-pyc` → `ctf-rev-managed` |
| Magic `\0asm` | `managed-wasm` → `ctf-rev-managed` |
| Magic `\x1BLua` | `managed-lua` → `ctf-rev-managed` |
| ELF маленький (<10KB), в коде один большой switch 50+ cases | `custom-vm` |
| ELF, в котором `main` только сравнивает длинный ключ с константой | `crypto-rev` |

## Шаг 3. Распаковка

| Signature | Способ |
|---|---|
| `UPX!` в заголовке | `upx -d <bin>` |
| Нет UPX, но entry в редкой секции, импорты только `LoadLibraryA/GetProcAddress` | custom packer — ветка `packed`, нужен ручной dump unpacked image (x64dbg + Scylla, или r2 с `aei` + `aesu`) |
| VMProtect-lite | ветка `custom-vm` — часто проще реверс VM, чем прямое снятие packer |

## Шаг 4. Capa auto-triage

```
capa <bin> -v > work/capa.txt
```

Capa проставит теги вроде `encrypt data using XOR`, `decode data using Base64`, `check for stack cookie`, `communicate over HTTP`. Это ровно те подсказки, которые экономят час декомпиляции.

## Шаг 5. Константы-якоря

```
# Крипто-магики
rabin2 -zz <bin> | grep -iE '(aes|des|rc4|xor|xtea|chacha|salsa)'

# Hex-магики: TEA/XTEA delta, MD5/SHA init, AES S-box первые 4 байта
# TEA/XTEA delta
rabin2 -s <bin> | grep -c '9e3779b9'
# AES S-box
python3 -c "d=open('<bin>','rb').read(); print(b'\\x63\\x7c\\x77\\x7b' in d)"
# zlib
python3 -c "d=open('<bin>','rb').read(); print(b'\\x78\\x9c' in d, b'\\x78\\xda' in d)"
```

Любой матч — явно впиши в `hypotheses.json`.

## Шаг 6. Диспатч

Запиши в `current-state.md`:
```
Subcategory: <native|packed|managed-*|custom-vm|crypto-rev>
Next agent: <worker>
```

И составь 1–5 гипотез в `hypotheses.json`. Для `native` + `crypto-rev` стандартный набор:
- H-001: прямой strings-leak (если на шаге 0 было подозрение);
- H-002: сравнение в `check*` функции с константой → реверсивное решение;
- H-003: кастомная крипто-функция, идентифицированная по константам.
