from unittest.mock import Mock

import pytest

from src.smartmeter_austria_energy.constants import DataType, PhysicalUnits
from src.smartmeter_austria_energy.decrypt import (
    SYSTITLE_LENGTH,
    SYSTITLE_START,
    Decrypt,
)
from src.smartmeter_austria_energy.obisvalue import ObisValueFloat


# --- Fixture for a supplier mock ---
@pytest.fixture
def supplier_mock()-> Mock:
    supplier = Mock()
    supplier.ic_start_byte = 0
    supplier.enc_data_start_byte = 0
    supplier.frame1_start_bytes = b"68fafa68"
    supplier.frame2_start_bytes = b"68727268"
    supplier.frame2_end_bytes = b"\x16"
    supplier.frame1_start_bytes_hex = "68fafa68"
    supplier.frame2_start_bytes_hex = "68727268"
    supplier.supplied_values = []
    return supplier

# --- Fixture for a Decrypt instance ---
@pytest.fixture
def decrypt_instance(supplier_mock: Mock) -> Decrypt:
    """ Create a Decrypt instance with a dummy frame for testing."""

    # Create a dummy frame with a length sufficient for systitle extraction.
    dummy_frame_length = SYSTITLE_START + SYSTITLE_LENGTH + 10
    dummy_frame = bytes([0] * dummy_frame_length)
    key_hex_string = "00112233445566778899aabbccddeeff"
    instance = Decrypt(supplier_mock, dummy_frame, dummy_frame, key_hex_string)
    
    # Clear any previously parsed data.
    instance.obis = {}
    instance.obis_values = {}
    
    return instance



def test_parse_all_doubleLongUnsigned_record(decrypt_instance: Decrypt)-> None:
    """
    This test provides a decrypted stream that contains a single record which, when parsed,
    enters the __parse_DoubleLongUnsigned_DataType branch.

    Record structure:
      Header (9 bytes):
        - Byte 0: DataType.OctetString
        - Byte 1: 6 (indicates that the next 6 bytes form the OBIS code)
        - Bytes 2-7: OBIS code (choose, e.g., b'\x11'*6)
        - Byte 8: DataType.DoubleLongUnsigned    (forces use of __parse_DoubleLongUnsigned_DataType)
      Body (10 bytes):
        - Bytes 0-3: 4-byte value; here b'\x00\x00\x03\xe8' which equals 1000.
        - Bytes 4-6: 3 dummy/filler bytes (arbitrary, e.g. b'\xAA\xAA\xAA')
        - Byte 7: Scale (0)
        - Byte 8: Dummy (e.g. b'\xBB')
        - Byte 9: Unit, e.g. b'\x21'
        
    Total record length: 9 + 10 = 19 bytes.
    
    After parse_all() is run, the OBIS dictionary should have the key (the OBIS code)
    mapping to the value 1000 and obis_values should contain an ObisValueFloat with that data.
    """
    obis_code = b'\x11' * 6
    header = bytes([DataType.OctetString, 6]) + obis_code + bytes([DataType.DoubleLongUnsigned])
    body = (
        b'\x00\x00\x03\xe8'   # 4-byte value (1000)
        + b'\xAA\xAA\xAA'     # 3 dummy bytes
        + b'\x00'             # scale = 0
        + b'\xBB'             # dummy byte
        + b'\x21'             # unit byte (0x21)
    )
    record = header + body  # total = 19 bytes

    # Use this record as the complete decrypted stream.
    decrypt_instance._data_decrypted = record # type: ignore
    decrypt_instance.obis = {}
    decrypt_instance.obis_values = {}

    decrypt_instance.parse_all()

    # Verify that the OBIS code is in the dictionary, with value 1000.
    assert obis_code in decrypt_instance.obis, "DoubleLongUnsigned record: OBIS code not present."
    assert decrypt_instance.obis[obis_code] == 1000, "DoubleLongUnsigned record: Value mismatch."
    ov = decrypt_instance.obis_values[obis_code]
    assert isinstance(ov, ObisValueFloat), "DoubleLongUnsigned record: Expected ObisValueFloat instance."
    assert ov.value == 1000, "DoubleLongUnsigned record: Incorrect stored value."
    expected_unit = PhysicalUnits(int.from_bytes(b'\x21', "big"))
    assert ov.unit == expected_unit, "DoubleLongUnsigned record: Unit mismatch."
    assert ov.scale == 0, "DoubleLongUnsigned record: Scale mismatch."

