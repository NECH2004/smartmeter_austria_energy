"""Define constants for Smartmeter Austria Energy integration."""

from enum import Enum


# https://www.dlms.com/files/Blue-Book-Ed-122-Excerpt.pdf
# define the data types
class DataType:
    NullData = 0x00
    Boolean = 0x03
    BitString = 0x04
    DoubleLong = 0x05
    DoubleLongUnsigned = 0x06
    OctetString = 0x09
    VisibleString = 0x0A
    Utf8String = 0x0C
    BinaryCodedDecimal = 0x0D
    Integer = 0x0F
    Long = 0x10
    Unsigned = 0x11
    LongUnsigned = 0x12
    Long64 = 0x14
    Long64Unsigned = 0x15
    Enum = 0x16
    Float32 = 0x17
    Float64 = 0x18
    DateTime = 0x19
    Date = 0x1A
    Time = 0x1B
    Array = 0x01
    Structure = 0x02
    CompactArray = 0x13


# https://www.dlms.com/files/Blue-Book-Ed-122-Excerpt.pdf
# defines the physical units of the data
class PhysicalUnits(Enum):
    Undef = 0x00

    W = 0x1B  # 27
    VA = 0x1C
    var = 0x1D
    Wh = 0x1E
    VAh = 0x1F
    varh = 0x20
    A = 0x21
    C = 0x22
    V = 0x23

    Hz = 0x2C
    
    NoUnit = 0xFF
