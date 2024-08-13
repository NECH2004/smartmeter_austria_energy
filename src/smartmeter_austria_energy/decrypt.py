"""Decrypts the smartmeter response frames."""

import binascii

from Crypto.Cipher import AES

from .constants import DataType, PhysicalUnits
from .obis import Obis
from .obisvalue import ObisValueFloat, ObisValueBytes
from .supplier import Supplier


# decryption class was mainly taken from and credits to https://github.com/tirolerstefan/kaifa
class Decrypt:
    """Decrypts the response frames."""

    def __init__(self, supplier: Supplier, frame1: bytes, frame2: bytes, key_hex_string: str):
        self.obis = {}
        self.obis_values = {}

        key = binascii.unhexlify(key_hex_string)  # convert to binary stream
        systitle = frame1[11:19]  # systitle at byte 12, length 8

        # invocation counter length 4
        ic = frame1[supplier.ic_start_byte : supplier.ic_start_byte + 4]
        iv = systitle + ic  # initialization vector

        # start at byte 26 or 27 (dep on supplier), excluding 2 bytes at end:
        # checksum byte, end byte 0x16
        data_frame1 = frame1[supplier.enc_data_start_byte : len(frame1) - 2]

        # start at byte 10, excluding 2 bytes at end:
        # checksum byte, end byte 0x16
        data_frame2 = frame2[9 : len(frame2) - 2]

        data_encrypted = data_frame1 + data_frame2
        cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
        self._data_decrypted = cipher.decrypt(data_encrypted)

    def parse_all(self):
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
                value = int.from_bytes(decrypted[pos : pos + 4], "big")
                scale = decrypted[pos + 4 + 3]
                if scale > 128:
                    scale -= 256
                unit = decrypted[pos + 4 + 3 + 2]
                pos += 2 + 8
                self.obis[obis_code] = value * (10**scale)

                self.obis_values[obis_code] = ObisValueFloat(
                    value, PhysicalUnits(unit), scale
                )
            elif data_type == DataType.LongUnsigned:
                value = int.from_bytes(decrypted[pos : pos + 2], "big")
                scale = decrypted[pos + 2 + 3]
                if scale > 128:
                    scale -= 256
                unit = decrypted[pos + 2 + 3 + 2]
                pos += 8
                self.obis[obis_code] = value * (10**scale)

                self.obis_values[obis_code] = ObisValueFloat(
                    value, PhysicalUnits(unit), scale
                )
            elif data_type == DataType.OctetString:
                octet_len = decrypted[pos]
                octet = decrypted[pos + 1 : pos + 1 + octet_len]
                pos += 1 + octet_len + 2
                self.obis[obis_code] = octet

                self.obis_values[obis_code] = ObisValueBytes(octet)

    def get_obis_value(self, name) -> ObisValueFloat | ObisValueBytes:
        """Fetch the value of the data structure using its key."""

        d = getattr(Obis, name)
        if d in self.obis_values:
            data = self.obis_values[d]
            return data

        return None
