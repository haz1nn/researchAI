---
name: hw-triage
description: Classification and decoder matrix for hardware CTF artifacts (firmware, MCU dumps, logic/radio captures, bus logs, RFID/NFC). Use to identify the artifact class and pick the right loader/decoder before analysis.
---

# Hardware Triage

Цель: за ≤60с определить класс аппаратного артефакта и выбрать декодер/лоадер. Не гони весь decoder-стек вслепую.

## Шаг 1 — sniff

```bash
file <art>; exiftool <art>; xxd <art> | head; strings -n 6 <art> | head
binwalk -E <art>                  # entropy: >7.5 равномерно → crypto/compressed
```

## Шаг 2 — класс по сигнатуре/расширению

| Признак | Класс | Инструмент |
|---|---|---|
| `hsqs`/`sqsh` (SquashFS), `UBI#`, uImage, U-Boot строки | firmware | `binwalk -Me`/`unblob` → enumerate FS |
| `0xE9`+ESP header | ESP32/8266 | `esptool.py image_info`, Ghidra Xtensa |
| первые 4 байта = SP в SRAM-диапазоне, затем reset PC | Cortex-M raw dump | Ghidra + SVD-Loader (CMSIS SVD) |
| AVR hex/elf (ATmega) | AVR | `avr-objdump`, `simavr` |
| ELF `e_machine`=MIPS/ARM | router bin | Ghidra + qemu-user/qiling/FirmAE |
| `.sr`/`.srzip` (zip c metadata+каналами) | logic capture | `sigrok-cli` + PD |
| `.cfile`/`.iq`/`.cu8`/`.cs16`, имя IQ | SDR capture | `inspectrum` → `urh` → `rtl_433` |
| `.wav` с шумом (не речь) | SDR audio/SSTV | spectrogram → URH/qsstv |
| `.sub` текстовый | Flipper SubGhz | URH / `rtl_433` |
| 16 строк ASCII-hex по 16 байт / `.mfd`/`.nfc` | Mifare dump | ключи A/B, чтение блоков |
| `.bit`/bitstream, `set_property` | FPGA | IceStorm/Trellis/Vivado, BRAM init |
| USB pcap (linktype 220/249) | USB | `tshark -Y usb.capdata` |
| CAN лог `.log`/`.asc`/`.blf` | CAN | `can-utils`/`cantools` |
| `.npy`/`.cwp` trace | side-channel | lascar/scared/ChipWhisperer (эскалация) |

## Шаг 3 — decoder matrix (sigrok / URH)

- **sigrok**: сначала перечисли кандидатные протоколы с pin-назначением, потом декодируй. UART baud auto-detect — по минимальному интервалу фронтов. `sigrok-cli -i f.sr -P uart:baudrate=<B>:rx=D<n>`. SPI/I2C/1-Wire/JTAG/SWD/CAN/LIN аналогично через `-P`.
- **URH/SDR**: `inspectrum` для waterfall → оценка модуляции (OOK/FSK/PSK) и символьной скорости (автокорреляция |magnitude|) → URH auto-detect печатает кандидатов → выбери минимум ошибок → bitstream → декод кадра.
- **MCU**: определи арку по endianness reset vector и правдоподобным базам SRAM/flash. Cortex-M → SVD даёт имена MMIO.

## Правила

- Не «угадывай флаг» без зафиксированного пути декода (красивый ASCII в BRAM — не доказательство).
- Side-channel (CPA/DPA) и FPGA — узких воркеров нет: фиксируй и сигнал на эскалацию.
- Флаг валиден только по regex; кандидат — в `notes.md` для `ctf-verifier`.
