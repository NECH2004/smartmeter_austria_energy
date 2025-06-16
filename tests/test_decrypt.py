from unittest.mock import Mock

import pytest

from src.smartmeter_austria_energy.constants import PhysicalUnits
from src.smartmeter_austria_energy.decrypt import (
    SYSTITLE_LENGTH,
    SYSTITLE_START,
    Decrypt,
)
from src.smartmeter_austria_energy.obis import Obis
from src.smartmeter_austria_energy.obisvalue import ObisValueBytes, ObisValueFloat


@pytest.fixture
def decrypt_instance()-> Decrypt:
    # Create a mock supplier with required attributes.
    mock_supplier = Mock()
    mock_supplier.ic_start_byte = 0
    mock_supplier.enc_data_start_byte = 0

    # Create a dummy frame that is long enough to accommodate SYSTITLE extraction.
    dummy_frame_length = SYSTITLE_START + SYSTITLE_LENGTH + 10
    dummy_frame = bytes([0] * dummy_frame_length)
    # Dummy key: 16-byte hex string.
    instance = Decrypt(mock_supplier, dummy_frame, dummy_frame, "00112233445566778899aabbccddeeff")
    return instance


def test_parse_double_long_unsigned_data_type(decrypt_instance: Decrypt)->None:
    """Test the _parse_DoubleLongUnsigned_DataType method of Decrypt."""

    # For DoubleLongUnsigned:
    # - 4 bytes for value (e.g., 0x000003e8 for 1000)
    # - 3 dummy bytes,
    # - 1 byte for the scale (0),
    # - 1 dummy byte,
    # - 1 byte for unit (e.g., 0x21).
    value_bytes = b'\x00\x00\x03\xe8'
    dummy_3 = b'\x00\x00\x00'
    scale = b'\x00'
    dummy_1 = b'\x00'
    unit = b'\x21'
    decrypted = value_bytes + dummy_3 + scale + dummy_1 + unit
    initial_pos = 0
    obis_code = b'\x01\x02\x03\x04\x05\x06'

    # Use the mangled name for the private method
    new_pos = decrypt_instance._Decrypt__parse_DoubleLongUnsigned_DataType(decrypted, initial_pos, obis_code) # type: ignore
    # The helper should advance pos by 10 bytes.
    assert new_pos == 10
    assert decrypt_instance.obis[obis_code] == 1000
    ov = decrypt_instance.obis_values[obis_code]
    assert isinstance(ov, ObisValueFloat)
    assert ov.value == 1000
    # Compare using the unit value.
    assert ov.unit == PhysicalUnits(int.from_bytes(unit, "big"))
    assert ov.scale == 0


def test_parse_long_unsigned_data_type(decrypt_instance: Decrypt)->None:
    """Test the __parse_LongUnsigned_DataType method of Decrypt."""

    # For LongUnsigned:
    # - 2 bytes for value (e.g., b'\x03\xe8' for 1000)
    # - 3 dummy bytes,
    # - 1 byte for scale (0),
    # - 1 dummy byte,
    # - 1 byte for unit.
    value_bytes = b'\x03\xe8'
    dummy_3 = b'\x00\x00\x00'
    scale = b'\x00'
    dummy_1 = b'\x00'
    unit = b'\x21'
    decrypted = value_bytes + dummy_3 + scale + dummy_1 + unit
    initial_pos = 0
    obis_code = b'\x0A\x0B\x0C\x0D\x0E\x0F'

    new_pos = decrypt_instance._Decrypt__parse_LongUnsigned_DataType(decrypted, initial_pos, obis_code) # type: ignore
    assert new_pos == 8
    assert decrypt_instance.obis[obis_code] == 1000
    ov = decrypt_instance.obis_values[obis_code]
    assert isinstance(ov, ObisValueFloat)
    assert ov.value == 1000
    assert ov.unit == PhysicalUnits(int.from_bytes(unit, "big"))
    assert ov.scale == 0


def test_parse_octet_string_data_type(decrypt_instance: Decrypt)->None:
    """Test the __parse_OctetString_DataType method of Decrypt."""

    # For OctetString:
    # 1 byte for length, then that many data bytes, plus 2 extra dummy bytes.
    octet = b'abc'
    octet_len = len(octet)
    decrypted = bytes([octet_len]) + octet + b'\x00\x00'
    initial_pos = 0
    obis_code = b'\x11\x12\x13\x14\x15\x16'

    new_pos = decrypt_instance._Decrypt__parse_OctetString_DataType(decrypted, initial_pos, obis_code) # type: ignore
    assert new_pos == 1 + octet_len + 2
    assert decrypt_instance.obis[obis_code] == octet
    ov = decrypt_instance.obis_values[obis_code]
    assert isinstance(ov, ObisValueBytes)
    assert ov.raw_value == octet


def test_parse_double_long_unsigned_insufficient_data(decrypt_instance: Decrypt)->None:
    """Test the _parse_double_long_unsigned_insufficient_data method of Decrypt."""

    decrypted = b'\x00\x00'  # Insufficient bytes for value.
    obis_code = b'\xaa\xbb\xcc\xdd\xee\xff'
    with pytest.raises(ValueError, match="Not enough data to read DoubleLongUnsigned value"):
        decrypt_instance._Decrypt__parse_DoubleLongUnsigned_DataType(decrypted, 0, obis_code) # type: ignore

