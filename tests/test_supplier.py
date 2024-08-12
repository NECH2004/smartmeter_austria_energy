"""Supplier classes tests."""

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


def test_Suppliers_EVN():
    """Test the Suppliers dict."""
    # arrange
    # act
    my_supplier = SUPPLIERS[SUPPLIER_EVN_NAME]

    # assert
    assert isinstance(my_supplier, SupplierEVN)


def test_Suppliers_SalzburgNetz():
    """Test the Suppliers dict."""
    # arrange
    # act
    my_supplier = SUPPLIERS[SUPPLIER_SALZBURGNETZ_NAME]

    # assert
    assert isinstance(my_supplier, SupplierSALZBURGNETZ)


def test_Suppliers_TINETZ():
    """Test the Suppliers dict."""
    # arrange
    # act
    my_supplier = SUPPLIERS[SUPPLIER_TINETZ_NAME]

    # assert
    assert isinstance(my_supplier, SupplierTINETZ)


def test_Suppliers_EVN_inheritance():
    """Test the SupplierEVN class for inheritance."""
    # arrange
    # act
    my_supplier = SupplierEVN()

    # assert
    assert isinstance(my_supplier, Supplier)


def test_Suppliers_SalzburgNETZ_inheritance():
    """Test the SupplierSALZBURGNETZ class for inheritance."""
    # arrange
    # act
    my_supplier = SupplierSALZBURGNETZ()

    # assert
    assert isinstance(my_supplier, SupplierTINETZ)
    assert isinstance(my_supplier, Supplier)


def test_Suppliers_TINETZ_inheritance():
    """Test the SupplierTINETZ class for inheritance."""
    # arrange
    # act
    my_supplier = SupplierTINETZ()

    # assert
    assert isinstance(my_supplier, Supplier)


def test_Supplier():
    """Test the Supplier class."""

    # arrange
    # act
    my_supplier = Supplier()

    # assert
    assert my_supplier.name is None
    assert my_supplier.ic_start_byte is None
    assert my_supplier.enc_data_start_byte is None

    assert my_supplier.frame1_start_bytes_hex == _frame1_start_bytes_hex
    assert my_supplier.frame1_start_bytes == _frame1_start_bytes
    assert my_supplier.frame2_end_bytes == _frame2_end_bytes
    assert my_supplier.supplied_values == None


def test_SupplierEVN():
    """Test the SupplierEVN class."""

    # arrange
    # act
    my_supplier = SupplierEVN()

    # assert
    assert my_supplier.name == "EVN"
    assert my_supplier.ic_start_byte == 22
    assert my_supplier.enc_data_start_byte == 26

    assert my_supplier.frame1_start_bytes_hex == _frame1_start_bytes_hex
    assert my_supplier.frame1_start_bytes == _frame1_start_bytes
    assert my_supplier.frame2_end_bytes == _frame2_end_bytes
    assert my_supplier.supplied_values == _supplied_values_evn

    assert my_supplier.frame2_start_bytes_hex == '68141468'
    assert my_supplier.frame2_start_bytes == b'\x68\x14\x14\x68'


def test_SupplierTINETZ():
    """Test the SupplierTINETZ class."""

    # arrange
    # act
    my_supplier = SupplierTINETZ()

    # assert
    assert my_supplier.name == "TINETZ"
    assert my_supplier.ic_start_byte == 23
    assert my_supplier.enc_data_start_byte == 27

    assert my_supplier.frame1_start_bytes_hex == _frame1_start_bytes_hex
    assert my_supplier.frame1_start_bytes == _frame1_start_bytes
    assert my_supplier.frame2_end_bytes == _frame2_end_bytes
    assert my_supplier.supplied_values == _supplied_values_ti

    assert my_supplier.frame2_start_bytes_hex == '68727268'
    assert my_supplier.frame2_start_bytes == b'\x68\x72\x72\x68'


def test_SupplierSALZBURGNETZ():
    """Test the SupplierSALZBURGNETZ class."""

    # arrange
    # act
    my_supplier = SupplierSALZBURGNETZ()

    # assert
    assert my_supplier.name == "SALZBURGNETZ"
    assert my_supplier.ic_start_byte == 23
    assert my_supplier.enc_data_start_byte == 27

    assert my_supplier.frame1_start_bytes_hex == _frame1_start_bytes_hex
    assert my_supplier.frame1_start_bytes == _frame1_start_bytes
    assert my_supplier.frame2_end_bytes == _frame2_end_bytes
    assert my_supplier.supplied_values == _supplied_values_ti

    assert my_supplier.frame2_start_bytes_hex == '68727268'
    assert my_supplier.frame2_start_bytes == b'\x68\x72\x72\x68'
