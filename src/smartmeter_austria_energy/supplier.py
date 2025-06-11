"""Classes used to define suppliers."""

    # pylint: disable=too-few-public-methods

class Supplier:
    """Supplier base class."""
    name : str
    frame1_start_bytes_hex : str = '68fafa68'
    frame1_start_bytes : bytes = b'\x68\xfa\xfa\x68'  # 68 FA FA 68
    frame2_start_bytes_hex : str
    frame2_start_bytes : bytes
    frame2_end_bytes : bytes = b'\x16'
    ic_start_byte : int
    enc_data_start_byte : int
    supplied_values : list[str]


class SupplierTINETZ(Supplier):
    """Defines TINETZ."""
    name : str = "TINETZ"
    frame2_start_bytes_hex : str = '68727268'
    frame2_start_bytes : bytes = b'\x68\x72\x72\x68'  # 68 72 72 68
    ic_start_byte : int = 23
    enc_data_start_byte : int = 27
    supplied_values : list[str] = [
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


class SupplierEVN(Supplier):
    """Defines EVN."""
    name : str = "EVN"
    frame2_start_bytes_hex : str = '68141468'
    frame2_start_bytes : bytes = b'\x68\x14\x14\x68'  # 68 14 14 68
    ic_start_byte : int = 22
    enc_data_start_byte : int = 26
    supplied_values : list[str] = [
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


class SupplierSALZBURGNETZ(SupplierTINETZ):
    """Defines SALZBURGNETZ."""
    name : str = "SALZBURGNETZ"


SUPPLIER_EVN_NAME = "EVN"
SUPPLIER_SALZBURGNETZ_NAME = "SALZBURGNETZ"
SUPPLIER_TINETZ_NAME = "TINETZ"

SUPPLIERS: dict[str, Supplier] = {
    SUPPLIER_EVN_NAME : SupplierEVN(),
    SUPPLIER_SALZBURGNETZ_NAME : SupplierSALZBURGNETZ(),
    SUPPLIER_TINETZ_NAME : SupplierTINETZ(),
}
