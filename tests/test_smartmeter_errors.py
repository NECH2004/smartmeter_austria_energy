import time
from unittest.mock import Mock

from _pytest.monkeypatch import MonkeyPatch
import pytest
import serial

from src.smartmeter_austria_energy.exceptions import SmartmeterException
from src.smartmeter_austria_energy.smartmeter import Smartmeter
from src.smartmeter_austria_energy.supplier import Supplier


# --- Supplier fixture (if not already defined) ---
@pytest.fixture
def supplier_mock()-> Supplier:
    """Create a mock Supplier instance with necessary attributes for testing."""

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

# --- Smartmeter fixture renamed to smartmeter_instance_running_false ---
@pytest.fixture
def smartmeter_instance_running_false(supplier_mock: Mock)-> Smartmeter:
    key_hex_string = "00112233445566778899aabbccddeeff"
    sm = Smartmeter(supplier=supplier_mock, port="COM_FAKE", key_hex_string=key_hex_string)
    sm._is_running = False # type: ignore
    return sm

# --- Dummy serial always returning the same incomplete chunk ---
class DummySerialConsistent:
    def __init__(self, data: bytes)-> None:
        self.data = data
    def isOpen(self):
        return True
    @property
    def is_open(self):
        return True
    def inWaiting(self):
        return len(self.data)  # Always report nonzero number of bytes.
    def read(self, n: int):
        return self.data      # Always return the same chunk.
    def close(self):
        pass


# --- Dummy serial that returns a sequence of chunks ---
class DummySerialSequence:
    def __init__(self, chunks: list[bytes])-> None:
        self.chunks = chunks
        self.index = 0
    def isOpen(self):
        return True
    @property
    def is_open(self):
        return True
    def inWaiting(self):
        # Always return the length of the next chunk if available.
        if self.index < len(self.chunks):
            return len(self.chunks[self.index])
        return 0
    def read(self, n: int):
        if self.index < len(self.chunks):
            chunk = self.chunks[self.index]
            self.index += 1
            return chunk
        return b""
    def close(self):
        pass


# --- Dummy serial that simulates no incoming data ---
class DummySerialNoData:
    def isOpen(self):
        return True
    @property
    def is_open(self):
        return True
    def inWaiting(self):
        return 0  # Always report no data available.
    def read(self, n: int):
        # Always return an empty byte string since no data is available.
        return b""
    def close(self):
        pass


def test_read_frame2_before_frame1_always_incomplete(monkeypatch: MonkeyPatch, smartmeter_instance_running_false: Smartmeter, supplier_mock: Supplier)->None:
    """
    This test exercises the branch in Smartmeter.read() where the frame2 marker is found
    before the frame1 marker. In that situation the code resets the stream to start at frame1 and continues.
    
    We simulate this by using a dummy serial that always returns the same incomplete chunk.
    The chunk is constructed so that the supplier's frame2 marker appears first, then some dummy data,
    then the supplier's frame1 marker appears later; also, the chunk does not end with the expected
    termination byte (supplier.frame2_end_bytes). This forces the while‐loop to repeatedly trim the stream.
    
    We simulate time progression via monkeypatching time.monotonic so that after several iterations
    the simulated time exceeds the allowed timeout (start time + 5 seconds) and a SmartmeterTimeoutException
    is raised.
    """
    # Construct a chunk where frame2 appears before frame1.
    # For example, if:
    #   supplier.frame2_start_bytes == b"68727268" and supplier.frame1_start_bytes == b"68fafa68"
    # then the following chunk ensures frame2 is found before frame1.
    chunk = supplier_mock.frame2_start_bytes + b"dummy" + supplier_mock.frame1_start_bytes + b"XYZ"
    # This chunk does not end with supplier.frame2_end_bytes (b"\x16"), so it is always incomplete.
    
    dummy_serial = DummySerialConsistent(chunk)
    monkeypatch.setattr(serial, "Serial", lambda *args, **kwargs: dummy_serial) # type: ignore
    # Override sleep so that the test does not really delay.
    monkeypatch.setattr(time, "sleep", lambda s: None) # type: ignore
    
    # Simulate monotonic time progression.
    # read() sets max_stop_time = start_time + 5*interval (with default interval = 1, so max_stop_time = start + 5).
    # We prepare a sequence of times that eventually exceeds that.
    start_time = 1000.0
    # Produce a list of increasing times; for example, 1000.0, 1000.5, 1001.0, 1001.5, …, and finally >1005.
    times = [start_time + 0.5 * i for i in range(11)]  # This yields: 1000.0, 1000.5, 1001.0, ... up to 1005.0
    # To force the timeout, we ensure the last value exceeds 1005 (say 1005.5).
    times[-1] = 1005.5
    time_iter = iter(times)
    monkeypatch.setattr(time, "monotonic", lambda: next(time_iter))
    
    with pytest.raises(SmartmeterException):
        smartmeter_instance_running_false.read()


