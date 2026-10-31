# Roadmap: что добавить к MVP

MVP (сейчас в репе) закрывает:
- category-router + 4 категорийных triage;
- 6 ключевых воркеров;
- `ctf-verifier` + `ctf-report`;
- переиспользуемые skills: `flag-hunter`, `*-triage`, `pwn-rop`, `pwn-heap`, `pwn-fmt`, `pwn-libc-matrix`, `stego-image`, `pcap-triage`, `hw-protocols`, `hw-mcu-reversing`.

## Приоритет 1 — после первых боёв

Добавить, когда таски реально приходят:

| Агент | Для чего | Skill, который к нему пишется |
|---|---|---|
| `ctf-rev-dynamic` | бинари, где нельзя статикой — anti-debug, самомодификация, рантайм-ключи | `rev-dynamic` (gdb + Frida + qemu-user) |
| `ctf-rev-vm` | кастомные VM внутри бинаря | `rev-vm-reversing` (dispatcher → opcode table → pseudo-C) |
| `ctf-forensics-memory` | memory dump | `volatility3-plugins` (с обязательным `windows.info`/`banners` в начале) |
| `ctf-forensics-disk` | disk images | `sleuthkit-workflow` (NTFS artifacts, $MFT, deleted recovery) |
| `ctf-forensics-stego-audio` | аудио-стего | `stego-audio` (spectrogram + LSB + hidden trailer) |
| `ctf-forensics-fileformat` | PDF/Office/zip-crack | `fileformat-crypto` (bkcrack, PDF streams, Office macros) |
| `ctf-hw-signal` | sigrok sessions | уже есть `hw-protocols` |
| `ctf-hw-sdr` | IQ-samples, SDR capture | уже есть `hw-protocols` + URH detail |

## Приоритет 2 — редкие категории

| Агент | Когда нужен |
|---|---|
| `ctf-pwn-kernel` | kernel-pwn (QEMU-rootfs, `.ko`) |
| `ctf-pwn-race` | race conditions |
| `ctf-rev-unpack` | нестандартные packer'ы |
| `ctf-hw-sidechannel` | лабораторный side-channel (power/EM traces) |
| `ctf-hw-fpga` | FPGA bitstream RE |
| `ctf-hw-rfid-nfc` | Mifare / Proxmark dumps |
| `ctf-forensics-mobile` | ADB/iOS backups, Docker image layers |

## Приоритет 3 — ensemble

- Параллельные `verification` work-items: несколько гипотез одновременно (по шаблону A/D-системы в соседнем репо).
- `ctf-escalation` — дорогая модель для тяжёлых развилок.
- Готовые few-shot writeup'ы в `.opencode/skills/*/references/` по 20–30 на категорию.

## Критерий «добавлять ли нового агента»

Добавлять, если:
1. Соответствующая таска реально попалась 2+ раза подряд.
2. Текущий triage её отдаёт в generic worker, который теряет >15 минут на базовом анализе.

Не добавлять «на всякий случай» — тонкие агенты + толстые skills работают хуже, чем узко-специализированные.