def test_parse_all_longUnsigned_record(decrypt_instance: Decrypt)-> None:
    """
    This test provides a decrypted stream that contains a single record which, when parsed,
    enters the _parse_LongUnsigned_DataType branch.

    Record structure:
      Header (9 bytes):
        - Byte 0: DataType.OctetString
        - Byte 1: 6 (indicates that the next 6 bytes form the OBIS code)
        - Bytes 2-7: OBIS code (choose, e.g., b'\x22'*6)
        - Byte 8: DataType.LongUnsigned        (forces use of _parse_LongUnsigned_DataType)
      Body (8 bytes):
        - Bytes 0-1: 2-byte value; here b'\x03\xe8' equals 1000.
        - Bytes 2-4: 3 dummy bytes (e.g. b'\xAA\xAA\xAA')
        - Byte 5: Scale (0)
        - Byte 6: Dummy (e.g. b'\xBB')
        - Byte 7: Unit; e.g. b'\x21'
      
    Total record length: 9 + 8 = 17 bytes.
  
    After parse_all() is run, the OBIS dictionary should have the key mapping to 1000 and obis_values
    should contain an ObisValueFloat with the appropriate data.
    """
    obis_code = b'\x22' * 6
    header = bytes([DataType.OctetString, 6]) + obis_code + bytes([DataType.LongUnsigned])
    body = (
        b'\x03\xe8'          # 2-byte value (1000)
        + b'\xAA\xAA\xAA'     # 3 dummy bytes
        + b'\x00'             # scale = 0
        + b'\xBB'             # dummy byte
        + b'\x21'             # unit byte (0x21)
    )
    record = header + body  # total = 17 bytes

    decrypt_instance._data_decrypted = record # type: ignore
    decrypt_instance.obis = {}
    decrypt_instance.obis_values = {}

    decrypt_instance.parse_all()

    assert obis_code in decrypt_instance.obis, "LongUnsigned record: OBIS code not present."
    assert decrypt_instance.obis[obis_code] == 1000, "LongUnsigned record: Value mismatch."
    ov = decrypt_instance.obis_values[obis_code]
    assert isinstance(ov, ObisValueFloat), "LongUnsigned record: Expected ObisValueFloat instance."
    assert ov.value == 1000, "LongUnsigned record: Incorrect stored value."
    expected_unit = PhysicalUnits(int.from_bytes(b'\x21', "big"))
    assert ov.unit == expected_unit, "LongUnsigned record: Unit mismatch."
    assert ov.scale == 0, "LongUnsigned record: Scale mismatch."

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



# ------------------------------------------------------------------------------
# Test 1: Everything is fine.
# ------------------------------------------------------------------------------
def test_doubleLongUnsigned_normal(decrypt_instance: Decrypt)-> None:
    """
    Assemble a decrypted stream for the __parse_DoubleLongUnsigned_DataType branch in normal mode.
    Expected structure (total length = 10 bytes):
      - Bytes [0:4]: 4-byte value: b'\x00\x00\x03\xe8', which equals 1000.
      - Bytes [4:7]: 3 dummy bytes (e.g. b'\xAA\xAA\xAA')
      - Byte [7]: scale byte = 0x00 (scale = 0)
      - Byte [8]: a dummy filler (e.g. b'\xBB')
      - Byte [9]: unit byte, e.g. b'\x21'
    
    The function then does:
      pos += (2 + 8) = 10, stores:
         self.obis[obis_code] = 1000 * (10**0) → 1000
         self.obis_values[obis_code] = ObisValueFloat(1000, PhysicalUnits(0x21), 0)
    """
    # Build the stream.
    value_bytes = b'\x00\x00\x03\xe8'         # 4 bytes = 1000.
    filler = b'\xAA\xAA\xAA'                   # 3 bytes filler.
    scale_byte = b'\x00'                       # scale = 0.
    dummy2 = b'\xBB'                           # dummy filler.
    unit_byte = b'\x21'                        # unit.
    decrypted_stream = value_bytes + filler + scale_byte + dummy2 + unit_byte  # total = 10 bytes.
    
    obis_code = b'\x11\x11\x11\x11\x11\x11'     # arbitrary OBIS code.
    
    new_pos = decrypt_instance._Decrypt__parse_DoubleLongUnsigned_DataType(decrypted_stream, 0, obis_code) # type: ignore
    assert new_pos == 10, "Expected new position to be 10 in normal branch."
    assert obis_code in decrypt_instance.obis
    assert decrypt_instance.obis[obis_code] == 1000, "Normal branch: value should be 1000."
    
    ov = decrypt_instance.obis_values[obis_code]
    assert isinstance(ov, ObisValueFloat)
    assert ov.value == 1000
    expected_unit = PhysicalUnits(int.from_bytes(unit_byte, "big"))
    assert ov.unit == expected_unit
    assert ov.scale == 0

