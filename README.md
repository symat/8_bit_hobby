# 8_bit_hobby
Developing an 8bit computer and peripherals, testers, debuggers, etc.


## Prerequisites

Beside building the computer and the devboard :)

* install python libraries (I'm using python 3.6 on Raspberry Pi OS)
  * `sudo pip install gpiozero` - for easily managing GPIO pins
  * 'sudo pip install spidev RPiMCP23S17' - to be able to use the I/O extender chip (MCP23S17)

* you need to load the SPI kernel modules before you can use SPI devices. Use the gpio command: `gpio load spi`

* to be able to open / edit the PCB plans, install: kicad (https://kicad.org/download/ubuntu/)