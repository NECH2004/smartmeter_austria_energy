"""OBIS data classes tests."""

# pylint: disable=invalid-name
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements

from unittest import mock
from unittest.mock import MagicMock, Mock

import pytest

from src.smartmeter_austria_energy.constants import PhysicalUnits
from src.smartmeter_austria_energy.decrypt import Decrypt
from src.smartmeter_austria_energy.obisdata import ObisData
from src.smartmeter_austria_energy.obisvalue import ObisValueBytes, ObisValueFloat


@pytest.fixture
def dummy_decrypt()-> Decrypt:
    """Create a dummy Decrypt instance for testing."""

    # Create a mock object for Decrypt.
    dummy = Mock()
    # Configure get_obis_value to return predetermined values
    # for some keys and None for others.
    dummy.get_obis_value.side_effect = lambda key: { # type: ignore
        "VoltageL1": ObisValueFloat(230, PhysicalUnits.V, 0),
        "CurrentL1": ObisValueFloat(5, PhysicalUnits.A, 0),
        "RealPowerIn": ObisValueFloat(1000, PhysicalUnits.W, 0),
        "RealPowerOut": ObisValueFloat(800, PhysicalUnits.W, 0),
        "DeviceNumber": ObisValueBytes(b"12345"),
    }.get(key, None) # type: ignore
    return dummy


@pytest.fixture
def dummy_decrypt_stub()-> Decrypt:
    """Create a dummy Decrypt instance for testing without specific keys."""

    dummy = MagicMock()
    # For simplicity in this test we don't need any specific keys.
    dummy.get_obis_value.return_value = None
    return dummy


@pytest.fixture
def dummy_big_decrypt_stub()-> Decrypt:
    """Create a dummy Decrypt instance with many keys for testing."""

    dummy = MagicMock()
    # Define the behavior for get_obis_value.
    dummy.get_obis_value.side_effect = lambda key: { # type: ignore
        "VoltageL1": ObisValueFloat(230, PhysicalUnits.V, 0),
        "CurrentL1": ObisValueFloat(5, PhysicalUnits.A, 0),
        "RealPowerIn": ObisValueFloat(1000, PhysicalUnits.W, 0),
        "RealPowerOut": ObisValueFloat(800, PhysicalUnits.W, 0),
        "DeviceNumber": ObisValueBytes(b"12345"),
    }.get(key, None) # type: ignore
    return dummy

def test_ObisData_constructor()-> None:
    """Test the obisdata constructor."""

    dec_mock = mock.MagicMock(spec=Decrypt)   # clone the public API

    obisdata = ObisData(dec=dec_mock, wanted_values=[])
    assert isinstance(obisdata, ObisData)