# ------------------------------------------------------------------------------
# Test 2: Scale > 128 branch.
# ------------------------------------------------------------------------------
def test_doubleLongUnsigned_scale_adjust(decrypt_instance: Decrypt)-> None:
    """
    Same as test 1 but the scale byte is > 128.
    
    We supply a scale byte of 130 (0x82). In the code:
       if scale > 128:
           scale -= 256
    So the effective scale becomes 130 - 256 = -126.
    The value remains 1000, so self.obis[obis_code] should be 1000 * 10^(-126).
    (Since 10**(-126) is a very small number, we're more interested in checking that
     the ObisValueFloat's scale field is -126.)
    """
    value_bytes = b'\x00\x00\x03\xe8'         # 1000.
    filler = b'\xAA\xAA\xAA'
    scale_byte = bytes([130])                  # 130 > 128.
    dummy2 = b'\xBB'
    unit_byte = b'\x21'
    decrypted_stream = value_bytes + filler + scale_byte + dummy2 + unit_byte  # total = 10 bytes.
    
    obis_code = b'\x12\x12\x12\x12\x12\x12'
    new_pos = decrypt_instance._Decrypt__parse_DoubleLongUnsigned_DataType(decrypted_stream, 0, obis_code) # type: ignore
    assert new_pos == 10, "Expected new position to be 10."
    
    # Check that scale was adjusted:
    ov = decrypt_instance.obis_values[obis_code]
    assert isinstance(ov, ObisValueFloat)
    assert ov.scale == -126, "Scale should be adjusted to -126."
    # Also, self.obis[obis_code] should reflect the multiplication
    expected = 1000 * (10 ** (-126))
    assert decrypt_instance.obis[obis_code] == expected

# ------------------------------------------------------------------------------
# Test 3: Raise ValueError for insufficient bytes to read value.
# ------------------------------------------------------------------------------
def test_doubleLongUnsigned_insufficient_value(decrypt_instance: Decrypt)-> None:
    """
    Test the branch where there are not even enough bytes to read the required 4-byte value.
    The function expects at least 4 bytes starting at pos. Set the stream shorter than that.
    """
    decrypted_stream = b'\x00\x00'  # Only 2 bytes; needs at least 4.
    obis_code = b'\x33\x33\x33\x33\x33\x33'
    with pytest.raises(ValueError, match="Not enough data to read DoubleLongUnsigned value"):
        decrypt_instance._Decrypt__parse_DoubleLongUnsigned_DataType(decrypted_stream, 0, obis_code) # type: ignore

# ------------------------------------------------------------------------------
# Test 4: Raise ValueError for insufficient bytes to read unit.
# ------------------------------------------------------------------------------
def test_doubleLongUnsigned_insufficient_unit(decrypt_instance: Decrypt)-> None:
    """
    Build a stream that supplies the 4-byte value, 3 filler bytes, and the scale byte,
    but then does not provide enough bytes for reading the unit (the method expects unit_pos = pos+4+3+2).
    
    For pos=0, value requires 4 bytes, filler 3 bytes, one scale byte = 8 bytes total before unit.
    For unit, index should be 8+? Actually:
       scale_pos = 0 + 4 + 3 = 7 (valid if total length > 7)
       unit_pos = 7 + 2 = 9.
    Let's build a stream of 9 bytes only.
    """
    # We'll assemble:
    # 4 bytes for value, 3 bytes filler, 1 byte for scale; total = 8 bytes.
    # We intentionally do not supply the 9th byte.
    value_bytes = b'\x00\x00\x03\xe8'         # 4 bytes.
    filler = b'\xAA\xAA\xAA'                   # 3 bytes.
    scale_byte = b'\x00'                       # scale.
    decrypted_stream = value_bytes + filler + scale_byte  # Total = 4+3+1 = 8 bytes.
    
    obis_code = b'\x44\x44\x44\x44\x44\x44'
    with pytest.raises(ValueError, match="Not enough data to read unit for DoubleLongUnsigned"):
        decrypt_instance._Decrypt__parse_DoubleLongUnsigned_DataType(decrypted_stream, 0, obis_code) # type: ignore

  
