"""OBIS data classes tests."""

# pylint: disable=invalid-name
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements

from src.smartmeter_austria_energy.constants import DataType


def test_DataType_conversion():
    """Test a datatype conversion."""

    assert int(DataType.Float32) == 0x17