def test_ObisData_properties()-> None:
    """Test the obisdata constructor."""

    dec_mock = mock.MagicMock(spec=Decrypt)
    obisdata = ObisData(dec=dec_mock, wanted_values=[])

    current1 = obisdata.CurrentL1
    current2 = obisdata.CurrentL2
    current3 = obisdata.CurrentL3

    voltage1 = obisdata.VoltageL1
    voltage2 = obisdata.VoltageL2
    voltage3 = obisdata.VoltageL3

    realPowerIn = obisdata.RealPowerIn
    realPowerOut = obisdata.RealPowerOut
    realPowerDelta = obisdata.RealPowerDelta

    realEnergyIn = obisdata.RealEnergyIn
    realEnergyOut = obisdata.RealEnergyOut

    reactiveEnergyIn = obisdata.ReactiveEnergyIn
    reactiveEnergyOut = obisdata.ReactiveEnergyOut

    deviceNumber = obisdata.DeviceNumber
    logicalDeviceNumber = obisdata.LogicalDeviceNumber

    assert isinstance(current1, ObisValueFloat)
    assert current1.raw_value == 0
    assert current1.unit == PhysicalUnits.A

    assert isinstance(current2, ObisValueFloat)
    assert current2.raw_value == 0
    assert current2.unit == PhysicalUnits.A

    assert isinstance(current3, ObisValueFloat)
    assert current3.raw_value == 0
    assert current3.unit == PhysicalUnits.A

    assert isinstance(voltage1, ObisValueFloat)
    assert voltage1.raw_value == 0
    assert voltage1.unit == PhysicalUnits.V

    assert isinstance(voltage2, ObisValueFloat)
    assert voltage2.raw_value == 0
    assert voltage2.unit == PhysicalUnits.V

    assert isinstance(voltage3, ObisValueFloat)
    assert voltage3.raw_value == 0
    assert voltage3.unit == PhysicalUnits.V

    assert isinstance(realPowerIn, ObisValueFloat)
    assert realPowerIn.raw_value == 0
    assert realPowerIn.unit == PhysicalUnits.W

    assert isinstance(realPowerOut, ObisValueFloat)
    assert realPowerOut.raw_value == 0
    assert realPowerOut.unit == PhysicalUnits.W

    assert isinstance(realPowerDelta, ObisValueFloat)
    assert realPowerDelta.raw_value == 0
    assert realPowerDelta.unit == PhysicalUnits.W

    assert isinstance(realPowerIn, ObisValueFloat)
    assert realPowerIn.raw_value == 0
    assert realPowerIn.unit == PhysicalUnits.W

    assert isinstance(realPowerOut, ObisValueFloat)
    assert realPowerOut.raw_value == 0
    assert realPowerOut.unit == PhysicalUnits.W

    assert isinstance(realEnergyIn, ObisValueFloat)
    assert realEnergyIn.raw_value == 0
    assert realEnergyIn.unit == PhysicalUnits.Wh

    assert isinstance(realEnergyOut, ObisValueFloat)
    assert realEnergyOut.raw_value == 0
    assert realEnergyOut.unit == PhysicalUnits.Wh

    assert isinstance(reactiveEnergyIn, ObisValueFloat)
    assert reactiveEnergyIn.raw_value == 0
    assert reactiveEnergyIn.unit == PhysicalUnits.varh

    assert isinstance(reactiveEnergyOut, ObisValueFloat)
    assert reactiveEnergyOut.raw_value == 0
    assert reactiveEnergyOut.unit == PhysicalUnits.varh

    assert isinstance(deviceNumber, ObisValueBytes)
    assert deviceNumber.raw_value == b""

    assert isinstance(logicalDeviceNumber, ObisValueBytes)
    assert logicalDeviceNumber.raw_value == b""


