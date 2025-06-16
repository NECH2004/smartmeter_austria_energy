"""Tests the Smartmeter class."""

from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch
import pytest
import serial

from src.smartmeter_austria_energy.exceptions import (
    SmartmeterException,
    SmartmeterSerialException,
    SmartmeterTimeoutException,
)
from src.smartmeter_austria_energy.smartmeter import Smartmeter
from src.smartmeter_austria_energy.supplier import Supplier, SupplierEVN


# Dummy serial module for when testing creation of serial.Serial.
class DummySerial:
    """A dummy serial class to simulate a serial port."""

    def __init__(self, *args, **kwargs) -> None: # type: ignore
        self.is_open = False
        # Set is_open to True to simulate a successful opening.
        self.is_open = True

    def close(self)-> None:
        """Simulate closing the serial port."""
        pass

class DummySerialClosed:
    """A dummy serial class to simulate a serial port."""

    def __init__(self, is_open: bool, raise_on_close: bool = False)-> None:
        """Initialize the dummy serial port."""

        self.is_open = is_open
        self.called = False  # Flag to indicate if close() was called.
        self.raise_on_close = raise_on_close

    def close(self)-> None:
        """Simulate closing the serial port."""
        
        self.called = True
        if self.raise_on_close:
            raise Exception("Dummy failure on close")


class DummySerial3(serial.Serial):
    """A dummy serial class to simulate a serial port."""

    def __init__(self, is_open: bool)-> None:
        """Initialize the dummy serial port."""

        self.is_open = is_open


class DummySupplier(Supplier):
    """A dummy supplier class to simulate a supplier."""

    def __init__(self)-> None:
        """Initialize the dummy supplier."""

        # Initialize any required properties. If Supplier has an __init__,
        # you might need to call super().__init__() and/or customize parameters.
        # For our tests, we define the minimal attributes needed.
        self.frame1_start_bytes = b"68fafa68"
        self.frame2_start_bytes = b"68727268"
        self.frame2_end_bytes = b"\x16"
        self.frame1_start_bytes_hex = "68fafa68"
        self.frame2_start_bytes_hex = "68727268"
        self.supplied_values = []  # Not used in close-serial tests


@pytest.fixture
def smartmeter_instance() -> Smartmeter:
    supplier = DummySupplier()
    """Fixture that creates a Smartmeter instance with dummy values."""

    # Provide dummy values for key and port. Other parameters are default.
    sm = Smartmeter(
        supplier=supplier,
        port="COM1",
        key_hex_string="00112233445566778899aabbccddeeff",
        interval=1
    )
    # Replace the logger with a dummy (or MagicMock) to silence output, if desired.
    sm._logger = MagicMock() # type: ignore
    return sm


@pytest.fixture
def smartmeter_instance2() -> Smartmeter:
    """
    Fixture that creates a Smartmeter instance with dummy values and
    assigns a MagicMock logger. Also sets _my_serial to a dummy serial
    object that is already open.
    """
    instance = Smartmeter(
        supplier=SupplierEVN(),
        port="COM1",
        key_hex_string="deadbeef",
        interval=1,
        baudrate=9600,
        parity="N",
        stopbits=1,
        bytesize=8,
        serial_read_chunk_size=100,
    )
    # Replace the internal logger with a MagicMock to capture logging calls.
    instance._logger = MagicMock() # type: ignore
    # Pre-assign _my_serial to simulate an already opened serial port.
    instance._my_serial = DummySerial(is_open=True) # type: ignore
    return instance


# Fixture to create an instance of your class with required attributes.
@pytest.fixture
def serial_instance() -> Smartmeter:
    """Fixture that creates a Smartmeter instance with dummy values"""

    # Create a Smartmeter instance.
    # The __init__ signature is:
    #   __init__(supplier, port, key_hex_string, interval=1, baudrate=2400,
    #            parity, stopbits, bytesize, serial_read_chunk_size)
    #
    # For testing __open_serial only, the supplier instance isn’t used,
    # so we can pass a dummy value (e.g. None).
    instance = Smartmeter(
        supplier=SupplierEVN(),
        port="COM1",
        key_hex_string="deadbeef",
        interval=1,
        baudrate=9600,
        parity="N",
        stopbits=1,
        bytesize=8,
        serial_read_chunk_size=100,
    )
    # Replace the logger with a MagicMock to capture logs.
    instance._logger = MagicMock() # type: ignore
    # Initialize _my_serial to None.
    instance._my_serial = None # type: ignore
    return instance