def test_read_bypass_while(monkeypatch: MonkeyPatch, smartmeter_instance_running_false: Smartmeter, supplier_mock: Supplier)->None:
    """
    Simulate that after opening the serial port, its is_open property is False.
    In that case, read() sets _is_running = False (because isOpen() returns False) and
    bypasses the while loop. Then, it proceeds to decryption.
    
    To avoid decryption errors (since no real telegrams are read), we monkey-patch:
      - __open_serial() so it does nothing.
      - Decrypt so that its parse_all() is a no-op.
      - ObisData so that it returns a dummy object.
    
    Then read() should immediately return the dummy ObisData.
    """
    # Override __open_serial to do nothing.
    monkeypatch.setattr(smartmeter_instance_running_false, "_Smartmeter__open_serial", lambda: None)
    
    # Create a dummy serial object that is "closed": is_open returns False.
    class DummyClosedSerial:
        @property
        def is_open(self):
            return False
        def isOpen(self):
            return False
        def inWaiting(self):
            return 0
        def read(self, n: int):
            return b""
        def close(self):
            pass

    smartmeter_instance_running_false._my_serial = DummyClosedSerial() # type: ignore

    # Monkey-patch Decrypt so that its parse_all() does nothing.
    class DummyDecrypt2:
        def parse_all(self):
            pass
    # IMPORTANT: adjust the module path if needed.
    monkeypatch.setattr("src.smartmeter_austria_energy.smartmeter.Decrypt", lambda supplier, f1, f2, key: DummyDecrypt2()) # type: ignore
    
    # Monkey-patch ObisData so that it returns a dummy object.
    class DummyObisData2:
        pass
    monkeypatch.setattr("src.smartmeter_austria_energy.smartmeter.ObisData", lambda dec, vals: DummyObisData2()) # type: ignore
    
    # Call read(). Because _my_serial.is_open is False, the while loop is not entered.
    result = smartmeter_instance_running_false.read()
    
    # Verify that the returned object is our dummy ObisData.
    assert isinstance(result, DummyObisData2), "Expected read() to return DummyObisData when while-loop is bypassed."



    """
    Simulate the branch in read() where frame2 is found before frame1 so that the stream is trimmed,
    and then (after a second read) the overall stream becomes complete.
    
    We supply two chunks:
      - chunk1: Contains the frame2 marker at the beginning followed by some junk and then the
                frame1 marker and additional data (making the telegram incomplete).
      - chunk2: Contains extra bytes so that when appended the final stream meets completeness:
                • It begins with supplier.frame1_start_bytes,
                • Contains supplier.frame2_start_bytes later, and
                • Ends with supplier.frame2_end_bytes.
    
    We also simulate monotonic time with an iterator so that the loop does not time out.
    Finally, we bypass decryption by monkey‑patching the Decrypt class and ObisData.
    """
    # Build chunk1 so that frame2 is found before frame1.
    chunk1 = supplier_mock.frame2_start_bytes + b"junk" + supplier_mock.frame1_start_bytes + b"incomplete"
    # When trimmed, the stream becomes: supplier.frame1_start_bytes + b"incomplete"
    #
    # Build chunk2 so that after appending the stream is complete.
    # For example, append a chunk that starts with some filler,
    # then contains supplier.frame2_start_bytes, some more filler, and ends with the expected termination.
    chunk2 = b"----" + supplier_mock.frame2_start_bytes + b"rest" + supplier_mock.frame2_end_bytes

    dummy_serial = DummySerialSequence([chunk1, chunk2])
    monkeypatch.setattr(serial, "Serial", lambda *args, **kwargs: dummy_serial) # type: ignore
    # Override time.sleep to avoid real delay.
    monkeypatch.setattr(time, "sleep", lambda s: None) # type: ignore

    # Simulate monotonic time progression.
    # We set a generator that returns values that never trigger a timeout.
    # For example, return 1000.0 on every call.
    monkeypatch.setattr(time, "monotonic", lambda: 1000.0)

    # Monkey-patch Decrypt so that its parse_all() does nothing.
    class DummyDecrypt:
        def parse_all(self):
            pass
    monkeypatch.setattr("src.smartmeter_austria_energy.smartmeter.Decrypt",
                        lambda supplier, f1, f2, key: DummyDecrypt()) # type: ignore
    
    # Monkey-patch ObisData to return a dummy object.
    class DummyObisData:
        pass
    monkeypatch.setattr("src.smartmeter_austria_energy.smartmeter.ObisData",
                        lambda dec, vals: DummyObisData()) # type: ignore

    # Call read(). With our two chunks, the while-loop should:
    #   1. Read chunk1, detect that frame2 appears before frame1 and trim the stream
    #   2. Then read chunk2, which makes the overall stream complete.
    result = smartmeter_instance_running_false.read()
    assert isinstance(result, DummyObisData), "Expected read() to return DummyObisData after processing chunks."


