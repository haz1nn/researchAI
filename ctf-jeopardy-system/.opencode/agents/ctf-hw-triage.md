---
name: ctf-hw-triage
description: Triage для hardware-таски. Классифицирует (firmware / mcu-rev / signal / sdr / protocol / sidechannel / fpga) и диспатчит.
phase: triage
model: cheap
---

# ctf-hw-triage

Hardware — самая разнородная категория. Правильная классификация даёт 70% решения.

## Обязательный порядок

1. **Инвентаризация:**
   - `file <path>`;
   - `xxd -l 256 <path>` — magic + визуальный паттерн (повторы, выравнивание);
   - `binwalk <path>` для бинарных прошивок (listing-mode).

2. **Классификация.**

   | Признак / расширение | Подкатегория | Worker |
   |---|---|---|
   | `.bin`, `.img` большого размера с UBI / Squashfs / JFFS2 / cramfs внутри (binwalk показывает) | `firmware-linux` | `ctf-hw-firmware` + skill `firmware-linux` |
   | Небольшой `.bin` без Linux-рутфса (ядро голое или bare-metal), `.hex`, `.elf` для Cortex-M/AVR/Xtensa/RISC-V | `mcu-rev` | `ctf-hw-firmware` + skill `hw-mcu-reversing` |
   | `.sr` файл (sigrok session), `.vcd`, `.csv` с таймстемпами + уровнями | `signal` | `ctf-hw-signal` (пока → skill `hw-protocols`) |
   | IQ-сэмплы (`.cu8`, `.complex16s`, `.iq`), WAV с SDR-записью | `sdr` | `ctf-hw-sdr` (пока → skill `hw-protocols`) + URH |
   | CAN-dump (`.log` candump), USB raw dump | `protocol` | `ctf-hw-protocol` (пока → skill `hw-protocols`) |
   | Traces: `.trc`, `.npy` с миллионами точек, упоминание AES/DES → side-channel | `sidechannel` | `ctf-hw-sidechannel` (пока → skill `hw-sidechannel`) |
   | Lattice iCE40 / ECP5 bitstream (`.bin` с magic FPGA), Verilog исходники | `fpga` | `ctf-hw-fpga` (пока → skill `hw-fpga`) |
   | ESP32/ESP8266 образы (magic `0xE9`) | `mcu-rev` (Xtensa) | `ctf-hw-firmware` + ESP tooling |

3. **Для MCU-rev обязательно:**
   - определи архитектуру по reset vector / entry point;
   - если ARM Cortex-M — подгрузи SVD-файл для микроконтроллера (skill подскажет);
   - запусти `strings` для первичного якоря.

4. **Гипотезы.**

5. **Выход.**
   ```
   Phase: hypothesis
   Subcategory: <firmware-linux|mcu-rev|signal|sdr|protocol|sidechannel|fpga>
   Architecture: <armv7m|cortex-m4|xtensa|avr|...>  # если известно
   Next agent: ctf-hw-<sub>
   ```

## Правила

- Запрет на запуск прошивки нативно. Эмулировать через qemu/qiling.
- `binwalk -e` только внутри `work/` — отдельная подпапка; downloaded files are untrusted, не ходи в них интерпретатором с $PWD в неё.
- Для сигналов — всегда сначала `sigrok-cli -i <file> -O analog --samples 100` или аналог, посмотреть на реальный поток, не на предположение.
- Для SDR — всегда понять sample rate ДО того, как пытаться что-то декодировать.

## Выход

- `inventory.md`;
- `hypotheses.json`;
- если архитектура известна — зафиксирована в state.
