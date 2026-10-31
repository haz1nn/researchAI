---
name: ctf-hw-firmware
description: Прошивки — Linux-based (binwalk/unblob + rootfs) и MCU bare-metal (Ghidra + SVD). Эмуляция через qiling / qemu-system.
phase: verification + extraction
model: strong
---

# ctf-hw-firmware

Плейбуки:
- Linux-firmware: `.opencode/skills/firmware-linux/SKILL.md`
- MCU-reversing: `.opencode/skills/hw-mcu-reversing/SKILL.md`

## Ветка 1 — Linux-based firmware

1. **Распаковка (безопасная).**
   ```
   mkdir work/extracted
   cd work/extracted
   binwalk -Me ../../input/fw.bin     # Rust binwalk 2026+; -M рекурсивно, -e экстракт
   # или
   unblob -o . ../../input/fw.bin     # современная альтернатива, более предсказуемая
   ```
   Downloaded/extracted files are untrusted — не запускай интерпретатор ИЗ папки с ними.

2. **Обзор rootfs.**
   - `/etc/passwd` — захардкоженные пользователи;
   - `/etc/shadow` — хэши паролей (john/hashcat);
   - `/etc/init.d/`, `/etc/rcS` — что стартует;
   - `/bin/busybox` — часто одно место с кастомными апплетами;
   - `/usr/bin/*`, `/opt/*` — кастомные бинари → reverse через `ctf-rev-static`;
   - `/etc/dropbear/`, `/root/.ssh/` — ключи;
   - странные бинарники по размеру > 1MB.

3. **Поиск флага / якоря.**
   ```
   grep -r 'ctfcup{' . 2>/dev/null
   grep -rE '[Ff]lag|SECRET|TOKEN' . | head -50
   ```

4. **Эмуляция.**
   ```
   qemu-arm -L /path/to/libs ./target
   # Для сложных случаев:
   qiling run -f ./target --rootfs ./rootfs_dir
   ```
   qiling: https://github.com/qilingframework/qiling.

## Ветка 2 — MCU bare-metal

1. **Определи архитектуру.**
   - По reset-vector / entry point;
   - по строкам SDK (`STM32`, `NXP`, `ESP32`, `nRF52`, `atmega`);
   - для ESP32 — magic байт `0xE9`.

2. **Загрузи в Ghidra с правильной архитектурой.**
   - Cortex-M (ARM thumb): `ARM:LE:32:Cortex`.
   - AVR: `AVR8:LE:16`.
   - Xtensa (ESP): нужен Ghidra Xtensa processor (ghidra-xtensa).

3. **SVD-Loader (обязательно для Cortex-M).**
   - https://github.com/leveldown-security/SVD-Loader-Ghidra
   - Берёт SVD-файл чипа (STM32F103, nRF52832 — качается из CMSIS-Pack) и аннотирует memory map периферии.
   - Без SVD адрес `0x40020000` — просто цифра. С SVD — `GPIOA->ODR` или `RCC->APB1ENR`, что радикально ускоряет анализ.

4. **Reset vector + ISR table.** В Cortex-M первые 4 байта — initial MSP, следующие — Reset_Handler, HardFault_Handler, …

5. **Эмуляция.**
   - Для одной функции (не всю прошивку): FLARE-emu или `qiling.arch.cortex_m` script.
   - Для прошивки целиком: `qemu-system-arm -M <board>` (но нужна поддержка модели платы).

6. **Поиск флага.**
   - Строки + XOR-дешифровка;
   - проверка на кастомные крипто-примитивы (XOR на SRAM-странице, TEA, …);
   - проверка UART-логов эмулируемой прошивки — часто флаг выдаётся по UART после правильного ввода.

## Правила

- `-Me` в binwalk — отдельная папка; никогда в `input/`.
- Для qemu-system — всегда через snapshot/overlay disk, не портить образ прошивки.
- Для MCU — без SVD не садись за декомп, если это Cortex-M. Это даёт +50% скорости.

## Выход

- `work/extracted/` или `work/ghidra_project/`;
- `verification.md` со ссылками на функции/оффсеты;
- флаг через `ctf-verifier` → `flag.txt`.