def test_ObisData_property_setter()-> None:
    """Test the obisdata constructor."""

    dec_mock = mock.MagicMock(spec=Decrypt)
    obisdata = ObisData(dec=dec_mock, wanted_values=[])

    obisdata.CurrentL1 = ObisValueFloat(1.1, PhysicalUnits.A, 1)
    obisdata.CurrentL2 = ObisValueFloat(0.77, PhysicalUnits.Undef, -2)
    obisdata.CurrentL3 = ObisValueFloat(0.4, PhysicalUnits.A, 0)

    obisdata.VoltageL1 = ObisValueFloat(1.1, PhysicalUnits.V, 0)
    obisdata.VoltageL2 = ObisValueFloat(10, PhysicalUnits.V, 1)
    obisdata.VoltageL3 = ObisValueFloat(0.4, PhysicalUnits.V, 2)

    current1 = obisdata.CurrentL1
    current2 = obisdata.CurrentL2
    current3 = obisdata.CurrentL3

    voltage1 = obisdata.VoltageL1
    voltage2 = obisdata.VoltageL2
    voltage3 = obisdata.VoltageL3

    realPowerIn = obisdata.RealPowerIn
    realPowerOut = obisdata.RealPowerOut
    realPowerDelta = obisdata.RealPowerDelta

    realEnergyIn = obisdata.RealEnergyIn
    realEnergyOut = obisdata.RealEnergyOut

    reactiveEnergyIn = obisdata.ReactiveEnergyIn
    reactiveEnergyOut = obisdata.ReactiveEnergyOut

    deviceNumber = obisdata.DeviceNumber
    logicalDeviceNumber = obisdata.LogicalDeviceNumber

    assert isinstance(current1, ObisValueFloat)
    assert current1.raw_value == 1.1
    assert current1.value == 11
    assert current1.value_string == "11.0 A"
    assert current1.unit == PhysicalUnits.A

    assert isinstance(current2, ObisValueFloat)
    assert current2.raw_value == 0.77
    assert current2.value == 0.0077
    assert current2.value_string == "0.0077 Undef"
    assert current2.unit == PhysicalUnits.Undef

    assert isinstance(current3, ObisValueFloat)
    assert current3.raw_value == 0.4
    assert current3.value == 0.4
    assert current3.value_string == "0.4 A"
    assert current3.unit == PhysicalUnits.A

    assert isinstance(voltage1, ObisValueFloat)
    assert voltage1.raw_value == 1.1
    assert voltage1.value == 1.1
    assert voltage1.unit == PhysicalUnits.V

    assert isinstance(voltage2, ObisValueFloat)
    assert voltage2.raw_value == 10
    assert voltage2.value == 100
    assert voltage2.unit == PhysicalUnits.V

    assert isinstance(voltage3, ObisValueFloat)
    assert voltage3.raw_value == 0.4
    assert voltage3.value == 40
    assert voltage3.unit == PhysicalUnits.V

    assert isinstance(realPowerIn, ObisValueFloat)
    assert realPowerIn.raw_value == 0
    assert realPowerIn.unit == PhysicalUnits.W

    assert isinstance(realPowerOut, ObisValueFloat)
    assert realPowerOut.raw_value == 0
    assert realPowerOut.unit == PhysicalUnits.W

    assert isinstance(realPowerDelta, ObisValueFloat)
    assert realPowerDelta.raw_value == 0
    assert realPowerDelta.unit == PhysicalUnits.W

    assert isinstance(realPowerIn, ObisValueFloat)
    assert realPowerIn.raw_value == 0
    assert realPowerIn.unit == PhysicalUnits.W

    assert isinstance(realPowerOut, ObisValueFloat)
    assert realPowerOut.raw_value == 0
    assert realPowerOut.unit == PhysicalUnits.W

    assert isinstance(realEnergyIn, ObisValueFloat)
    assert realEnergyIn.raw_value == 0
    assert realEnergyIn.unit == PhysicalUnits.Wh

    assert isinstance(realEnergyOut, ObisValueFloat)
    assert realEnergyOut.raw_value == 0
    assert realEnergyOut.unit == PhysicalUnits.Wh

    assert isinstance(reactiveEnergyIn, ObisValueFloat)
    assert reactiveEnergyIn.raw_value == 0
    assert reactiveEnergyIn.unit == PhysicalUnits.varh

    assert isinstance(reactiveEnergyOut, ObisValueFloat)
    assert reactiveEnergyOut.raw_value == 0
    assert reactiveEnergyOut.unit == PhysicalUnits.varh

    assert isinstance(deviceNumber, ObisValueBytes)
    assert deviceNumber.raw_value == b""

    assert isinstance(logicalDeviceNumber, ObisValueBytes)
    assert logicalDeviceNumber.raw_value == b""


def test_Obisdata_no_wanted_values(dummy_big_decrypt_stub: Decrypt) -> None:
    """Test the ObisObisDataValue class."""

    data = ObisData(dummy_big_decrypt_stub, [])
    # Defaults for numeric values defined in __init__ should remain.
    assert isinstance(data.VoltageL1, ObisValueFloat)
    assert data.VoltageL1.value == 0
    # For bytes, default is an empty bytes object.
    assert isinstance(data.DeviceNumber, ObisValueBytes)
    assert data.DeviceNumber.raw_value == b""

