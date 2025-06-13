import pytest
from unittest.mock import Mock

from src.smartmeter_austria_energy.obis import Obis
from src.smartmeter_austria_energy.constants import DataType, PhysicalUnits
from src.smartmeter_austria_energy.decrypt import Decrypt, SYSTITLE_START, SYSTITLE_LENGTH
from src.smartmeter_austria_energy.obisvalue import ObisValueFloat, ObisValueBytes


@pytest.fixture
def decrypt_instance():
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


def test_parse_double_long_unsigned_data_type(decrypt_instance: Decrypt):
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


def test_parse_long_unsigned_data_type(decrypt_instance: Decrypt):
    """Test the _parse_LongUnsigned_DataType method of Decrypt."""

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

    new_pos = decrypt_instance._parse_LongUnsigned_DataType(decrypted, initial_pos, obis_code) # type: ignore
    assert new_pos == 8
    assert decrypt_instance.obis[obis_code] == 1000
    ov = decrypt_instance.obis_values[obis_code]
    assert isinstance(ov, ObisValueFloat)
    assert ov.value == 1000
    assert ov.unit == PhysicalUnits(int.from_bytes(unit, "big"))
    assert ov.scale == 0


def test_parse_octet_string_data_type(decrypt_instance: Decrypt):
    """Test the _parse_OctetString_DataType method of Decrypt."""

    # For OctetString:
    # 1 byte for length, then that many data bytes, plus 2 extra dummy bytes.
    octet = b'abc'
    octet_len = len(octet)
    decrypted = bytes([octet_len]) + octet + b'\x00\x00'
    initial_pos = 0
    obis_code = b'\x11\x12\x13\x14\x15\x16'

    new_pos = decrypt_instance._parse_OctetString_DataType(decrypted, initial_pos, obis_code) # type: ignore
    assert new_pos == 1 + octet_len + 2
    assert decrypt_instance.obis[obis_code] == octet
    ov = decrypt_instance.obis_values[obis_code]
    assert isinstance(ov, ObisValueBytes)
    assert ov.raw_value == octet


def test_parse_double_long_unsigned_insufficient_data(decrypt_instance: Decrypt):
    """Test the _parse_double_long_unsigned_insufficient_data method of Decrypt."""

    decrypted = b'\x00\x00'  # Insufficient bytes for value.
    obis_code = b'\xaa\xbb\xcc\xdd\xee\xff'
    with pytest.raises(ValueError, match="Not enough data to read DoubleLongUnsigned value"):
        decrypt_instance._Decrypt__parse_DoubleLongUnsigned_DataType(decrypted, 0, obis_code) # type: ignore

# ------------------------------------------------------------------------------
# Test: Error case for insufficient data in OctetString parsing.
# ------------------------------------------------------------------------------
def test_parse_octet_string_insufficient_data(decrypt_instance: Decrypt):
    """Test the _parse_OctetString_DataType method with insufficient data."""

    decrypted = bytes([5]) + b'abc' + b'\x00'  # Insufficient bytes for a complete OctetString.
    obis_code = b'\xff\xff\xff\xff\xff\xff'
    with pytest.raises(ValueError, match="Not enough data to read the complete OctetString"):
        decrypt_instance._parse_OctetString_DataType(decrypted, 0, obis_code) # type: ignore


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


def test_get_obis_value_returns_none(decrypt_instance: Decrypt):
    """Test the get_obis_value method of Decrypt when the key does not exist."""

    # Monkey-patch the Obis class with a key that is not present in obis_values.
    setattr(Obis, "NON_EXISTENT", b'\x00\x00\x00\x00\x00\x00')
    # Ensure that the key is not in obis_values.
    decrypt_instance.obis_values.pop(b'\x00\x00\x00\x00\x00\x00', None)

    # get_obis_value should return None when the key is not found.
    result = decrypt_instance.get_obis_value("NON_EXISTENT")
    assert result is None

def test_parse_all_exits_on_empty_data(decrypt_instance: Decrypt):
    """Test that parse_all exits immediately when decrypted data is empty."""
    decrypt_instance._data_decrypted = b''  # type: ignore # Set decrypted data to an empty byte string.

    # Call parse_all() which should not process anything.
    decrypt_instance.parse_all()

    # Ensure no OBIS values were parsed.
    assert decrypt_instance.obis == {}
    assert decrypt_instance.obis_values == {}


