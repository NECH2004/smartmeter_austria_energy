"""Tests the exception classes."""

# pylint: disable=invalid-name

from src.smartmeter_austria_energy.exceptions import (
    SmartmeterException,
    SmartmeterSerialException,
    SmartmeterTimeoutException,
)


def test_SmartmeterException_is_exception()-> None:
    """Test the SmartmeterException class."""
    my_exception = SmartmeterException()

    assert isinstance(my_exception, Exception)


def test_SmartmeterTimeoutException_is_exception()-> None:
    """Test the SmartmeterTimeoutException class."""
    my_exception = SmartmeterTimeoutException()

    assert isinstance(my_exception, SmartmeterException)


def test_SmartmeterSerialException_is_exception()-> None:
    """Test the SmartmeterSerialException class."""
    my_exception = SmartmeterSerialException()

    assert isinstance(my_exception, SmartmeterException)
    assert isinstance(my_exception, Exception)