def test_obisdata_dynamic_assignment(dummy_decrypt: Decrypt)-> None:
    """Test that the __init__ dynamically assigns OBIS values based on wanted_values."""
    
    # Only provide keys for which dummy_decrypt.get_obis_value returns a value.
    wanted_keys = ["VoltageL1", "DeviceNumber", "NonExistingKey"]
    data = ObisData(dummy_decrypt, wanted_keys)

    # For keys that were provided and exist...
    # VoltageL1 should have been updated; compare by checking its value.
    vol_l1 = data.VoltageL1
    assert isinstance(vol_l1, ObisValueFloat)
    assert vol_l1.value == 230
    assert vol_l1.unit == PhysicalUnits.V

    # DeviceNumber should be updated.
    dev_num = data.DeviceNumber
    assert isinstance(dev_num, ObisValueBytes)
    # In your design, DeviceNumber remains set to the dummy value.
    assert dev_num.raw_value == b"12345"

    # For keys not returned (or non-existing), the default should remain.
    # For example, VoltageL2 was initialized with a zero value and unit V.
    vol_l2 = data.VoltageL2
    assert isinstance(vol_l2, ObisValueFloat)
    assert vol_l2.value == 0
    assert vol_l2.unit == PhysicalUnits.V


def test_obisdata_setters_and_getters(dummy_decrypt: Decrypt)-> None:
    """Test that the setters and getters for ObisData work correctly."""
    
    data = ObisData(dummy_decrypt, [])
    
    # Set each property using the setter and check with the getter.
    new_voltage = ObisValueFloat(240, PhysicalUnits.V, 0)
    data.VoltageL1 = new_voltage
    assert data.VoltageL1 == new_voltage

    new_current = ObisValueFloat(10, PhysicalUnits.A, 0)
    data.CurrentL1 = new_current
    assert data.CurrentL1 == new_current

    new_device = ObisValueBytes(b"ABCDEF")
    data.DeviceNumber = new_device
    assert data.DeviceNumber == new_device


def test_real_power_delta(dummy_decrypt: Decrypt)-> None:
    """Test that the RealPowerDelta property calculates the difference correctly."""

    # We don't care about the dynamic assignment here.
    data = ObisData(dummy_decrypt, [])
    # Set RealPowerIn and RealPowerOut via the setters.
    data.RealPowerIn = ObisValueFloat(1000, PhysicalUnits.W, 0)
    data.RealPowerOut = ObisValueFloat(800, PhysicalUnits.W, 0)
    # Assuming ObisValueFloat supports subtraction and produces a new ObisValueFloat.
    delta = data.RealPowerDelta
    # The expected difference is 200.
    assert isinstance(delta, ObisValueFloat)
    assert delta.value == 200
    # Optionally, check that the units match.
    assert delta.unit == PhysicalUnits.W


def test_energy_and_logical_device_setters(dummy_decrypt_stub: Decrypt)-> None:
    """Test the setters for energy and logical device properties."""
    
    # Create an ObisData instance with an empty wanted_values list.
    data = ObisData(dummy_decrypt_stub, [])

    # --- Real Energy In ---
    new_energy_in = ObisValueFloat(500, PhysicalUnits.Wh, 0)
    data.RealEnergyIn = new_energy_in
    assert data.RealEnergyIn == new_energy_in
    # --- Real Energy Out ---
    new_energy_out = ObisValueFloat(300, PhysicalUnits.Wh, 0)
    data.RealEnergyOut = new_energy_out
    assert data.RealEnergyOut == new_energy_out

    # --- Reactive Energy In ---
    new_reactive_in = ObisValueFloat(150, PhysicalUnits.varh, 0)
    data.ReactiveEnergyIn = new_reactive_in
    assert data.ReactiveEnergyIn == new_reactive_in
    # --- Reactive Energy Out ---
    new_reactive_out = ObisValueFloat(100, PhysicalUnits.varh, 0)
    data.ReactiveEnergyOut = new_reactive_out
    assert data.ReactiveEnergyOut == new_reactive_out

    # --- Logical Device Number ---
    new_logical_device = ObisValueBytes(b"LOG123")
    data.LogicalDeviceNumber = new_logical_device
    assert data.LogicalDeviceNumber == new_logical_device