def test_parse_all(decrypt_instance: Decrypt):
    """
    This test builds a decrypted stream that consists of three blocks:
    
    Block 1: DoubleLongUnsigned
        Header (9 bytes):
          - Byte 0: DataType.OctetString
          - Byte 1: 6
          - Bytes 2-7: OBIS code block1 (e.g. b'\x11\x11\x11\x11\x11\x11')
          - Byte 8: DataType.DoubleLongUnsigned
        Body (10 bytes):
          - 4 bytes value: b'\x00\x00\x03\xe8' (i.e. 1000)
          - 3 bytes dummy: b'\x00\x00\x00'
          - 1 byte scale: b'\x00'
          - 1 byte dummy: b'\x00'
          - 1 byte unit: b'\x21'
        Total = 19 bytes.
    
    Block 2: LongUnsigned
        Header (9 bytes):
          - Byte 0: DataType.OctetString
          - Byte 1: 6
          - Bytes 2-7: OBIS code block2 (e.g. b'\x22\x22\x22\x22\x22\x22')
          - Byte 8: DataType.LongUnsigned
        Body (8 bytes):
          - 2 bytes value: b'\x03\xe8' (i.e. 1000)
          - 3 bytes dummy: b'\x00\x00\x00'
          - 1 byte scale: b'\x00'
          - 1 byte dummy: b'\x00'
          - 1 byte unit: b'\x21'
        Total = 17 bytes.
    
    Block 3: OctetString via EVN Device Name Emulation (requires pos>220)
        We add filler bytes so that the block starts after position 220.
        Header (2 bytes):
          - At position >220: Byte 0: DataType.OctetString, Byte 1: 0xC
          (This header always uses a fixed OBIS code: b"\x00\x00\x60\x01\x00\xff" and sets data_type = DataType.OctetString.)
        Body (6 bytes):
          - 1 byte length: here we pick 3 (i.e. b'\x03')
          - 3 bytes of data: b'xyz'
          - 2 extra bytes: b'\x00\x00'
        Total = 8 bytes (2 header + 6 body).
    
    We then verify that after calling parse_all() on the full stream:
      - Block 1 data is correctly mapped (value 1000, unit corresponding to b'\x21', scale 0) for its OBIS code.
      - Block 2 data is correctly mapped with value 1000.
      - Block 3 uses the fixed OBIS code b"\x00\x00\x60\x01\x00\xff" and contains the OctetString data b'xyz'.
    """
    # --- Build Block 1 (DoubleLongUnsigned) ---
    obis_code1 = b'\x11\x11\x11\x11\x11\x11'
    header1 = bytes([
        DataType.OctetString,    # Header byte 0
        6                        # Header byte 1
    ]) + obis_code1 + bytes([DataType.DoubleLongUnsigned]) # Header bytes 2-8 (9 bytes total)
    # Body for DoubleLongUnsigned: 10 bytes.
    # value: 4 bytes for 1000, 3 dummy bytes, scale (0), dummy (0), unit (0x21)
    body1 = b'\x00\x00\x03\xe8' + b'\x00\x00\x00' + b'\x00' + b'\x00' + b'\x21'
    block1 = header1 + body1  # Total 19 bytes

    # --- Build Block 2 (LongUnsigned) ---
    obis_code2 = b'\x22\x22\x22\x22\x22\x22'
    header2 = bytes([
        DataType.OctetString,
        6
    ]) + obis_code2 + bytes([DataType.LongUnsigned])  # Header: 9 bytes
    # Body for LongUnsigned: 8 bytes.
    body2 = b'\x03\xe8' + b'\x00\x00\x00' + b'\x00' + b'\x00' + b'\x21'
    block2 = header2 + body2  # Total 17 bytes

    # --- Create filler to push the next block beyond pos 220 ---
    current_length = len(block1) + len(block2)  # = 19 + 17 = 36 bytes
    filler_length = 221 - current_length       # Fill to reach position 221.
    filler = b'\xFF' * filler_length            # Filler bytes; arbitrary value not equal to DataType.OctetString.

    # --- Build Block 3 (OctetString via EVN Device Name Emulation) ---
    # For the EVN Device Name Emulation, header:
    #   When decrypted[pos+1] == 0xC and pos > 220, the code sets:
    #       obis_code = b"\x00\x00\x60\x01\x00\xff"
    #       data_type = DataType.OctetString, and increments pos by 1.
    header3 = bytes([DataType.OctetString, 0xC])
    # Body for OctetString: 6 bytes: length (1 byte), data (3 bytes), then 2 extra bytes.
    octet_data = b'xyz'
    body3 = bytes([len(octet_data)]) + octet_data + b'\x00\x00'
    block3 = header3 + body3  # Total 2 + 6 = 8 bytes

    # --- Concatenate all parts to form the full decrypted data ---
    full_decrypted = block1 + block2 + filler + block3

    # Override the _data_decrypted attribute with our constructed stream.
    decrypt_instance._data_decrypted = full_decrypted # type: ignore

    # Call parse_all() to process the full stream.
    decrypt_instance.parse_all()

    # --- Verify Block 1 parsing results ---
    # Block 1 uses the OBIS code from header1.
    assert obis_code1 in decrypt_instance.obis
    # Block 1 represents a DoubleLongUnsigned value 1000 * (10**0).
    assert decrypt_instance.obis[obis_code1] == 1000
    ov1 = decrypt_instance.obis_values[obis_code1]
    assert isinstance(ov1, ObisValueFloat)
    assert ov1.value == 1000
    assert ov1.scale == 0
    assert ov1.unit == PhysicalUnits(int.from_bytes(b'\x21', "big"))

    # --- Verify Block 2 parsing results ---
    assert obis_code2 in decrypt_instance.obis
    assert decrypt_instance.obis[obis_code2] == 1000
    ov2 = decrypt_instance.obis_values[obis_code2]
    assert isinstance(ov2, ObisValueFloat)
    assert ov2.value == 1000
    assert ov2.scale == 0
    assert ov2.unit == PhysicalUnits(int.from_bytes(b'\x21', "big"))

    # --- Verify Block 3 (OctetString) parsing results ---
    # Block 3 uses the fixed OBIS code from EVN Device Name Emulation.
    obis_code3 = b"\x00\x00\x60\x01\x00\xff"
    assert obis_code3 in decrypt_instance.obis

    # Update the expected value to a string if your production code is converting bytes to str.
    expected_octet_data = "xyz"
    ov3 = decrypt_instance.obis_values[obis_code3]
    # If your ObisValueBytes returns the data as str
    assert isinstance(ov3, ObisValueBytes)
    assert ov3.value == expected_octet_data


