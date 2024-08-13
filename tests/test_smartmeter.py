"""Tests the Smartmeter class."""

import pytest
from src.smartmeter_austria_energy.exceptions import SmartmeterException
from src.smartmeter_austria_energy.smartmeter import Smartmeter
from src.smartmeter_austria_energy.supplier import SupplierEVN


def test_smartmeter_constructor():
    """Test the constructor of the smartmeter class."""
    supplier = SupplierEVN
    key_hex_string = "some_hex"
    port = "COM5"

    my_smartmeter = Smartmeter(supplier, port, key_hex_string)

    assert isinstance(my_smartmeter, Smartmeter)


def test_smartmeter_has_empty_port():
    """Test the constructor of the smartmeter class with an empty port."""
    supplier = SupplierEVN
    key_hex_string = "some_hex"
    port = ""

    my_smartmeter = Smartmeter(supplier, port, key_hex_string)
    with pytest.raises(SmartmeterException):
        my_smartmeter.read()


def test_smartmeter_supplier():
    """Test the supplier property of the smartmeter class."""
    supplier = SupplierEVN
    key_hex_string = "some_hex"
    port = "COM5"

    my_smartmeter = Smartmeter(supplier, port, key_hex_string)

    assert supplier == my_smartmeter.supplier
