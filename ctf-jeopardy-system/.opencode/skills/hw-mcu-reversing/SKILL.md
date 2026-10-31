# skill: hw-mcu-reversing

Reverse прошивок MCU: Cortex-M, AVR, Xtensa (ESP), RISC-V.

## Шаг 1. Определи архитектуру

Признаки:
- `file <bin>` редко помогает;
- берём первые 4 байта и смотрим как 32-битное little-endian слово:
  - значение `0x20000000`–`0x20100000` → initial MSP, похоже на Cortex-M (SRAM в этой области);
  - `0xE9` первым байтом → ESP32/ESP8266 firmware image header;
  - читаемые ASCII «UBI», «squashfs» → это Linux rootfs, не MCU — вернуть в `ctf-hw-firmware` ветку Linux.

Для Cortex-M проверка reset vector:
```
python3 -c "
import struct
d = open('fw.bin','rb').read()
msp, pc = struct.unpack('<II', d[:8])
print(f'MSP=0x{msp:08x}, PC=0x{pc:08x}')
# PC должен быть odd (thumb bit=1)
"
```

## Шаг 2. Загрузи в Ghidra с правильным processor

- Cortex-M: `ARM:LE:32:Cortex`;
- AVR: `AVR8:LE:16`;
- RISC-V 32: `RISCV:LE:32:default`;
- Xtensa: нужен плагин **ghidra-xtensa** (устанавливается отдельно).

**Load base address критичен.** Для Cortex-M — обычно `0x08000000` (STM32 flash) или `0x00000000` (внутренняя flash других MCU). Для ESP32 — зависит от offset'а в image.

## Шаг 3. SVD-Loader (обязательно для ARM Cortex-M)

https://github.com/leveldown-security/SVD-Loader-Ghidra

1. Скачай SVD для своего чипа (STM32F103, nRF52832 и т.д.) из CMSIS-Pack:
   https://github.com/cmsis-svd/cmsis-svd (большая база).
2. В Ghidra: Script Manager → `SVD-Loader.py` → выбери SVD-файл.
3. Сразу после загрузки чтение/запись в peripheral адреса превращается в `GPIOA->ODR = X`, `RCC->APB1ENR |= 1<<Y`.

**Без SVD** декомпиляция Cortex-M выглядит как `*(uint*)0x40020014 = 0x12345` — нечитаемо.

## Шаг 4. Reset vector + ISR table

Первые 0x200–0x400 байт в Cortex-M — таблица векторов. Второй указатель (`Reset_Handler`) — твоя точка входа. Пройди Define Function + Analyze вручную, если авто-анализ пропустил.

## Шаг 5. Поиск флага

Варианты:
1. **Прямой strings-leak**:
   ```
   rg -oP 'ctfcup\{[^}]+\}' -a fw.bin
   ```
2. **XOR-ed flag в flash**: typical pattern — байт-массив длиной 32-40, рядом короткий цикл по длине. См. `flag-hunter` шаг 6 (XOR-sweep).
3. **Проверка через UART**: прошивка сравнивает ввод по UART с константой. Эмулируй:
   - `qiling` + `qiling.hw.external_device.UartDevice` → автоматический прогон;
   - или `qemu-system-arm -M <board>` с serial on stdio.
4. **Side-channel в прошивке**: если прошивка для AES → см. skill `hw-sidechannel`.

## Шаг 6. Эмуляция в qiling (пример для Cortex-M)

```python
# work/emu.py
from qiling import Qiling
from qiling.const import QL_VERBOSE

ql = Qiling(
    [r'./fw.bin'],
    r'./rootfs_stm32',       # пустая, но нужна
    archtype='cortex_m',
    verbose=QL_VERBOSE.DEBUG,
)

# UART input: что отправить
# ql.hw.create('usart1').send(b'password\n')

ql.run()
```

Для детальной эмуляции микроконтроллера qemu-system-arm требует board definition; qiling проще, но ограничен поддерживаемыми peripherals.

## Шаг 7. AVR особенности

- Harvard architecture: отдельные flash и RAM; строки часто в `__flash` сегменте, читаются через `pgm_read_byte`;
- в Ghidra обязательно разметить memory map с flash отдельно от RAM;
- для декомпиляции иногда помогает `avr-objdump -d -m avr5 fw.bin`.

## Шаг 8. ESP32 особенности

- Прошивка структурирована как image с несколькими сегментами;
- `esptool.py image_info fw.bin` показывает layout;
- Xtensa-плагин для Ghidra: https://github.com/Ebiroll/ghidra-xtensa (community);
- альтернатива — IDA с Xtensa processor module.