def test_parse_all_with_evn(decrypt_instance: Decrypt):
    """Test the parse_all() method of Decrypt with an EVN block."""
    """
    In this test, we build three blocks:

    Block 1: A DoubleLongUnsigned block

    Block 2: A LongUnsigned block

    Block 3: An EVN OctetString block.
    
    For the EVN block:
    To trigger the EVN branch, we need:
        - At the block start: first byte = DataType.OctetString.
        - Second byte = 0xC.
        - Then, after the header, the parser will do "pos += 1"
        and call _parse_OctetString_DataType with pos pointing to the
        length byte. Therefore, we provide the length byte as 0x0C (12).
        - Then we supply 12 data bytes, and 2 extra bytes.

    Total length of Block 3 = header (2 bytes) + body (1 + 12 + 2) = 17 bytes.
    """

    # --- Build Block 1 (DoubleLongUnsigned) ---
    obis_code1 = b'\x11\x11\x11\x11\x11\x11'
    header1 = bytes([
        DataType.OctetString,    # Byte 0
        6                        # Byte 1: OBIS code length (6)
    ]) + obis_code1 + bytes([DataType.DoubleLongUnsigned])
    body1 = b'\x00\x00\x03\xe8' + b'\x00\x00\x00' + b'\x00' + b'\x00' + b'\x21'
    block1 = header1 + body1  # Total 19 bytes

    # --- Build Block 2 (LongUnsigned) ---
    obis_code2 = b'\x22\x22\x22\x22\x22\x22'
    header2 = bytes([
        DataType.OctetString,
        6
    ]) + obis_code2 + bytes([DataType.LongUnsigned])
    body2 = b'\x03\xe8' + b'\x00\x00\x00' + b'\x00' + b'\x00' + b'\x21'
    block2 = header2 + body2  # Total 17 bytes

    # --- Build Block 3 (EVN OctetString) ---
    # EVN header: 2 bytes: first is DataType.OctetString, second is 0xC.
    header3 = bytes([DataType.OctetString, 0xC])
    # For the body, the EVN branch now advances 2 bytes so that the next byte is the length.
    octet_data = b'abcdefghijkl'
    octet_data_length = len(octet_data)  # 12
    body3 = bytes([octet_data_length]) + octet_data + b'\x00\x00'
    block3 = header3 + body3  # 2 + 1 + 12 + 2 = 17 bytes

    # --- Assemble the full decrypted stream ---
    initial_stream = block1 + block2  # 19 + 17 = 36 bytes.
    filler_length = 221 - len(initial_stream)
    filler = b'\xFF' * filler_length
    full_decrypted = initial_stream + filler + block3

    # Override the _data_decrypted attribute.
    decrypt_instance._data_decrypted = full_decrypted # type: ignore

    # Call parse_all() to process the stream.
    decrypt_instance.parse_all()

    # --- Verify Block 1 parsing ---
    assert obis_code1 in decrypt_instance.obis
    assert decrypt_instance.obis[obis_code1] == 1000
    ov1 = decrypt_instance.obis_values[obis_code1]
    assert isinstance(ov1, ObisValueFloat)
    assert ov1.value == 1000
    assert ov1.scale == 0
    assert ov1.unit == PhysicalUnits(int.from_bytes(b'\x21', "big"))
    
    # --- Verify Block 2 parsing ---
    assert obis_code2 in decrypt_instance.obis
    assert decrypt_instance.obis[obis_code2] == 1000
    ov2 = decrypt_instance.obis_values[obis_code2]
    assert isinstance(ov2, ObisValueFloat)
    assert ov2.value == 1000
    assert ov2.scale == 0
    assert ov2.unit == PhysicalUnits(int.from_bytes(b'\x21', "big"))
    
    # --- Verify Block 3 (EVN OctetString) parsing ---
    evn_obis_code = b"\x00\x00\x60\x01\x00\xff"
    assert evn_obis_code in decrypt_instance.obis

    # Update the expected value to a string if your production code is converting bytes to str.
    expected_octet_data = "abcdefghijkl"
    ov3 = decrypt_instance.obis_values[evn_obis_code]
    # If your ObisValueBytes returns the data as str
    assert isinstance(ov3, ObisValueBytes)
    assert ov3.value == expected_octet_data