def test_smartmeter_constructor() -> None:
    """Test the constructor of the smartmeter class."""
    supplier = SupplierEVN()
    key_hex_string = "some_hex"
    port = "COM5"

    my_smartmeter = Smartmeter(supplier, port, key_hex_string)

    assert isinstance(my_smartmeter, Smartmeter)


def test_smartmeter_has_empty_port() -> None:
    """Test the constructor of the smartmeter class with an empty port."""
    supplier = SupplierEVN()
    key_hex_string = "some_hex"
    port = ""

    my_smartmeter = Smartmeter(supplier, port, key_hex_string)
    with pytest.raises(SmartmeterException):
        my_smartmeter.read()


def test_smartmeter_supplier() -> None:
    """Test the supplier property of the smartmeter class."""
    supplier = SupplierEVN()
    key_hex_string = "some_hex"
    port = "COM5"

    my_smartmeter = Smartmeter(supplier, port, key_hex_string)

    assert supplier == my_smartmeter.supplier


def test_close_serial_none(smartmeter_instance: Smartmeter) -> None:
    """
    Test __close_serial does nothing if _my_serial is not set.
    """
    if hasattr(smartmeter_instance, "_my_serial"):
        del smartmeter_instance._my_serial # type: ignore
    # Invoke the private method via name mangling.
    smartmeter_instance._Smartmeter__close_serial() # type: ignore
    # No exception should occur.


def test_close_serial_already_closed(smartmeter_instance: Smartmeter) -> None:
    """
    Test __close_serial does nothing if _my_serial exists but the port is not open.
    """
    dummy = DummySerialClosed(is_open=False)
    smartmeter_instance._my_serial = dummy # type: ignore
    # Invoke the private method via name mangling.
    smartmeter_instance._Smartmeter__close_serial() # type: ignore
    # The dummy's close should not have been called.
    assert dummy.called is False


def test_close_serial_when_open(smartmeter_instance: Smartmeter) -> None:
    """
    Test __close_serial calls close() when _my_serial is open.
    """
    dummy = DummySerialClosed(is_open=True)
    smartmeter_instance._my_serial = dummy # type: ignore
    # Invoke the private method via name mangling.
    smartmeter_instance._Smartmeter__close_serial() # type: ignore
    assert dummy.called is True


def test_close_serial_exception(smartmeter_instance: Smartmeter) -> None:
    """
    Test that if _my_serial.close() raises an exception, __close_serial wraps it in SmartmeterException.
    """
    dummy = DummySerialClosed(is_open=True, raise_on_close=True)
    smartmeter_instance._my_serial = dummy # type: ignore
    with pytest.raises(SmartmeterException) as excinfo:
    # Invoke the private method via name mangling.
        smartmeter_instance._Smartmeter__close_serial() # type: ignore
    assert f"Closing port '{smartmeter_instance._port}' failed" in str(excinfo.value) # type: ignore


def test_already_open(smartmeter_instance2: Smartmeter) -> None:
    """
    Test that if the _my_serial attribute is already set and open,
    __open_serial logs the message and exits early.
    """
    # Access the private __open_serial method through name mangling.
    smartmeter_instance2._Smartmeter__open_serial() # type: ignore
    
    # Verify that the logger was called with a debug message indicating the port is already open.
    smartmeter_instance2._logger.debug.assert_called_with("Serial port 'COM1' is already open.") # type: ignore


