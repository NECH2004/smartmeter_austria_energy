"""Tests the obisvalue classes."""

# pylint: disable=invalid-name

import math

from src.smartmeter_austria_energy.constants import PhysicalUnits
from src.smartmeter_austria_energy.obisvalue import ObisValueBytes, ObisValueFloat


def test_ObisvalueFloat()-> None:
    """Test the ObisValueFloat class."""
    my_raw_value: float = 12345

    my_Wh = 0x1E
    my_unit = PhysicalUnits(my_Wh)
    my_scale = -3

    my_obisvalue = ObisValueFloat(raw_value=my_raw_value, unit=my_unit, scale=my_scale)

    assert my_obisvalue.raw_value == my_raw_value
    assert my_obisvalue.scale == my_scale
    assert my_obisvalue.unit == my_unit

    assert my_obisvalue.value == my_raw_value * 10**my_scale
    assert my_obisvalue.value_string == f"{my_obisvalue.value} {my_obisvalue.unit.name}"


def test_ObisvalueFloat_add_matching_unit()-> None:
    """Test the ObisValueFloat class add method."""

    my_raw_value1: float = 1.1
    my_raw_value2: float = 2.1

    my_Wh = 0x1E
    my_unit = PhysicalUnits(my_Wh)
    my_scale1 = 3
    my_scale2 = -1

    my_obisvalue1 = ObisValueFloat(
        raw_value=my_raw_value1, unit=my_unit, scale=my_scale1
    )
    my_obisvalue2 = ObisValueFloat(
        raw_value=my_raw_value2, unit=my_unit, scale=my_scale2
    )

    my_obisvalue = my_obisvalue1 + my_obisvalue2

    assert my_obisvalue.unit == my_unit

    assert (
        my_obisvalue.value
        == my_raw_value1 * 10**my_scale1 + my_raw_value2 * 10**my_scale2
    )
    assert my_obisvalue.value_string == f"{my_obisvalue.value} {my_obisvalue.unit.name}"


def test_ObisvalueFloat_sub_matching_unit()-> None:
    """Test the ObisValueFloat class subtract method."""

    my_raw_value1: float = 1.1
    my_raw_value2: float = 2.1

    my_Wh = 0x1E
    my_unit = PhysicalUnits(my_Wh)
    my_scale1 = 3
    my_scale2 = -1

    my_obisvalue1 = ObisValueFloat(
        raw_value=my_raw_value1, unit=my_unit, scale=my_scale1
    )
    my_obisvalue2 = ObisValueFloat(
        raw_value=my_raw_value2, unit=my_unit, scale=my_scale2
    )

    my_obisvalue = my_obisvalue1 - my_obisvalue2

    assert my_obisvalue.unit == my_unit
    assert (
        my_obisvalue.value
        == my_raw_value1 * 10**my_scale1 - my_raw_value2 * 10**my_scale2
    )
    assert my_obisvalue.value_string == f"{my_obisvalue.value} {my_obisvalue.unit.name}"


def test_ObisvalueFloat_add_not_matching_unit()-> None:
    """Test the ObisValueFloat class add method."""

    my_raw_value1: float = 0.7
    my_raw_value2: float = 6.23

    my_Wh = 0x1E
    my_W = 0x1B
    my_unit1 = PhysicalUnits(my_Wh)
    my_unit2 = PhysicalUnits(my_W)

    my_scale1 = -1
    my_scale2 = 4

    my_obisvalue1 = ObisValueFloat(
        raw_value=my_raw_value1, unit=my_unit1, scale=my_scale1
    )
    my_obisvalue2 = ObisValueFloat(
        raw_value=my_raw_value2, unit=my_unit2, scale=my_scale2
    )
    my_obisvalue = my_obisvalue1 + my_obisvalue2

    assert my_obisvalue.unit == PhysicalUnits.Undef
    assert math.isnan(my_obisvalue.value)
    assert my_obisvalue.value_string == f"{my_obisvalue.value} {my_obisvalue.unit.name}"


def test_ObisvalueFloat_sub_not_matching_unit()-> None:
    """Test the ObisValueFloat class subtract method."""

    my_raw_value1: float = 1.1
    my_raw_value2: float = 2.1

    my_Wh = 0x1E
    my_W = 0x1B
    my_unit1 = PhysicalUnits(my_Wh)
    my_unit2 = PhysicalUnits(my_W)

    my_scale1 = 1
    my_scale2 = 0

    my_obisvalue1 = ObisValueFloat(
        raw_value=my_raw_value1, unit=my_unit1, scale=my_scale1
    )
    my_obisvalue2 = ObisValueFloat(
        raw_value=my_raw_value2, unit=my_unit2, scale=my_scale2
    )
    my_obisvalue = my_obisvalue1 - my_obisvalue2

    assert my_obisvalue.unit == PhysicalUnits.Undef
    assert math.isnan(my_obisvalue.value)
    assert my_obisvalue.value_string == f"{my_obisvalue.value} {my_obisvalue.unit.name}"


def test_ObisvalueBates_raw_value()-> None:
    """Test the ObisValueBytes raw_value property."""

    my_raw_value: bytes = "Test_me".encode()
    my_obisvalue = ObisValueBytes(raw_value=my_raw_value)

    assert my_obisvalue.raw_value == my_raw_value


def test_ObisvalueBytes_value()-> None:
    """Test the ObisValueBytes value property."""

    my_raw_value: bytes = "Test_me".encode()
    my_obisvalue = ObisValueBytes(raw_value=my_raw_value)

    assert my_obisvalue.value == "Test_me"
