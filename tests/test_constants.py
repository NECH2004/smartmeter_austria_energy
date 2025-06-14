"""OBIS data classes tests."""

# pylint: disable=invalid-name
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements

from src.smartmeter_austria_energy.constants import DataType, PhysicalUnits


def test_DataType_conversion()-> None:
    """Test a datatype conversion."""

    assert int(DataType.Float32) == 0x17

def test_datatype_values()-> None:
    """Test that DataType enum members have the expected hexadecimal values."""

    assert DataType.NullData == 0x00
    assert DataType.Boolean == 0x03
    assert DataType.BitString == 0x04
    assert DataType.DoubleLong == 0x05
    assert DataType.DoubleLongUnsigned == 0x06
    assert DataType.OctetString == 0x09
    assert DataType.VisibleString == 0x0A
    assert DataType.Utf8String == 0x0C
    assert DataType.BinaryCodedDecimal == 0x0D
    assert DataType.Integer == 0x0F
    assert DataType.Long == 0x10
    assert DataType.Unsigned == 0x11
    assert DataType.LongUnsigned == 0x12
    assert DataType.Long64 == 0x14
    assert DataType.Long64Unsigned == 0x15
    assert DataType.Enum == 0x16
    assert DataType.Float32 == 0x17
    assert DataType.Float64 == 0x18
    assert DataType.DateTime == 0x19
    assert DataType.Date == 0x1A
    assert DataType.Time == 0x1B
    assert DataType.Array == 0x01
    assert DataType.Structure == 0x02
    assert DataType.CompactArray == 0x13

def test_datatype_int_conversion()-> None:
    """Test that each DataType enum member converts to an integer correctly."""

    for member in DataType:
        # Verify that conversion to int yields an integer type.
        assert isinstance(int(member), int)

def test_physicalunits_values()-> None:
    """Test that PhysicalUnits enum members have the expected hexadecimal values."""

    assert PhysicalUnits.Undef == 0x00
    assert PhysicalUnits.W == 0x1B
    assert PhysicalUnits.VA == 0x1C
    assert PhysicalUnits.var == 0x1D
    assert PhysicalUnits.Wh == 0x1E
    assert PhysicalUnits.VAh == 0x1F
    assert PhysicalUnits.varh == 0x20
    assert PhysicalUnits.A == 0x21
    assert PhysicalUnits.C == 0x22
    assert PhysicalUnits.V == 0x23
    assert PhysicalUnits.Hz == 0x2C
    assert PhysicalUnits.NoUnit == 0xFF

def test_physicalunits_int_conversion()-> None:
    """Test that each PhysicalUnits enum member converts to an integer correctly."""

    for member in PhysicalUnits:
        # Verify that conversion to int yields an integer type.
        assert isinstance(int(member), int)

def test_datatype_unique()-> None:
    """Test that all values in DataTypes are unique."""
    
    values = [member.value for member in DataType]
    assert len(values) == len(set(values)), "Duplicate values found in DataType"

def test_physicalunits_unique()-> None:
    """Test that all values in PhysicalUnits are unique."""

    values = [member.value for member in PhysicalUnits]
    assert len(values) == len(set(values)), "Duplicate values found in PhysicalUnits"