def test_doubleLongUnsigned_insufficient_scale(decrypt_instance: Decrypt)-> None:
    """
    Test the branch where there are not enough bytes to read the scale for DoubleLongUnsigned.

    For pos = 0 and DOUBLELONG_SIZE = 4, scale_pos is 7.
    We supply exactly 7 bytes in the stream:
      - 4 bytes for the value (e.g. b'\x00\x00\x03\xe8' for 1000)
      - 3 bytes filler (dummy) 
    Total = 7 bytes. This is enough to read the value, but not enough to access the byte at index 7,
    thus triggering the ValueError about insufficient data to read scale.
    """
    # 4 bytes value = 1000.
    value_bytes = b'\x00\x00\x03\xe8'
    # 3 filler bytes; total stream length = 4 + 3 = 7.
    filler = b'\xAA\xAA\xAA'
    decrypted_stream = value_bytes + filler  # total length = 7
    
    obis_code = b'\x55\x55\x55\x55\x55\x55'
    
    with pytest.raises(ValueError, match="Not enough data to read scale for DoubleLongUnsigned"):
        decrypt_instance._Decrypt__parse_DoubleLongUnsigned_DataType(decrypted_stream, 0, obis_code) # type: ignore


# ================================================================
# Test 1: Normal case for _parse_LongUnsigned_DataType
# ================================================================
def test_longUnsigned_normal(decrypt_instance: Decrypt)-> None:
    value_bytes = b'\x03\xe8'          # 2-byte value for 1000.
    filler = b'\xAA\xAA\xAA'           # 3 dummy bytes.
    scale_byte = b'\x00'               # scale 0.
    dummy2 = b'\xBB'                   # dummy filler.
    unit_byte = b'\x21'                # unit.
    stream = value_bytes + filler + scale_byte + dummy2 + unit_byte  # Total = 8 bytes.
    
    obis_code = b'\x22' * 6            # arbitrary OBIS code.
    new_pos = decrypt_instance._Decrypt__parse_LongUnsigned_DataType(stream, 0, obis_code) # type: ignore
    # _parse_LongUnsigned_DataType increments pos by 8.
    assert new_pos == 8, "Expected new position to be 8 in the normal branch."
    
    # Compute value 1000 * (10 ** 0)
    assert obis_code in decrypt_instance.obis
    assert decrypt_instance.obis[obis_code] == 1000, "Normal branch: Value mismatch."
    
    ov = decrypt_instance.obis_values[obis_code]
    assert isinstance(ov, ObisValueFloat)
    assert ov.value == 1000, "Normal branch: Stored value is incorrect."
    expected_unit = PhysicalUnits(int.from_bytes(unit_byte, "big"))
    assert ov.unit == expected_unit, "Normal branch: Unit mismatch."
    assert ov.scale == 0, "Normal branch: Scale should be 0."


# ================================================================
# Test 2: Scale > 128 branch for _parse_LongUnsigned_DataType
# ================================================================
def test_longUnsigned_scale_adjust(decrypt_instance: Decrypt)-> None:
    # Use same structure as normal test except scale byte is set to 130.
    value_bytes = b'\x03\xe8'          # 1000.
    filler = b'\xAA\xAA\xAA'
    # scale byte: 130. Since 130 > 128, effective scale becomes 130 - 256 = -126.
    scale_byte = bytes([130])
    dummy2 = b'\xBB'
    unit_byte = b'\x21'
    stream = value_bytes + filler + scale_byte + dummy2 + unit_byte
    
    obis_code = b'\x33' * 6
    new_pos = decrypt_instance._Decrypt__parse_LongUnsigned_DataType(stream, 0, obis_code) # type: ignore
    assert new_pos == 8, "Scale adjust branch: new position should be 8."
    
    ov = decrypt_instance.obis_values[obis_code]
    assert isinstance(ov, ObisValueFloat)
    assert ov.scale == -126, "Expected scale to be adjusted to -126."
    # Here, value remains 1000, so expected stored value = 1000 * 10^(-126)
    expected_value = 1000 * (10 ** (-126))
    assert decrypt_instance.obis[obis_code] == expected_value

