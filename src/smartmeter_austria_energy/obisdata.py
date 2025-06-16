"""Defines the OBIS data object."""

from .constants import PhysicalUnits
from .decrypt import Decrypt
from .obisvalue import ObisValueBytes, ObisValueFloat


class ObisData():
    """Holds all OBIS data."""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=invalid-name
    # names of variables are fixed. Do not change.

    def __init__(self, dec: Decrypt, wanted_values: list[str]) -> None:
        self._voltage_l1: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.V)
        self._voltage_l2: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.V)
        self._voltage_l3: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.V)
        self._current_l1: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.A)
        self._current_l2: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.A)
        self._current_l3: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.A)
        self._real_power_in: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.W)
        self._real_power_out: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.W)
        self._real_energy_in: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.Wh)
        self._real_energy_out: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.Wh)
        self._reactive_energy_in: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.varh)
        self._reactive_energy_out: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.varh)
        self._device_number: ObisValueBytes = ObisValueBytes(b"")
        self._logical_device_number: ObisValueBytes = ObisValueBytes(b"")

        for key in wanted_values:
            my_value = dec.get_obis_value(key)

            if hasattr(self, key):
                setattr(self, key, my_value)

    # Voltage
    @property
    def VoltageL1(self) -> ObisValueFloat:
        """Actual voltage on line 1."""
        return self._voltage_l1

    @VoltageL1.setter
    def VoltageL1(self, voltageL1: ObisValueFloat):
        self._voltage_l1 = voltageL1

    @property
    def VoltageL2(self) -> ObisValueFloat:
        """Actual voltage on line 2."""
        return self._voltage_l2

    @VoltageL2.setter
    def VoltageL2(self, voltageL2: ObisValueFloat):
        self._voltage_l2 = voltageL2

    @property
    def VoltageL3(self) -> ObisValueFloat:
        """Actual voltage on line 3."""
        return self._voltage_l3

    @VoltageL3.setter
    def VoltageL3(self, voltageL3: ObisValueFloat):
        self._voltage_l3 = voltageL3

    # Current
    @property
    def CurrentL1(self) -> ObisValueFloat:
        """Actual current on line 1."""
        return self._current_l1

    @CurrentL1.setter
    def CurrentL1(self, currentL1: ObisValueFloat):
        self._current_l1 = currentL1

    @property
    def CurrentL2(self) -> ObisValueFloat:
        """Actual current on line 2."""
        return self._current_l2

    @CurrentL2.setter
    def CurrentL2(self, currentL2: ObisValueFloat):
        self._current_l2 = currentL2

    @property
    def CurrentL3(self) -> ObisValueFloat:
        """Actual current on line31."""
        return self._current_l3

    @CurrentL3.setter
    def CurrentL3(self, currentL3: ObisValueFloat):
        self._current_l3 = currentL3

    # Power
    @property
    def RealPowerIn(self) -> ObisValueFloat:
        """The actual taken power."""
        return self._real_power_in

    @RealPowerIn.setter
    def RealPowerIn(self, realPowerIn: ObisValueFloat):
        self._real_power_in = realPowerIn

    @property
    def RealPowerOut(self) -> ObisValueFloat:
        """The actual given power."""
        return self._real_power_out

    @RealPowerOut.setter
    def RealPowerOut(self, realPowerOut: ObisValueFloat):
        self._real_power_out = realPowerOut

    # Calculated power property
    @property
    def RealPowerDelta(self) -> ObisValueFloat:
        """The difference between taken and given power."""
        return self._real_power_in - self._real_power_out

    # Energy
    @property
    def RealEnergyIn(self) -> ObisValueFloat:
        """The actual taken energy."""
        return self._real_energy_in

    @RealEnergyIn.setter
    def RealEnergyIn(self, realEnergyIn: ObisValueFloat):
        self._real_energy_in = realEnergyIn

    @property
    def RealEnergyOut(self) -> ObisValueFloat:
        """The actual given energy."""
        return self._real_energy_out

    @RealEnergyOut.setter
    def RealEnergyOut(self, realEnergyOut: ObisValueFloat):
        self._real_energy_out = realEnergyOut

    @property
    def ReactiveEnergyIn(self) -> ObisValueFloat:
        """The actual taken reactive energy."""
        return self._reactive_energy_in

    @ReactiveEnergyIn.setter
    def ReactiveEnergyIn(self, reactiveEnergyIn: ObisValueFloat):
        self._reactive_energy_in = reactiveEnergyIn

    @property
    def ReactiveEnergyOut(self) -> ObisValueFloat:
        """The actual given reactive energy."""
        return self._reactive_energy_out

    @ReactiveEnergyOut.setter
    def ReactiveEnergyOut(self, reactiveEnergyOut: ObisValueFloat):
        self._reactive_energy_out = reactiveEnergyOut

    # Device
    @property
    def DeviceNumber(self) -> ObisValueBytes:
        """The device number."""
        return self._device_number

    @DeviceNumber.setter
    def DeviceNumber(self, deviceNumber: ObisValueBytes):
        self._device_number = deviceNumber

    @property
    def LogicalDeviceNumber(self) -> ObisValueBytes:
        """The logical device number."""
        return self._logical_device_number

    @LogicalDeviceNumber.setter
    def LogicalDeviceNumber(self, logicalDeviceNumber: ObisValueBytes):
        self._logical_device_number = logicalDeviceNumber
