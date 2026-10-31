# skill: hw-protocols

Декодирование электрических и радиосигналов. Применяется в `ctf-hw-signal`, `ctf-hw-sdr`, `ctf-hw-protocol`.

## sigrok-cli — цифровые сигналы

sigrok поддерживает ~130 protocol decoders (PD). Полный список: `sigrok-cli -L | grep decoder`.

Типовые:

| Протокол | PD | Параметры (минимум) |
|---|---|---|
| UART | `uart` | baud rate, data bits, parity, stop bits |
| I2C | `i2c` | SDA, SCL |
| SPI | `spi` | CLK, MOSI, MISO, CS |
| 1-Wire | `onewire_link`, `onewire_network` | DQ |
| CAN | `can` | CANH/CANL (или одно поле) + baud |
| USB (low/full speed) | `usb_signalling`, `usb_packet`, `usb_request` | D+, D-, speed |
| PS/2 | `ps2` | CLK, DATA |
| Modbus | `modbus` | поверх uart |
| JTAG | `jtag` | TCK, TMS, TDI, TDO |

### Пример: UART с автоопределением baud

```
# Если baud rate неизвестен — часто подбирается перебором стандартных:
for b in 9600 19200 38400 57600 115200 230400 460800 921600; do
  echo "=== $b ==="
  sigrok-cli -i session.sr -P uart:baudrate=$b:rx=D0 -A uart=rx-data 2>/dev/null | head -5
done
```

### Пример: SPI поверх `.sr`-файла

```
sigrok-cli -i session.sr -P spi:clk=D0:miso=D1:mosi=D2:cs=D3 -A spi=mosi-transfer,miso-transfer
```

### Для `.vcd` (ValueChangeDump)

```
sigrok-cli -i trace.vcd -P uart:baudrate=115200:rx=signal_name
```

## URH — радиосигналы (OOK/ASK/FSK/PSK)

https://github.com/jopohl/urh

Для `.cu8`, `.complex16s`, `.iq`, `.wav` (с SDR-записью):

1. Открой в URH GUI (`urh`).
2. **Interpretation tab:** определи sample rate (обычно задано в имени файла или описании таски).
3. Signal → autodetect modulation (OOK чаще всего в CTF-тасках).
4. **Analysis tab:** URH пытается найти символьный клок и декодировать биты.
5. Decode: Manchester / Differential Manchester / NRZ / NRZI — проверь все.

Для CLI batch'а:
```
# URH имеет CLI, но интерактивнее в GUI. Для batch:
urh_cli --signal input.complex16s --signal-sample-rate 2000000 \
        --modulation ask --bit-length 500 \
        --output-file bits.txt
```

## rtl_433 — ISM/433/868 МГц устройства

https://github.com/merbanan/rtl_433

Если задача про smart meters, remote keys, weather stations:
```
rtl_433 -r input.cu8 -A      # auto-decode все известные протоколы
rtl_433 -r input.cu8 -R 73   # конкретный протокол (список в -R help)
```

Часто CTF-таски строят на known protocols rtl_433 знает их все.

## Baud-rate detection by eye

Если sigrok не нашёл baud — открой `.sr` в PulseView, посмотри на самый короткий импульс. Baud ≈ `1 / shortest_pulse_time`.

Для `.wav` (аналоговый) с явной OOK — найди shortest high period в Audacity, inverse → bit rate.

## Правила

- Для UART без parity info и STOP — попробуй `8N1` первым, 95% CTF.
- Для SPI — проверь оба CPOL/CPHA (`spimode=0..3`), часто default не угадывает.
- Для I2C — если видишь много `NACK` — скорее всего неправильная sampling rate.
- URH **автоопределяет modulation и baud** на простых сигналах. Начинай с него, не руками.
