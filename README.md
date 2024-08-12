# Smartmeter Energy Austria

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield_y]][commits]
[![GitHub Activity][commits-shield_m]][commits]
[![GitHub Activity][commits-shield_w]][commits]

[![PyPi][pypi-shield]][pypi-address]
[![Python Versions][pypi-version-shield]][github-address]
[![Validate][validate-shield]][validation]
[![Build Status][pypi-publish-shield]][pypi-publish]

Library for connecting to Austrian Smart Meters of Salzburg Netz, TINETZ and EVN
Retrieves the data from the M-BUS connector using a serial to USB converter.

Only tested on a Kaifa MA309 and Salzburg Netz (Salzburg AG).
Some technical informations:
The device uses Wired M-Bus (RJ 12) at 2400 baud. (1 start bit, 8 data bits, 1 parity bit, even, 1 stop bit.
Communication is push only, every 5 seconds.

## Usage

1. Install this package `pip install smartmeter_austria_energy`
2. Connect to your inverter using the correct COM port and fetch the data.
Possible COM port settings:
/dev/ttyUSB0, eg. using Linux
COM5, eg using Windows

```python
from smartmeter_austria_energy.supplier import (SupplierSALZBURGNETZ)
from smartmeter_austria_energy.smartmeter import(Smartmeter)

def main():
    supplier = SupplierSALZBURGNETZ
    key_hex_string = "-- this is your key --"
    port = "COM5"

    smartmeter = Smartmeter(supplier, port, key_hex_string)
    my_obisdata = smartmeter.read()

    print(f"RealEnergyIn: {my_obisdata.RealEnergyIn.ValueString}")
    print(f"RealEnergyOut: {my_obisdata.RealEnergyOut.ValueString}")
 
if __name__ == '__main__':
    main()
```

Script was tested on Linux (Ubuntu, Debian, Raspberry OS) and Windows (Windows 10, Windows 11).

[releases-shield]: https://img.shields.io/github/v/release/NECH2004/smartmeter_austria_energy?style=for-the-badge
[releases]: https://github.com/NECH2004/smartmeter_austria_energy/releases

[commits-shield_y]: https://img.shields.io/github/commit-activity/y/NECH2004/smartmeter_austria_energy?style=for-the-badge
[commits-shield_m]: https://img.shields.io/github/commit-activity/m/NECH2004/smartmeter_austria_energy?style=for-the-badge
[commits-shield_w]: https://img.shields.io/github/commit-activity/w/NECH2004/smartmeter_austria_energy?style=for-the-badge
[commits]: https://github.com/NECH2004/smartmeter_austria_energy/commits/dev

[validate-shield]: https://github.com/NECH2004/smartmeter_austria_energy/actions/workflows/verify.yml/badge.svg
[validation]: https://github.com/NECH2004/smartmeter_austria_energy/actions/workflows/verify.yml

[license-shield]:https://img.shields.io/github/license/nech2004/smartmeter_austria_energy?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Christian%20Neumeier%20%40NECH2004?style=for-the-badge

[pypi-shield]: https://img.shields.io/pypi/v/smartmeter_austria_energy.svg
[pypi-address]: https://pypi.python.org/pypi/smartmeter_austria_energy/
[pypi-version-shield]: https://img.shields.io/pypi/pyversions/smartmeter_austria_energy.svg
[pypi-publish-shield]: https://github.com/NECH2004/smartmeter_austria_energy/actions/workflows/python-publish.yml/badge.svg
[pypi-publish]: https://github.com/NECH2004/smartmeter_austria_energy/actions/workflows/publish.yaml

[github-address]: https://github.com/NECH2004/smartmeter_austria_energy/

## Usage
Credits to Stefan who had done a cool work that was used in this implementation.
https://github.com/tirolerstefan/kaifa
