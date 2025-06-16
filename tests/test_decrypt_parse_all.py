from unittest.mock import Mock

import pytest

from src.smartmeter_austria_energy.constants import DataType
from src.smartmeter_austria_energy.decrypt import (
    SYSTITLE_LENGTH,
    SYSTITLE_START,
    Decrypt,
)
from src.smartmeter_austria_energy.obisvalue import ObisValueBytes


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

# -------------------------------------------------------------------------
# Test 1: Normal branch – header with second byte equal to 6
# -------------------------------------------------------------------------
def test_parse_all_normal_branch(decrypt_instance: Decrypt)-> None:
    """
    Builds a decrypted stream triggering the normal OctetString branch.
    
    The stream is:
      Byte 0: DataType.OctetString             (record trigger)
      Byte 1: 6                                (indicates that bytes 2–7 form the OBIS code)
      Bytes 2–7: OBIS code (e.g. b'\x11\x11\x11\x11\x11\x11')
      Byte 8: DataType.OctetString             (payload’s data type)
      Byte 9: Payload length (e.g. 3)
      Bytes 10–12: Payload (e.g. b"abc")
      Bytes 13–14: Two termination bytes (for example, b'\x00\x16')
      (Can append extra bytes if desired)
    
    Afterwards, the OBIS code should map to the payload b"abc".
    """
    normal_stream = (
        bytes([DataType.OctetString, 6]) +         # Header: marker and length indicator
        b'\x11\x11\x11\x11\x11\x11' +                # 6-byte OBIS code
        bytes([DataType.OctetString, 3]) +           # Payload header: marker and payload length (3)
        b'abc' +                                   # 3-byte payload
        b'\x00\x16'                                # 2 termination bytes
    )
    normal_stream += b'\x00\x00'  # Optional extra bytes.

    decrypt_instance._data_decrypted = normal_stream # type: ignore
    decrypt_instance.obis = {}
    decrypt_instance.obis_values = {}

    decrypt_instance.parse_all()

    expected_obis = b'\x11\x11\x11\x11\x11\x11'
    assert expected_obis in decrypt_instance.obis, "Normal branch: OBIS code not found."
    assert decrypt_instance.obis[expected_obis] == b'abc', "Normal branch: Payload mismatch."
    ov = decrypt_instance.obis_values[expected_obis]
    assert isinstance(ov, ObisValueBytes), "Normal branch: Expected ObisValueBytes instance."
    if hasattr(ov, "raw_value"):
        assert ov.raw_value == b'abc'
    else:
        assert ov.value == b'abc'

# -------------------------------------------------------------------------
# Test 2: EVN Device Name Emulation branch – header with second byte 0xC triggers EVN branch.
# -------------------------------------------------------------------------
def test_parse_all_evn_branch(decrypt_instance: Decrypt)-> None:
    """
    Builds a decrypted stream to trigger the EVN Device Name Emulation branch.
    
    Requirements:
      - The parsing position must exceed 220.
      - Then a header is encountered where:
            Byte 0 = DataType.OctetString
            Byte 1 = 0xC  (which equals 12)
      - In this branch, the code sets:
            obis_code = b"\x00\x00\x60\x01\x00\xff"
            data_type = DataType.OctetString, and does: pos += 1.
        Thus, the second header byte (0xC) is interpreted as the octet-string length.
      - Immediately following, __parse_OctetString_DataType reads:
            octet_len = 0xC (i.e., 12), then reads 12 bytes of payload,
            and expects 2 termination bytes.
    
    We build the EVN block as:
      EVN header: 2 bytes → [DataType.OctetString, 0xC]
      Payload: 12 bytes (e.g., b"xyzxyzxyzxyz")
      Termination: 2 bytes (e.g., b'\x00\x16')
      → EVN block length = 2 + 12 + 2 = 16 bytes.
    
    Prepend a filler of 221 bytes to ensure the block starts after position 220.
    After parsing, the fixed OBIS code (b"\x00\x00\x60\x01\x00\xff") should map to the payload.
    """
    filler = b'\x00' * 221  # Guarantee pos > 220.
    evn_header = bytes([DataType.OctetString, 0xC])  # 0xC will be interpreted as 12.
    payload = b'xyzxyzxyzxyz'  # 12 bytes.
    termination = b'\x00\x16'  # 2 termination bytes.
    # No extra length byte is added.
    evn_block = evn_header + payload + termination  # Total = 2 + 12 + 2 = 16 bytes.
    full_stream = filler + evn_block  # Total stream length = 221 + 16 = 237 bytes.

    decrypt_instance._data_decrypted = full_stream # type: ignore
    decrypt_instance.obis = {}
    decrypt_instance.obis_values = {}

    decrypt_instance.parse_all()

    expected_fixed_obis = b"\x00\x00\x60\x01\x00\xff"
    assert expected_fixed_obis in decrypt_instance.obis, "EVN branch: Fixed OBIS code not found."
    # __parse_OctetString_DataType should read length from decrypted[222] (which is 0xC = 12)
    # and then payload from decrypted[223:223+12], yielding our payload.
    assert decrypt_instance.obis[expected_fixed_obis] == payload, "EVN branch: Payload mismatch."
    ov = decrypt_instance.obis_values[expected_fixed_obis]
    assert isinstance(ov, ObisValueBytes), "EVN branch: Expected ObisValueBytes instance."
    if hasattr(ov, "raw_value"):
        assert ov.raw_value == payload, "EVN branch: Stored raw value mismatch."
    else:
        assert ov.value == payload, "EVN branch: Stored value mismatch."


