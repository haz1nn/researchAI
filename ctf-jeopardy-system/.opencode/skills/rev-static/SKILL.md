# skill: rev-static

Основной статический плейбук. Применяет `ctf-rev-static`.

## Шаг 1. Открытие

Два канала — используй параллельно, если доступны.

### GhidraMCP

Запусти Ghidra, импортируй бинарь, подключись через GhidraMCP (`decompile_function`, `rename_symbol`, `list_strings`, `list_functions`, `list_imports`). URL: https://github.com/LaurieWired/GhidraMCP.

### radare2

```
r2 -A ./binary
> aaa
> afl              # список функций
> is               # символы
> iz               # strings
> pdf @ main       # декомпил/дизасм main
```

С `r2ai`: `r2ai -m <model>` — встроенный LLM-канал поверх r2 (https://github.com/radareorg/r2ai).

## Шаг 2. Capa проход

```
capa ./binary -v > work/capa.txt
```

Теги вроде `encrypt data using XOR`, `decode data using Base64`, `check for stack cookie`, `communicate over HTTP` — экономят время.

## Шаг 3. Signature-first

Для каждой подозрительной функции (`main`, `check*`, `verify*`, `decrypt*`, `init*`) ровно 5 bullets:

```
- inputs:      <типы, откуда приходят>
- outputs:     <что возвращает и куда пишет>
- side effects:<fs/net/stdin/stdout>
- likely name: <предполагаемое имя>
- algorithm:   <XOR / RC4 / TEA / XTEA / AES / CRC32 / FNV / custom>
```

Запрет на «explain this code». Этот свёрнутый формат защищает от болтовни.

## Шаг 4. Константы-якоря

```
# TEA / XTEA
r2 -q -c 'px/4 @ main; / 9e3779b9' ./binary
# AES S-box
python3 -c "d=open('./binary','rb').read(); print(b'\\x63\\x7c\\x77\\x7b' in d)"
# zlib
python3 -c "d=open('./binary','rb').read(); print(b'\\x78\\x9c' in d or b'\\x78\\xda' in d)"
# md5 init
r2 -q -c '/ 67452301' ./binary
```

## Шаг 5. Rename-loop (только Ghidra)

- Проход 1: декомпилировать → предложить имена через LLM → применить `rename_symbol`.
- Проход 2: декомпилировать уже с чистыми именами. Читаемость резко растёт.

## Шаг 6. Два пути к флагу

### A. Reverse-check

Функция сравнивает ввод с константой/XOR-результатом. Пишешь `work/solver.py`:
```python
# пример: байтовый XOR
cipher = bytes.fromhex('...')
key    = bytes.fromhex('...')
flag   = bytes(c ^ k for c, k in zip(cipher, key*((len(cipher)//len(key))+1)))
print(flag)
```

### B. Крипто-примитив

Опознан TEA / RC4 / AES-ECB:
```python
# пример XTEA
from struct import pack, unpack

def xtea_decrypt(block, key, rounds=32):
    v0, v1 = unpack('<II', block)
    delta = 0x9E3779B9
    sum_  = (delta * rounds) & 0xFFFFFFFF
    for _ in range(rounds):
        v1 = (v1 - (((v0<<4 ^ v0>>5) + v0) ^ (sum_ + key[(sum_>>11) & 3]))) & 0xFFFFFFFF
        sum_ = (sum_ - delta) & 0xFFFFFFFF
        v0 = (v0 - (((v1<<4 ^ v1>>5) + v1) ^ (sum_ + key[sum_ & 3]))) & 0xFFFFFFFF
    return pack('<II', v0, v1)
```

## Шаг 7. Если застрял

- angr для constraint-solving: когда флаг — вход, прошедший серию branches:
```python
import angr
p = angr.Project('./binary', auto_load_libs=False)
st = p.factory.entry_state()
sm = p.factory.simgr(st)
sm.explore(find=0xADDR_SUCCESS, avoid=[0xADDR_FAIL])
print(sm.found[0].posix.dumps(0))
```
- FLARE-emu для эмуляции одной функции (Unicorn-based).

## Правила

- Декомпиляция — гипотеза, не истина. Константы и ветки проверяй дизасмом.
- Для крипто-функций имя Ghidra игнорируй. Доверяй сигнатуре констант.
- Запрет додумывания: если ты не декомпилировал функцию, не пиши «вероятно XOR».
