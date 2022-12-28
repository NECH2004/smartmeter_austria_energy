from src.smartmeter_austria_energy.constants import (PhysicalUnits)
from src.smartmeter_austria_energy.obisvalue import (ObisValueFloat, ObisValueString)


def test_ObisvalueFloat():
    """Test the ObisValueFloat class."""
    # arrange
    my_raw_value : float = 12345

    my_Wh = 0x1E
    my_unit = PhysicalUnits(my_Wh)
    my_scale = -3

    # act
    my_obisvalue = ObisValueFloat(raw_value=my_raw_value, unit=my_unit, scale=my_scale)

    # assert
    assert my_obisvalue.RawValue == my_raw_value
    assert my_obisvalue.Scale == my_scale
    assert my_obisvalue.Unit == my_unit

    assert my_obisvalue.Value == my_raw_value * 10**my_scale
    assert my_obisvalue.ValueString == "{} {}".format(my_obisvalue.Value, my_obisvalue.Unit.name)


def test_ObisvalueString():
    """Test the ObisValueString class."""
    # arrange
    my_raw_value : str = "Test_me"

    # act
    my_obisvalue = ObisValueString(raw_value=my_raw_value)

    # assert
    assert my_obisvalue.RawValue == my_raw_value
