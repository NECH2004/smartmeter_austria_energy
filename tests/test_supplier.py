"""Supplier classes tests."""

# pylint: disable=invalid-name

from src.smartmeter_austria_energy.supplier import (
    SUPPLIER_EVN_NAME,
    SUPPLIER_SALZBURGNETZ_NAME,
    SUPPLIER_TINETZ_NAME,
    SUPPLIERS,
    Supplier,
    SupplierEVN,
    SupplierSALZBURGNETZ,
    SupplierTINETZ,
)

_frame1_start_bytes_hex : str = '68fafa68'
_frame1_start_bytes : bytes = b'\x68\xfa\xfa\x68'  # 68 FA FA 68
_frame2_end_bytes : bytes = b'\x16'
_supplied_values_ti : list[str] = [
    "VoltageL1",
    "VoltageL2",
    "VoltageL3",
    "CurrentL1",
    "CurrentL2",
    "CurrentL3",
    "RealPowerIn",
    "RealPowerOut",
    "RealEnergyIn",
    "RealEnergyOut",
    "ReactiveEnergyIn",
    "ReactiveEnergyOut",
    "Factor",
    "DeviceNumber",
    "LogicalDeviceNumber"]

_supplied_values_evn : list[str] = [
    "VoltageL1",
    "VoltageL2",
    "VoltageL3",
    "CurrentL1",
    "CurrentL2",
    "CurrentL3",
    "RealPowerIn",
    "RealPowerOut",
    "RealEnergyIn",
    "RealEnergyOut",
    "Factor",
    "DeviceNumber",
    "LogicalDeviceNumber"]


def test_Suppliers_EVN()-> None:
    """Test the Suppliers dict."""
    my_supplier = SUPPLIERS[SUPPLIER_EVN_NAME]

    assert isinstance(my_supplier, SupplierEVN)


def test_Suppliers_SalzburgNetz()-> None:
    """Test the Suppliers dict."""
    my_supplier = SUPPLIERS[SUPPLIER_SALZBURGNETZ_NAME]

    assert isinstance(my_supplier, SupplierSALZBURGNETZ)


def test_Suppliers_TINETZ()-> None:
    """Test the Suppliers dict."""
    my_supplier = SUPPLIERS[SUPPLIER_TINETZ_NAME]

    assert isinstance(my_supplier, SupplierTINETZ)


def test_Suppliers_EVN_inheritance()-> None:
    """Test the SupplierEVN class for inheritance."""
    my_supplier = SupplierEVN()

    assert isinstance(my_supplier, Supplier)


def test_Suppliers_SalzburgNETZ_inheritance()-> None:
    """Test the SupplierSALZBURGNETZ class for inheritance."""
    my_supplier = SupplierSALZBURGNETZ()

    assert isinstance(my_supplier, SupplierTINETZ)
    assert isinstance(my_supplier, Supplier)


def test_Suppliers_TINETZ_inheritance()-> None:
    """Test the SupplierTINETZ class for inheritance."""
    my_supplier = SupplierTINETZ()

    assert isinstance(my_supplier, Supplier)


def test_Supplier()-> None:
    """Test the Supplier class."""
    my_supplier = Supplier()

    assert my_supplier.frame1_start_bytes_hex == _frame1_start_bytes_hex
    assert my_supplier.frame1_start_bytes == _frame1_start_bytes
    assert my_supplier.frame2_end_bytes == _frame2_end_bytes


def test_SupplierEVN()-> None:
    """Test the SupplierEVN class."""
    my_supplier = SupplierEVN()

    assert my_supplier.name == "EVN"
    assert my_supplier.ic_start_byte == 22
    assert my_supplier.enc_data_start_byte == 26

    assert my_supplier.frame1_start_bytes_hex == _frame1_start_bytes_hex
    assert my_supplier.frame1_start_bytes == _frame1_start_bytes
    assert my_supplier.frame2_end_bytes == _frame2_end_bytes
    assert my_supplier.supplied_values == _supplied_values_evn

    assert my_supplier.frame2_start_bytes_hex == '68141468'
    assert my_supplier.frame2_start_bytes == b'\x68\x14\x14\x68'


def test_SupplierTINETZ()-> None:
    """Test the SupplierTINETZ class."""
    my_supplier = SupplierTINETZ()

    assert my_supplier.name == "TINETZ"
    assert my_supplier.ic_start_byte == 23
    assert my_supplier.enc_data_start_byte == 27

    assert my_supplier.frame1_start_bytes_hex == _frame1_start_bytes_hex
    assert my_supplier.frame1_start_bytes == _frame1_start_bytes
    assert my_supplier.frame2_end_bytes == _frame2_end_bytes
    assert my_supplier.supplied_values == _supplied_values_ti

    assert my_supplier.frame2_start_bytes_hex == '68727268'
    assert my_supplier.frame2_start_bytes == b'\x68\x72\x72\x68'


def test_SupplierSALZBURGNETZ()-> None:
    """Test the SupplierSALZBURGNETZ class."""
    my_supplier = SupplierSALZBURGNETZ()

    assert my_supplier.name == "SALZBURGNETZ"
    assert my_supplier.ic_start_byte == 23
    assert my_supplier.enc_data_start_byte == 27

    assert my_supplier.frame1_start_bytes_hex == _frame1_start_bytes_hex
    assert my_supplier.frame1_start_bytes == _frame1_start_bytes
    assert my_supplier.frame2_end_bytes == _frame2_end_bytes
    assert my_supplier.supplied_values == _supplied_values_ti

    assert my_supplier.frame2_start_bytes_hex == '68727268'
    assert my_supplier.frame2_start_bytes == b'\x68\x72\x72\x68'