def test_parse_all_no_valid_header(decrypt_instance: Decrypt)-> None:
    """
    Build a decrypted stream that does not contain any valid record.

    In the parse_all() loop the very first check is:
      if decrypted[pos] != DataType.OctetString:
         pos += 1
         continue

    This test uses a stream where every byte is different from DataType.OctetString,
    so the parser skips the entire stream without parsing any record.
    
    After parse_all() finishes, obis and obis_values should remain empty.
    """
    # Choose a byte that is guaranteed not to be equal to DataType.OctetString.
    # For example, if DataType.OctetString is not zero, we can use zero.
    invalid_marker = 0 if DataType.OctetString != 0 else 0xFF # type: ignore
    # Build a stream (say 50 bytes) filled with the invalid marker.
    stream = bytes([invalid_marker]) * 50

    decrypt_instance._data_decrypted = stream # type: ignore
    decrypt_instance.obis = {}
    decrypt_instance.obis_values = {}

    # Execute the parser. It should not raise an exception.
    decrypt_instance.parse_all()

    # Assert that nothing was parsed.
    assert decrypt_instance.obis == {}, "Expected no OBIS entries when no valid headers exist."
    assert decrypt_instance.obis_values == {}, "Expected no OBIS values when no valid headers exist."


def test_parse_all_unrecognized_header(decrypt_instance: Decrypt)-> None:
    """
    Build a decrypted stream that contains a header with:
      - Byte 0: equal to DataType.OctetString (so it qualifies for header checking)
      - Byte 1: a value (for example, 5) that is neither 6 nor 0xC.
      
    In that case, the code falls to the else clause of the header check,
    does pos += 1, and continues without parsing any record.
    
    After running parse_all(), the obis and obis_values dictionaries should remain empty.
    """
    # Construct a stream:
    # First two bytes: [DataType.OctetString, 5] (5 is not 6 and not 0xC)
    # Followed by some arbitrary bytes.
    stream = bytes([DataType.OctetString, 5]) + b'\xAA' * 20

    decrypt_instance._data_decrypted = stream # type: ignore
    decrypt_instance.obis = {}
    decrypt_instance.obis_values = {}

    # Run the parser.
    decrypt_instance.parse_all()

    # Since the header is unrecognized, no record should be parsed.
    assert decrypt_instance.obis == {}, "Expected no OBIS entries for unrecognized header."
    assert decrypt_instance.obis_values == {}, "Expected no OBIS values for unrecognized header."


def test_parse_all_unknown_data_type(decrypt_instance: Decrypt)-> None:
    """
    This test builds a decrypted stream that contains a record header with a valid OBIS code,
    but an unknown data type value. The header is constructed as follows:
    
      - Byte 0: DataType.OctetString (so that the record branch is entered)
      - Byte 1: 6  (indicates that bytes 2-7 form the OBIS code)
      - Bytes 2-7: An OBIS code (for example, b'\x55'*6)
      - Byte 8: An unknown data type (choose a value not equal to
                DataType.DoubleLongUnsigned, DataType.LongUnsigned, or DataType.OctetString,
                for example, 99)
    
    Since the header is valid but the data type is not recognized, no branch in the data-type
    selection (the "if data_type == ..." block) will execute. The function then reaches the end
    of the iteration and continues with pos incremented by 9 (the header length).
    
    After parse_all() completes, no OBIS record should have been parsed; hence the obis and
    obis_values dictionaries should remain empty.
    """
    # Build the header:
    header = (
        bytes([DataType.OctetString, 6]) +  # Byte 0 and Byte 1
        b'\x55' * 6 +                     # Bytes 2-7: OBIS code (for example, b'\x55'*6)
        bytes([99])                       # Byte 8: unknown data type (99 is not recognized)
    )
    # We can append some extra bytes to the stream if desired.
    extra = b'\x00' * 5
    stream = header + extra
    
    # Set up the instance:
    decrypt_instance._data_decrypted = stream # type: ignore
    decrypt_instance.obis = {}
    decrypt_instance.obis_values = {}
    
    decrypt_instance.parse_all()
    
    # Since unknown data type did not match any if/elif clause, nothing should be stored.
    assert decrypt_instance.obis == {}, "No OBIS records should be parsed for unknown data type."
    assert decrypt_instance.obis_values == {}, "No OBIS value entries should be stored for unknown data type."
    