def test_read_loop_sleep_and_timeout(monkeypatch: MonkeyPatch, smartmeter_instance_running_false: Smartmeter, supplier_mock: Supplier)->None:
    """
    This test covers the following lines in the read() method:

        time.sleep(sleep_interval)
        actual_time = time.monotonic()
        if actual_time < max_stop_time:
            continue
        raise SmartmeterTimeoutException()

    We simulate a serial port that never delivers any data
    (inWaiting() always returns 0). Then, we simulate a monotonic time
    sequence that eventually exceeds the allowed timeout (start_time + 5×interval).
    As a result, the while-loop continues to call time.sleep and eventually raises
    SmartmeterTimeoutException.
    """
    # Replace serial.Serial with a dummy serial that always returns no data.
    monkeypatch.setattr(serial, "Serial", lambda *args, **kwargs: DummySerialNoData()) # type: ignore
    
    # Override time.sleep so the test runs quickly.
    monkeypatch.setattr(time, "sleep", lambda s: None) # type: ignore
    
    # Simulate a monotonically increasing time sequence.
    # In the read() method, after opening the port the following is computed:
    #    start_time = time.monotonic()
    #    max_stop_time = start_time + 5 * self._interval
    # (with self._interval by default equal to 1, i.e. max_stop_time = start_time + 5)
    #
    # We simulate time.monotonic to return these values in sequence:
    #   1000.0, 1001.0, 1002.0, 1003.0, 1004.0, then 1005.1 (exceeding the timeout).
    time_values = [1000.0, 1001.0, 1002.0, 1003.0, 1004.0, 1005.1]
    time_iter = iter(time_values)
    monkeypatch.setattr(time, "monotonic", lambda: next(time_iter))
    
    # Since no data ever arrives, the while loop will run until the simulated time exceeds max_stop_time.
    with pytest.raises(SmartmeterException):
        smartmeter_instance_running_false.read()

