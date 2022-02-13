# SC16IS752-micropython-library
Micropython library to connect WCMCU-752 2-UART Expansion board (SC16IS752) to ESP-32

My goal was to connect the third [GM-60](http://myosuploads3.banggood.com/products/20210303/20210303012407GM60BarcodeReaderModuleUserManual.pdf) Qr-code reader to ESP-32 which controls a club entrance. ESP-32 has only 2 UARTs so I bought the [WCMCU-752](https://www.nxp.com/docs/en/data-sheet/SC16IS752_SC16IS762.pdf) 2-UART Expansion board from Aliexpress. 

I didn't find a SC16IS752 library for Micropython, so I ported a suitable lib from C++. Only I2C communication has been ported, if you need SPI, you can easily add it yourself.

There is also a small script **test_uart.py** which allows to test the lib with GM-60 or any other device which transmits smth to UART.

## How to connect stuff

| SC16IS752	| ESP-32 |
|:---------:|:------:|
| VCC |	5V |
| GND	|	GND |
| RESET |	N/C |
| A0/CS	|	5V |
| A1/SI	|	GND (this gives addr 76 |
| NC/SO	| N/C |
| IRQ	| 17*|
| I2C/SPI	| 5V |
| SCL/SCLK | 18 |
| SDA/VSS | 19 |

* you need to wire the 1K resisor to 5V from one side and to GPIO 17 (ESP-32) and IRQ (WCMCU-752) pins from another side (it will look like a fork)

| GM-60 | ESP-32 | WCMCU-752 |
|:-----:|:------:|:---------:|
| GND | GND | N/C |
| RXD | N/C | TXA |
| TXD | N/C | RXA |
| VCC | 3.5V | N/C |