# ================================================================
# Test 3: Insufficient bytes to read value (needs at least 2 bytes)
# ================================================================
def test_longUnsigned_insufficient_value(decrypt_instance: Decrypt)-> None:
    # Provide a stream with fewer than 2 bytes.
    stream = b'\x03'  # only one byte
    obis_code = b'\x44' * 6
    with pytest.raises(ValueError, match="Not enough data to read LongUnsigned value"):
        decrypt_instance._Decrypt__parse_LongUnsigned_DataType(stream, 0, obis_code) # type: ignore

# ================================================================
# Test 4: Insufficient bytes to read scale for LongUnsigned
# ================================================================
def test_longUnsigned_insufficient_scale(decrypt_instance: Decrypt)-> None:
    """
    For pos=0 and LONG_SIZE=2, scale_pos = 0+2+3 = 5.
    Provide a stream with total length <= 5 so that reading the scale fails.
    """
    # Provide exactly 5 bytes.
    stream = b'\x03\xe8' + b'\xAA\xAA\xAA'[:1]  # 2 bytes + 1 byte filler = 3 bytes; then add 2 more bytes → total = 5 bytes.
    # To be explicit, let's set stream = 5 bytes.
    stream = b'\x03\xe8' + b'\xAA\xAA\xAA'[:1] + b'\xAA'  # That gives 2 + 1 + 1 = 4 bytes?  Let's do this clearly:
    # We need exactly 5 bytes. One way is: 2 bytes for value, then 3 dummy bytes.
    stream = b'\x03\xe8' + b'\xAA\xAA\xAA'
    # Total length = 2 + 3 = 5.
    obis_code = b'\x55' * 6
    with pytest.raises(ValueError, match="Not enough data to read scale for LongUnsigned"):
        decrypt_instance._Decrypt__parse_LongUnsigned_DataType(stream, 0, obis_code) # type: ignore

# ================================================================
# Test 5: Insufficient bytes to read unit for LongUnsigned.
# ================================================================
def test_longUnsigned_insufficient_unit(decrypt_instance: Decrypt)-> None:
    """
    For pos = 0, LONG_SIZE = 2 -> value occupies indices [0,1].
    Then filler (3 bytes) occupies indices [2,3,4].
    The scale byte is at index 5, then unit is expected at index 7 (because unit_pos = scale_pos +2, scale_pos= 0+2+3=5).
    Provide a stream that has exactly 7 bytes so that the unit cannot be read.
    """
    # Build the stream: 2 bytes value, 3 filler, 1 byte scale → total 6 bytes so far,
    # then one dummy byte to bring total length to 7.
    stream = b'\x03\xe8' + b'\xAA\xAA\xAA' + b'\x00' + b'\xBB'
    # Total length = 2 + 3 + 1 + 1 = 7 bytes, so index 7 (unit byte) is missing.
    obis_code = b'\x66' * 6
    with pytest.raises(ValueError, match="Not enough data to read unit for DoubleLongUnsigned"):
        decrypt_instance._Decrypt__parse_LongUnsigned_DataType(stream, 0, obis_code) # type: ignore