# ------------------------------------------------------------------------------
# Test: Error case for insufficient data in OctetString parsing.
# ------------------------------------------------------------------------------
def test_parse_octet_string_insufficient_data(decrypt_instance: Decrypt)->None:
    """Test the __parse_OctetString_DataType method with insufficient data."""

    decrypted = bytes([5]) + b'abc' + b'\x00'  # Insufficient bytes for a complete OctetString.
    obis_code = b'\xff\xff\xff\xff\xff\xff'
    with pytest.raises(ValueError, match="Not enough data to read the complete OctetString"):
        decrypt_instance._Decrypt__parse_OctetString_DataType(decrypted, 0, obis_code) # type: ignore


def test_get_obis_value_returns_value(decrypt_instance: Decrypt):
    """Test the get_obis_value method of Decrypt."""
    
    # Monkey-patch the Obis class to include an attribute that maps to a known OBIS code.
    test_obis_code = b'\xAA\xBB\xCC\xDD\xEE\xFF'
    setattr(Obis, "TEST_KEY", test_obis_code)
    
    # Now, populate the decrypt_instance's obis_values dictionary for that key.
    dummy_value = 123
    dummy_scale = 0
    dummy_unit = PhysicalUnits(0x21)
    dummy_ov = ObisValueFloat(dummy_value, dummy_unit, dummy_scale)
    decrypt_instance.obis_values[test_obis_code] = dummy_ov

    # Verify that get_obis_value returns the expected value.
    result = decrypt_instance.get_obis_value("TEST_KEY")
    assert result == dummy_ov


def test_get_obis_value_returns_none(decrypt_instance: Decrypt)->None:
    """Test the get_obis_value method of Decrypt when the key does not exist."""

    # Monkey-patch the Obis class with a key that is not present in obis_values.
    setattr(Obis, "NON_EXISTENT", b'\x00\x00\x00\x00\x00\x00')
    # Ensure that the key is not in obis_values.
    decrypt_instance.obis_values.pop(b'\x00\x00\x00\x00\x00\x00', None)

    # get_obis_value should return None when the key is not found.
    result = decrypt_instance.get_obis_value("NON_EXISTENT")
    assert result is None

def test_parse_all_exits_on_empty_data(decrypt_instance: Decrypt)->None:
    """Test that parse_all exits immediately when decrypted data is empty."""
    decrypt_instance._data_decrypted = b''  # type: ignore # Set decrypted data to an empty byte string.

    # Call parse_all() which should not process anything.
    decrypt_instance.parse_all()

    # Ensure no OBIS values were parsed.
    assert decrypt_instance.obis == {}
    assert decrypt_instance.obis_values == {}

    """
    Test the _parse_LongUnsigned_DataType function.
    
    We construct a decrypted stream as follows:
      - Bytes [0:2]: The 2-byte value. We choose b'\x03\xe8' for 1000.
      - Bytes [2:5]: 3 dummy bytes filler.
      - Byte [5]: Scale, chosen as 0.
      - Byte [6]: 1 dummy byte.
      - Byte [7]: Unit byte; chosen as b'\x21'.
    
    Total length is 8 bytes.
    In the method:
      - LONG_SIZE is 2.
      - scale_pos = pos + LONG_SIZE + 3 = 0 + 2 + 3 = 5.
      - unit_pos = scale_pos + 2 = 7.
      - The method increments pos by 8.
    
    After parsing, the method sets:
      obis[obis_code] = value * (10**scale) i.e. 1000,
      and creates an ObisValueFloat with (value, PhysicalUnits(unit), scale).
    """
    value_bytes = b'\x03\xe8'       # 2 bytes value 1000.
    dummy_fill = b'\xAA\xAA\xAA'     # 3 dummy bytes.
    scale_byte = b'\x00'             # scale 0.
    dummy2 = b'\xBB'                 # dummy byte.
    unit_byte = b'\x21'              # unit value.
    
    decrypted_stream = value_bytes + dummy_fill + scale_byte + dummy2 + unit_byte  # total: 2+3+1+1+1 = 8 bytes.
    
    obis_code = b'\x22\x22\x22\x22\x22\x22'
    
    new_pos = decrypt_instance._Decrypt__parse_LongUnsigned_DataType(decrypted_stream, 0, obis_code) # type: ignore
    # This method adds 8 to pos.
    assert new_pos == 8, "Expected new pos to be 8 for LongUnsigned parsing."
    
    # Check result:
    assert obis_code in decrypt_instance.obis, "OBIS code not stored for LongUnsigned."
    assert decrypt_instance.obis[obis_code] == 1000, "LongUnsigned value mismatch."
    ov = decrypt_instance.obis_values[obis_code]
    assert isinstance(ov, ObisValueFloat), "Expected an ObisValueFloat instance for LongUnsigned."
    assert ov.value == 1000, "Stored value in ObisValueFloat is incorrect for LongUnsigned."
    expected_unit = PhysicalUnits(int.from_bytes(unit_byte, "big"))
    assert ov.unit == expected_unit, "Unit in ObisValueFloat is incorrect for LongUnsigned."
    assert ov.scale == 0, "Scale is expected to be 0 for LongUnsigned."