import re
import time
from unittest.mock import MagicMock, Mock

from _pytest.monkeypatch import MonkeyPatch
import pytest

# Import serial exceptions.
from src.smartmeter_austria_energy.smartmeter import Smartmeter
from src.smartmeter_austria_energy.supplier import Supplier
from src.smartmeter_austria_energy.exceptions import SmartmeterException


class DummySupplier(Supplier):
    """Dummy Supplier class to simulate the expected attributes for Smartmeter."""

    def __init__(self)-> None:
        # Minimal attributes expected by Smartmeter:
        self.frame1_start_bytes = b"68fafa68"
        self.frame2_start_bytes = b"68727268"
        self.frame2_end_bytes = b"\x16"
        self.frame1_start_bytes_hex = "68fafa68"
        self.frame2_start_bytes_hex = "68727268"
        self.supplied_values = []  # For OBISData

# A dummy serial class to simulate reading.
class DummySerialForRead:
    """Dummy Serial class to simulate reading from a serial port."""

    def __init__(self, stream: bytes) -> None:
        self.stream = stream
        self.call_count = 0

    def isOpen(self) -> bool:
        return True

    @property
    def is_open(self) -> bool:
        return self.isOpen()

    def inWaiting(self) -> int:
        if self.call_count == 0:
            self.call_count += 1
            return len(self.stream)
        return 0

    def read(self, n: int) -> bytes:
        if self.stream:
            ret = self.stream
            self.stream = b""
            return ret
        return b""

    def close(self) -> None:
        # no-op; simulates closing the port.
        pass


# Dummy Decrypt still uses the constructor.
class DummyDecrypt:
    """Dummy Decrypt class to simulate decryption."""
    
    # This class is a placeholder to simulate the decryption process.
    def __init__(self, supplier: Supplier, frame1: bytes, frame2: bytes, key_hex_string: str)-> None:
        self.supplier: Supplier = supplier
        self.frame1:bytes = frame1
        self.frame2:bytes = frame2
        self.key_hex_string:str = key_hex_string
    
    def parse_all(self)-> None:
        pass


# Pytest fixture for a Smartmeter instance using DummySupplier.
@pytest.fixture
def smartmeter_instance()-> Smartmeter:
    """Create a Smartmeter instance with a dummy supplier and minimal configuration."""
    
    supplier = DummySupplier()
    sm = Smartmeter(
        supplier=supplier,
        port="COM1",
        key_hex_string="00112233445566778899aabbccddeeff",
        interval=1  # Using 1 sec interval for simplicity.
    )
    # Replace logger with MagicMock to suppress/log checks.
    sm._logger = MagicMock() # type: ignore
    return sm

# --- Supplier fixture, in case it's not already defined ---
@pytest.fixture
def supplier_mock():
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



###############################
# Tests for Smartmeter.read() #
###############################

def test_read_already_running(smartmeter_instance: Smartmeter)-> None:
    """
    When _is_running is already True, read() should immediately return None.
    """
    smartmeter_instance._is_running = True # type: ignore

    with pytest.raises(SmartmeterException) as excinfo: # type: ignore
        smartmeter_instance.read()


def test_read_success(monkeypatch: MonkeyPatch, smartmeter_instance: Smartmeter)-> None:
    """
    Test a successful read path where two complete telegrams are received.
    We patch serial.Serial (not __open_serial) so that no real device is opened.
    """
    supplier = smartmeter_instance._supplier # type: ignore

    # Construct a dummy stream that contains:
    #   - frame1_start_bytes
    #   - A payload (here: b"payload1")
    #   - frame2_start_bytes
    #   - Another payload (here: b"payload2")
    #   - frame2_end_bytes at the end.
    stream = (supplier.frame1_start_bytes +
              b"payload1" +
              supplier.frame2_start_bytes +
              b"payload2" +
              supplier.frame2_end_bytes)
    
    # Create a dummy serial object which returns our stream when read.
    dummy_serial = DummySerialForRead(stream)
    
    # Patch serial.Serial so that __open_serial() uses our dummy.
    monkeypatch.setattr("src.smartmeter_austria_energy.smartmeter.serial.Serial", lambda *args, **kwargs: dummy_serial) # type: ignore
    
    # Override time.sleep to avoid delays.
    monkeypatch.setattr(time, "sleep", lambda x: None) # type: ignore
    
    # To simulate valid telegram splitting, patch re.split to return the expected parts:
    # For example, let re.split return a list that alternates between frame markers and payloads.
    monkeypatch.setattr(re, "split", lambda regex, s: [ # type: ignore
        supplier.frame1_start_bytes,
        b"payload1",
        supplier.frame2_start_bytes,
        b"payload2",
    ])
    
    # Create a dummy Decrypt class that does nothing but supports parse_all().
    class DummyDecrypt:
        """Dummy Decrypt class to simulate decryption."""

        def __init__(self, supplier: Supplier, frame1: bytes, frame2: bytes, key_hex_string: str)-> None:
            self.supplier = supplier
            self.frame1 = frame1
            self.frame2 = frame2
            self.key_hex_string = key_hex_string

        def parse_all(self)-> None:
            """Dummy parse_all method that does nothing."""
            pass

    # Patch Decrypt in the smartmeter module:
    monkeypatch.setattr("src.smartmeter_austria_energy.smartmeter.Decrypt", DummyDecrypt)
    
    # Create a dummy OBIS data class that simply wraps some dummy data.
    class DummyObisData:
        pass

    monkeypatch.setattr("src.smartmeter_austria_energy.smartmeter.ObisData", lambda dec, vals: DummyObisData()) # type: ignore
    
    # Ensure read begins with _is_running False.
    smartmeter_instance._is_running = False # type: ignore
    
    result = smartmeter_instance.read()
    
    # Check that the returned result is our dummy OBISData instance.
    assert isinstance(result, DummyObisData)


def test_read_weird_result(monkeypatch: MonkeyPatch, smartmeter_instance: Smartmeter)-> None:
    """
    Test the branch where after reading, the split result does not lead to valid telegrams.
    In this test, we simulate re.split returning an empty list,
    which forces the 'weird result' branch.
    Even in that case, the decryption and OBISData creation take place.
    """

    supplier = smartmeter_instance._supplier # type: ignore
    stream = (supplier.frame1_start_bytes +
              b"payload1" +
              supplier.frame2_start_bytes +
              b"payload2" +
              supplier.frame2_end_bytes)
    dummy_serial = DummySerialForRead(stream)

    def dummy_open_serial():
        smartmeter_instance._my_serial = dummy_serial # type: ignore
    monkeypatch.setattr(smartmeter_instance, "_Smartmeter__open_serial", dummy_open_serial)
    monkeypatch.setattr(time, "sleep", lambda x: None) # type: ignore

    # Override re.split so that it returns an empty list (simulating wrong telegram parsing).
    monkeypatch.setattr(re, "split", lambda regex, s: []) # type: ignore

    monkeypatch.setattr("src.smartmeter_austria_energy.smartmeter.Decrypt", DummyDecrypt)

    # Override OBISData to return a dummy instance.
    class DummyObisData:
        pass
    monkeypatch.setattr("src.smartmeter_austria_energy.smartmeter.ObisData", lambda dec, vals: DummyObisData()) # type: ignore

    smartmeter_instance._is_running = False # type: ignore
    result = smartmeter_instance.read()
    assert isinstance(result, DummyObisData)

