# Octoprint-Xiaomi-BLE-Thermometer

The idea of this plugin is to be able to connect BLE thermometers running the [ATC_MiThermometer](https://github.com/atc1441/ATC_MiThermometer) custom firmware.


Requires:

> sudo apt-get install mercurial libbluetooth-dev libreadline-dev gcc python-dev bluetooth libbluetooth-dev

And pybluez Library running on python >=3.6:
> sudo pip3 install pybluez


|Xiaomi Mijia (LYWSD03MMC) | [Xiaomi Miaomiaoce (MHO-C401)](https://pvvx.github.io/MHO_C401) | [Qingping Temp & RH Monitor (CGG1-Mijia)](https://pvvx.github.io/CGG1) |
|:--:|:--:|:--:|
|  <img src="https://tasmota.github.io/docs/_media/bluetooth/LYWSD03MMC.png" alt="Xiaomi Mijia (LYWSD03MMC)" width="160"/> |  <img src="https://tasmota.github.io/docs/_media/bluetooth/MHO-C401.png" alt="Xiaomi Miaomiaoce (MHO-C401)" width="160"/> | <img src="https://pvvx.github.io/CGG1/img/CGG1-M.jpg" alt="E-ink CGG1 'Qingping Temp & RH Monitor', Xiaomi Mijia DevID: 0x0B48" width="160"/> |

## Advertising format of the custom firmware:
The [ATC_MiThermometer](https://github.com/atc1441/ATC_MiThermometer) custom firmware sends every minute an update of advertising data on the UUID 0x181A with the Tempereature, Humidity and Battery data.

The format of the advertising data is as follow: 

* Byte 5-10 MAC in correct order

* Byte 11-12 Temperature in int16

* Byte 13 Humidity in percent

* Byte 14 Battery in percent

* Byte 15-16 Battery in mV uint16_t

* Byte 17 frame packet counter

Example:
0x0e, 0x16, 0x1a, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xaa, 0xaa, 0xbb, 0xcc, 0xdd, 0xdd, 0x00