def test_open_serial_success(monkeypatch: MonkeyPatch, smartmeter_instance: Smartmeter) -> None:
    """
    Test that __open_serial successfully opens the serial port
    and assigns _my_serial when no exception occurs.
    """
    # Create a dummy serial object that simulates a successful open.
    dummy_serial = DummySerial()

    # Monkey-patch serial.Serial to return our dummy
    def dummy_serial_constructor(*args, **kwargs): # type: ignore
        return dummy_serial

    monkeypatch.setattr(serial, "Serial", dummy_serial_constructor) # type: ignore
    
    # Ensure _my_serial is not set
    if hasattr(smartmeter_instance, "_my_serial"):
        del smartmeter_instance._my_serial # type: ignore

    # Call __open_serial (via name mangling)
    smartmeter_instance._Smartmeter__open_serial() # type: ignore

    # Verify that _my_serial was set to our dummy object.
    assert smartmeter_instance._my_serial is dummy_serial # type: ignore
    # Verify that an info log message was issued by __open_serial.
    smartmeter_instance._logger.debug.assert_called_with( # type: ignore
        f"Serial port '{smartmeter_instance._port}' opened successfully." # type: ignore
    )


def test_open_serial_already_open(monkeypatch: MonkeyPatch, smartmeter_instance: Smartmeter) -> None:
    """
    Test that if _my_serial already exists and is open,
    __open_serial does nothing.
    """
    # Set _my_serial to a dummy serial that is open.
    dummy_serial = DummySerial()
    smartmeter_instance._my_serial = dummy_serial # type: ignore

    # Monkey-patch serial.Serial with a function that would raise if called.
    def should_not_be_called(*args, **kwargs): # type: ignore
        pytest.fail("serial.Serial constructor should not be called when port is already open.")
    monkeypatch.setattr(serial, "Serial", should_not_be_called) # type: ignore

    # Call __open_serial again.
    smartmeter_instance._Smartmeter__open_serial() # type: ignore
    # Check that _my_serial is unchanged.
    assert smartmeter_instance._my_serial is dummy_serial # type: ignore
    # Verify that a debug message was issued.
    smartmeter_instance._logger.debug.assert_called_with( # type: ignore
        f"Serial port '{smartmeter_instance._port}' is already open." # type: ignore
    )


def test_open_serial_timeout_exception(monkeypatch: MonkeyPatch, smartmeter_instance: Smartmeter) -> None:
    """
    Test that a SerialTimeoutException raised by serial.Serial is wrapped
    as a SmartmeterTimeoutException.
    """
    def dummy_constructor_timeout(*args, **kwargs): # type: ignore
        raise serial.SerialTimeoutException("Timeout occurred.")

    monkeypatch.setattr(serial, "Serial", dummy_constructor_timeout) # type: ignore

    with pytest.raises(SmartmeterTimeoutException) as excinfo: # type: ignore
        smartmeter_instance._Smartmeter__open_serial() # type: ignore
    # Check that the exception message contains the port name.
    assert f"Timeout occurred when opening port '{smartmeter_instance._port}'" in str(excinfo.value) # type: ignore
    smartmeter_instance._logger.error.assert_called() # type: ignore


def test_open_serial_serial_exception(monkeypatch: MonkeyPatch, smartmeter_instance: Smartmeter) -> None:
    """
    Test that a SerialException raised by serial.Serial is wrapped
    as a SmartmeterSerialException.
    """
    def dummy_constructor_serial(*args, **kwargs): # type: ignore
        raise serial.SerialException("Serial error.")

    monkeypatch.setattr(serial, "Serial", dummy_constructor_serial) # type: ignore

    with pytest.raises(SmartmeterSerialException) as excinfo:
        smartmeter_instance._Smartmeter__open_serial() # type: ignore
    assert f"Unable to open port '{smartmeter_instance._port}'" in str(excinfo.value) # type: ignore
    smartmeter_instance._logger.error.assert_called() # type: ignore


def test_open_serial_generic_exception(monkeypatch: MonkeyPatch, smartmeter_instance: Smartmeter) -> None:
    """
    Test that a generic Exception raised by serial.Serial is wrapped
    as a SmartmeterException.
    """
    def dummy_constructor_generic(*args, **kwargs): # type: ignore
        raise Exception("Generic error.")

    monkeypatch.setattr(serial, "Serial", dummy_constructor_generic) # type: ignore

    with pytest.raises(SmartmeterException) as excinfo:
        smartmeter_instance._Smartmeter__open_serial() # type: ignore
    assert f"Connection to '{smartmeter_instance._port}' failed" in str(excinfo.value) # type: ignore
    smartmeter_instance._logger.exception.assert_called() # type: ignore
