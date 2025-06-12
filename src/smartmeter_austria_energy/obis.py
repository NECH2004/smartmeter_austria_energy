"""Defines the OBIS objects."""

class Obis:
    """Defines the OBIS object."""

    @staticmethod
    def to_bytes(code: str) -> bytes:
        """Returns the code as byte array."""

        return bytes([int(a) for a in code.split(".")])

    # names of variables are fixed. Do not change.
    VoltageL1: bytes = to_bytes("01.0.32.7.0.255")
    VoltageL2: bytes = to_bytes("01.0.52.7.0.255")
    VoltageL3: bytes = to_bytes("01.0.72.7.0.255")
    CurrentL1: bytes = to_bytes("1.0.31.7.0.255")
    CurrentL2: bytes = to_bytes("1.0.51.7.0.255")
    CurrentL3: bytes = to_bytes("1.0.71.7.0.255")
    RealPowerIn: bytes = to_bytes("1.0.1.7.0.255")
    RealPowerOut: bytes = to_bytes("1.0.2.7.0.255")
    RealEnergyIn: bytes = to_bytes("1.0.1.8.0.255")
    RealEnergyOut: bytes = to_bytes("1.0.2.8.0.255")
    ReactiveEnergyIn: bytes = to_bytes("1.0.3.8.0.255")
    ReactiveEnergyOut: bytes = to_bytes("1.0.4.8.0.255")
    Factor: bytes= to_bytes("01.0.13.7.0.255")
    DeviceNumber: bytes = to_bytes("0.0.96.1.0.255")
    LogicalDeviceNumber: bytes = to_bytes("0.0.42.0.0.255")
