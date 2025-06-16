"""Decrypts the smartmeter response frames."""

import binascii

from Crypto.Cipher import AES

from .constants import DataType, PhysicalUnits
from .obis import Obis
from .obisvalue import ObisValueBytes, ObisValueFloat
from .supplier import Supplier

# Constants for frame parsing
SYSTITLE_START: int = 11
SYSTITLE_LENGTH: int = 8

DOUBLELONG_SIZE: int = 4
LONG_SIZE: int = 2


# decryption class was mainly taken from and credits to https://github.com/tirolerstefan/kaifa
class Decrypt:
    """Decrypts the response frames."""

    def __init__(self, supplier: Supplier, frame1: bytes, frame2: bytes, key_hex_string: str)-> None:
        self.obis: dict[bytes, str | bytes] = {}
        self.obis_values: dict[bytes, ObisValueFloat | ObisValueBytes | None] = {}

        key = binascii.unhexlify(key_hex_string)  # convert to binary stream
        systitle = frame1[SYSTITLE_START : SYSTITLE_START + SYSTITLE_LENGTH]  # systitle at byte 12, length 8

        # invocation counter length 4
        ic = frame1[supplier.ic_start_byte : supplier.ic_start_byte + 4]

        # concatenating a system title and the invocation counter to form a nonce for AES GCM
        iv = systitle + ic # initialization vector

        # start at byte 26 or 27 (dep on supplier), excluding 2 bytes at end:
        # checksum byte, end byte 0x16
        data_frame1 = frame1[supplier.enc_data_start_byte : len(frame1) - 2]

        # start at byte 10, excluding 2 bytes at end:
        # checksum byte, end byte 0x16
        data_frame2 = frame2[9 : len(frame2) - 2]

        data_encrypted = data_frame1 + data_frame2
        cipher = AES.new(key=key, mode=AES.MODE_GCM, nonce=iv) # type: ignore
        self._data_decrypted = cipher.decrypt(data_encrypted)

    def parse_all(self)-> None:
        """Parse both frames."""

        decrypted = self._data_decrypted
        pos = 0
        total = len(decrypted)
        self.obis = {}
        self.obis_values = {}

        while pos < total:
            if decrypted[pos] != DataType.OctetString:
                pos += 1
                continue
            if decrypted[pos + 1] == 6:
                obis_code = decrypted[pos + 2 : pos + 2 + 6]
                data_type = decrypted[pos + 2 + 6]
                pos += 2 + 6 + 1
            elif decrypted[pos + 1] == 0xC and pos > 220:
                # EVN Device Name Emulation for OBIS 0-0:96.1.0.255
                obis_code = b"\x00\x00\x60\x01\x00\xff"
                data_type = DataType.OctetString
                pos += 1
            else:
                pos += 1
                continue

            if data_type == DataType.DoubleLongUnsigned:
                pos = self.__parse_DoubleLongUnsigned_DataType(decrypted, pos, obis_code)
            elif data_type == DataType.LongUnsigned:
                pos = self.__parse_LongUnsigned_DataType(decrypted, pos, obis_code)
            elif data_type == DataType.OctetString:
                pos = self.__parse_OctetString_DataType(decrypted, pos, obis_code)

    def __parse_DoubleLongUnsigned_DataType(self, decrypted: bytes, pos: int, obis_code: bytes) -> int:
        """Parse the DoubleLongUnsigned data type."""
        
        total_length = len(decrypted)
        bytes_needed = DOUBLELONG_SIZE
        if pos + bytes_needed > total_length:
            raise ValueError("Not enough data to read DoubleLongUnsigned value")

        value = int.from_bytes(decrypted[pos : pos + DOUBLELONG_SIZE], "big")

        # Check for the 'scale'. The scale is extracted from an offset (DOUBLELONG_SIZE +3 bytes beyond pos)
        scale_pos = pos + DOUBLELONG_SIZE + 3
        if scale_pos >= total_length:
            raise ValueError("Not enough data to read scale for DoubleLongUnsigned")
        
        scale = decrypted[scale_pos]
        if scale > 128:
            scale -= 256
        
        # Check for the 'unit' that comes after scale (offset 2 more)
        unit_pos = scale_pos + 2
        if unit_pos >= total_length:
            raise ValueError("Not enough data to read unit for DoubleLongUnsigned")
        
        unit = decrypted[unit_pos]

        pos += 2 + 8
        self.obis[obis_code] = value * (10 ** scale)

        self.obis_values[obis_code] = ObisValueFloat(value, PhysicalUnits(unit), scale)
        
        return pos

    def __parse_LongUnsigned_DataType(self, decrypted: bytes, pos: int, obis_code: bytes) -> int:
        """Parse the LongUnsigned data type."""

        total_length = len(decrypted)
        bytes_needed = LONG_SIZE
        if pos + bytes_needed > total_length:
            raise ValueError("Not enough data to read LongUnsigned value")

        value = int.from_bytes(decrypted[pos : pos + LONG_SIZE], "big")

        # Check for the 'scale'. The scale is extracted from an offset (LONG_SIZE +3 bytes beyond pos)
        scale_pos = pos + LONG_SIZE + 3
        if scale_pos >= total_length:
            raise ValueError("Not enough data to read scale for LongUnsigned")
        
        scale = decrypted[scale_pos]
        if scale > 128:
            scale -= 256

        # Check for the 'unit' that comes after scale (offset 2 more)
        unit_pos = scale_pos + 2
        if unit_pos >= total_length:
            raise ValueError("Not enough data to read unit for DoubleLongUnsigned")
        
        unit = decrypted[unit_pos]

        pos += 8
        self.obis[obis_code] = value * (10**scale)

        self.obis_values[obis_code] = ObisValueFloat(value, PhysicalUnits(unit), scale)
        
        return pos

    def __parse_OctetString_DataType(self, decrypted: bytes, pos: int, obis_code: bytes) -> int :
        """Parse the OctetString data type."""
        total_length = len(decrypted)
        
        # Check there is at least one byte available for the octet length.
        if pos >= total_length:
            raise ValueError("Not enough data to read the octet length for OctetString data type")        
        
        # Read the length of the octet string.
        octet_len = decrypted[pos]

        # Calculate the expected end position: 1 byte for the length, octet_len bytes for the data,
        # and an additional 2 bytes for checksum/end bytes.
        expected_end = pos + 1 + octet_len + 2
        if expected_end > total_length:
            raise ValueError("Not enough data to read the complete OctetString: expected end position {} but total length is {}".format(expected_end, total_length))
 
        octet = decrypted[pos + 1 : pos + 1 + octet_len]

        pos += 1 + octet_len + 2
        self.obis[obis_code] = octet

        self.obis_values[obis_code] = ObisValueBytes(octet)

        return pos

    def get_obis_value(self, name: str) -> ObisValueFloat | ObisValueBytes | None:
        """Fetch the value of the data structure using its key."""

        d = getattr(Obis, name)
        if d in self.obis_values:
            data = self.obis_values[d]
            return data

        return None
    