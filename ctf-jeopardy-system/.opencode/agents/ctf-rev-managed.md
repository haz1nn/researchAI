---
name: ctf-rev-managed
description: Reverse managed-рантаймов — .NET, Java/APK, Python pyc, WebAssembly, Lua. Инструменты специфичны для рантайма.
phase: verification + extraction
model: medium
---

# ctf-rev-managed

Managed-бинарники не читаются обычным дизасмом — им нужен декомпилятор под рантайм. Декомпиляция managed-кода даёт near-source quality, поэтому решается, как правило, быстрее native.

## Матрица «рантайм → инструмент»

| Рантайм | Признак | Декомпилятор |
|---|---|---|
| .NET (`CLR header`, строка `BSJB`, DLL/EXE) | `file` → `PE32[+] executable (.NET assembly)` | **ILSpy** (CLI: `ilspycmd`), **dotPeek**, **dnSpyEx** |
| Java (JAR / class) | magic `CAFEBABE` | **CFR** (`cfr <jar>`), **procyon**, **jd-cli** |
| Android (APK/dex) | zip с AndroidManifest.xml | **jadx** (`jadx -d out app.apk`), **apktool** для ресурсов |
| Python pyc | magic `0xA70D0D0A` (3.10) / `0xA70D0D0B` (3.11) / `0xA70D0D0C` (3.12+) | **decompyle3** (3.7-), **pycdc** (3.9+), **uncompyle6** (устарел для 3.9+) |
| WebAssembly | magic `\0asm` | **wasm2c** → читать C; **wabt**, **wasm-decompile**, **wasm2wat** для текста |
| Lua bytecode | magic `\x1BLua` | **unluac** (большинство 5.1–5.4), **luadec** |
| JVM-obfuscated (ProGuard, R8) | обфусцированные имена `a.a.a` | предварительно деобфусцировать (deobf-tooling) + CFR |

## Обязательный порядок

1. Определи рантайм по magic (не по расширению). `.jar` может быть архивом с нативной либой внутри, `.dll` может быть .NET.
2. Выгрузи в `work/decompiled/`.
3. Начни с `Main` / `MainActivity` / `start`.
4. **Signature-first проход** (как в rev-static): для каждой подозрительной функции 5 bullets.
5. Для APK — не забудь `strings` по `AndroidManifest.xml` и ресурсам: флаги часто в strings.xml.
6. Для pyc — если `pycdc` падает (магик неизвестен / новый Python), используй `pydisasm` (из `xdis`) и читай байт-код как assembly.
7. Для wasm — обязательно сначала `wasm-decompile` для беглого обзора, потом `wasm2wat` для деталей.

## Правила

- Deobfuscated code — рабочая гипотеза. Для анти-реверса (Reflection в .NET, strings в native-методе) — явно отметь, что часть логики недоступна статикой.
- Для шифрующих managed-функций: часто ключ лежит захардкоженным в поле класса — ищи инициализаторы.
- Запрет додумывания: если ты не декомпилировал функцию `check()`, не пиши «вероятно XOR».

## Выход

- `work/decompiled/` — все исходники;
- `verification.md` с ссылкой на конкретный файл/метод/строку;
- если нужен брутфорс входа — `work/solver.py` на подходящем языке;
- флаг через `ctf-verifier` → `flag.txt`.