# -------------------------------------------------------------------------
# Test 1: Normal case – octet length > 0
# -------------------------------------------------------------------------
def test__octetString_normal(decrypt_instance: Decrypt)-> None:
    """
    Construct a stream for a normal OctetString record.
    
    Let the octet length L be 3. Then the stream should be:
      - Byte [0]: L (i.e. 3)
      - Bytes [1:4]: The payload (e.g. b"abc")
      - Bytes [4:6]: Two termination bytes (e.g. b'\x00\x16')
    
    Total length = 1 + 3 + 2 = 6.
    The function should return pos + 6 (i.e. 6) and store the payload.
    """
    octet_len = 3
    payload = b"abc"
    termination = b'\x00\x16'
    decrypted_stream = bytes([octet_len]) + payload + termination  # 6 bytes total.
    
    obis_code = b'\x11' * 6
    
    new_pos = decrypt_instance._Decrypt__parse_OctetString_DataType(decrypted_stream, 0, obis_code) # type: ignore
    assert new_pos == 6, "Normal case: Expected new position to be 6."
    
    # The function stores the payload to both dictionaries.
    assert obis_code in decrypt_instance.obis
    assert decrypt_instance.obis[obis_code] == payload
    ov = decrypt_instance.obis_values[obis_code]
    # We assume ObisValueBytes stores the raw payload in an attribute named either 'value' or 'raw_value'
    if hasattr(ov, "raw_value"):
        assert ov.raw_value == payload # type: ignore
    else:
        assert ov.value == payload # type: ignore

# -------------------------------------------------------------------------
# Test 2: Edge Case – Zero-Length OctetString
# -------------------------------------------------------------------------
def test__octetString_zero_length(decrypt_instance: Decrypt)-> None:
    """
    Test the branch where the octet length is zero.
    
    Then the stream should be:
      - Byte [0]: 0 (length)
      - There is no payload (empty)
      - Followed by 2 termination bytes.
    
    Total length required = 1 + 0 + 2 = 3.
    The function should return pos + 3 (i.e. 3) and store an empty payload.
    """
    octet_len = 0
    payload = b""  # No payload bytes.
    termination = b'\x00\x16'
    decrypted_stream = bytes([octet_len]) + payload + termination  # Total = 3 bytes.
    
    obis_code = b'\x22' * 6
    new_pos = decrypt_instance._Decrypt__parse_OctetString_DataType(decrypted_stream, 0, obis_code) # type: ignore
    assert new_pos == 3, "Zero-length case: Expected new position to be 3."
    
    assert obis_code in decrypt_instance.obis # type: ignore
    assert decrypt_instance.obis[obis_code] == b"" # type: ignore
    ov = decrypt_instance.obis_values[obis_code] # type: ignore
    if hasattr(ov, "raw_value"):
        assert ov.raw_value == b"" # type: ignore
    else:
        assert ov.value == b"" # type: ignore

# -------------------------------------------------------------------------
# Test 3: Insufficient Bytes to Read the Octet Length
# -------------------------------------------------------------------------
def test__octetString_insufficient_length_byte(decrypt_instance: Decrypt)-> None:
    """
    Test the branch where there is no byte available at pos to read the octet length.
    
    For instance, if the decrypted stream is empty.
    """
    decrypted_stream = b""  # Empty stream.
    obis_code = b'\x33' * 6
    with pytest.raises(ValueError, match="Not enough data to read the octet length for OctetString data type"):
        decrypt_instance._Decrypt__parse_OctetString_DataType(decrypted_stream, 0, obis_code) # type: ignore

# -------------------------------------------------------------------------
# Test 4: Insufficient Bytes for Complete OctetString
# -------------------------------------------------------------------------
def test__octetString_insufficient_complete_stream(decrypt_instance: Decrypt)-> None:
    """
    Test the branch where the stream does not have enough bytes to cover the entire OctetString.
    
    For a given octet length L, the function expects the stream to have at least:
         pos + 1 + L + 2 bytes.
    For example, let L = 3; then expected_end = 0 + 1 + 3 + 2 = 6.
    Provide a stream whose total length is less than 6.
    
    In this test, we provide only 5 bytes.
    """
    octet_len = 3
    payload = b"abc"  # 3 bytes payload.
    termination = b'\x00'  # Only 1 termination byte instead of 2.
    # Total length = 1 + 3 + 1 = 5, but expected_end = 6.
    decrypted_stream = bytes([octet_len]) + payload + termination
    obis_code = b'\x44' * 6
    with pytest.raises(ValueError, match="Not enough data to read the complete OctetString: expected end position 6 but total length is 5"):
        decrypt_instance._Decrypt__parse_OctetString_DataType(decrypted_stream, 0, obis_code) # type: ignore