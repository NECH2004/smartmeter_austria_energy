"""OBIS data classes tests."""

# pylint: disable=invalid-name
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements

from src.smartmeter_austria_energy.constants import PhysicalUnits
from src.smartmeter_austria_energy.decrypt import Decrypt
from src.smartmeter_austria_energy.obisdata import ObisData
from src.smartmeter_austria_energy.obisvalue import ObisValueFloat, ObisValueBytes
from src.smartmeter_austria_energy.supplier import SupplierTINETZ


def test_ObisData_constructor():
    """Test the obisdata constructor."""

    obisdata = ObisData(dec=None, wanted_values=[])
    assert isinstance(obisdata, ObisData)


def test_ObisData_properties():
    """Test the obisdata constructor."""

    obisdata = ObisData(dec=None, wanted_values=[])

    current1 = obisdata.CurrentL1
    current2 = obisdata.CurrentL2
    current3 = obisdata.CurrentL3

    voltage1 = obisdata.VoltageL1
    voltage2 = obisdata.VoltageL2
    voltage3 = obisdata.VoltageL3

    realPowerIn = obisdata.RealPowerIn
    realPowerOut = obisdata.RealPowerOut
    realPowerDelta = obisdata.RealPowerDelta

    realEnergyIn = obisdata.RealEnergyIn
    realEnergyOut = obisdata.RealEnergyOut

    reactiveEnergyIn = obisdata.ReactiveEnergyIn
    reactiveEnergyOut = obisdata.ReactiveEnergyOut

    deviceNumber = obisdata.DeviceNumber
    logicalDeviceNumber = obisdata.LogicalDeviceNumber

    assert isinstance(current1, ObisValueFloat)
    assert current1.raw_value == 0
    assert current1.unit == PhysicalUnits.A

    assert isinstance(current2, ObisValueFloat)
    assert current2.raw_value == 0
    assert current2.unit == PhysicalUnits.A

    assert isinstance(current3, ObisValueFloat)
    assert current3.raw_value == 0
    assert current3.unit == PhysicalUnits.A

    assert isinstance(voltage1, ObisValueFloat)
    assert voltage1.raw_value == 0
    assert voltage1.unit == PhysicalUnits.V

    assert isinstance(voltage2, ObisValueFloat)
    assert voltage2.raw_value == 0
    assert voltage2.unit == PhysicalUnits.V

    assert isinstance(voltage3, ObisValueFloat)
    assert voltage3.raw_value == 0
    assert voltage3.unit == PhysicalUnits.V

    assert isinstance(realPowerIn, ObisValueFloat)
    assert realPowerIn.raw_value == 0
    assert realPowerIn.unit == PhysicalUnits.W

    assert isinstance(realPowerOut, ObisValueFloat)
    assert realPowerOut.raw_value == 0
    assert realPowerOut.unit == PhysicalUnits.W

    assert isinstance(realPowerDelta, ObisValueFloat)
    assert realPowerDelta.raw_value == 0
    assert realPowerDelta.unit == PhysicalUnits.W

    assert isinstance(realPowerIn, ObisValueFloat)
    assert realPowerIn.raw_value == 0
    assert realPowerIn.unit == PhysicalUnits.W

    assert isinstance(realPowerOut, ObisValueFloat)
    assert realPowerOut.raw_value == 0
    assert realPowerOut.unit == PhysicalUnits.W

    assert isinstance(realEnergyIn, ObisValueFloat)
    assert realEnergyIn.raw_value == 0
    assert realEnergyIn.unit == PhysicalUnits.Wh

    assert isinstance(realEnergyOut, ObisValueFloat)
    assert realEnergyOut.raw_value == 0
    assert realEnergyOut.unit == PhysicalUnits.Wh

    assert isinstance(reactiveEnergyIn, ObisValueFloat)
    assert reactiveEnergyIn.raw_value == 0
    assert reactiveEnergyIn.unit == PhysicalUnits.varh

    assert isinstance(reactiveEnergyOut, ObisValueFloat)
    assert reactiveEnergyOut.raw_value == 0
    assert reactiveEnergyOut.unit == PhysicalUnits.varh

    assert isinstance(deviceNumber, ObisValueBytes)
    assert deviceNumber.raw_value == ""

    assert isinstance(logicalDeviceNumber, ObisValueBytes)
    assert logicalDeviceNumber.raw_value == ""


def test_ObisData_property_setter():
    """Test the obisdata constructor."""

    obisdata = ObisData(dec=None, wanted_values=[])

    obisdata.CurrentL1 = ObisValueFloat(1.1, PhysicalUnits.A, 1)
    obisdata.CurrentL2 = ObisValueFloat(0.77, PhysicalUnits.Undef, -2)
    obisdata.CurrentL3 = ObisValueFloat(0.4, PhysicalUnits.A, 0)

    obisdata.VoltageL1 = ObisValueFloat(1.1, PhysicalUnits.V, 0)
    obisdata.VoltageL2 = ObisValueFloat(10, PhysicalUnits.V, 1)
    obisdata.VoltageL3 = ObisValueFloat(0.4, PhysicalUnits.V, 2)

    current1 = obisdata.CurrentL1
    current2 = obisdata.CurrentL2
    current3 = obisdata.CurrentL3

    voltage1 = obisdata.VoltageL1
    voltage2 = obisdata.VoltageL2
    voltage3 = obisdata.VoltageL3

    realPowerIn = obisdata.RealPowerIn
    realPowerOut = obisdata.RealPowerOut
    realPowerDelta = obisdata.RealPowerDelta

    realEnergyIn = obisdata.RealEnergyIn
    realEnergyOut = obisdata.RealEnergyOut

    reactiveEnergyIn = obisdata.ReactiveEnergyIn
    reactiveEnergyOut = obisdata.ReactiveEnergyOut

    deviceNumber = obisdata.DeviceNumber
    logicalDeviceNumber = obisdata.LogicalDeviceNumber

    assert isinstance(current1, ObisValueFloat)
    assert current1.raw_value == 1.1
    assert current1.value == 11
    assert current1.value_string == "11.0 A"
    assert current1.unit == PhysicalUnits.A

    assert isinstance(current2, ObisValueFloat)
    assert current2.raw_value == 0.77
    assert current2.value == 0.0077
    assert current2.value_string == "0.0077 Undef"
    assert current2.unit == PhysicalUnits.Undef

    assert isinstance(current3, ObisValueFloat)
    assert current3.raw_value == 0.4
    assert current3.value == 0.4
    assert current3.value_string == "0.4 A"
    assert current3.unit == PhysicalUnits.A

    assert isinstance(voltage1, ObisValueFloat)
    assert voltage1.raw_value == 1.1
    assert voltage1.value == 1.1
    assert voltage1.unit == PhysicalUnits.V

    assert isinstance(voltage2, ObisValueFloat)
    assert voltage2.raw_value == 10
    assert voltage2.value == 100
    assert voltage2.unit == PhysicalUnits.V

    assert isinstance(voltage3, ObisValueFloat)
    assert voltage3.raw_value == 0.4
    assert voltage3.value == 40
    assert voltage3.unit == PhysicalUnits.V

    assert isinstance(realPowerIn, ObisValueFloat)
    assert realPowerIn.raw_value == 0
    assert realPowerIn.unit == PhysicalUnits.W

    assert isinstance(realPowerOut, ObisValueFloat)
    assert realPowerOut.raw_value == 0
    assert realPowerOut.unit == PhysicalUnits.W

    assert isinstance(realPowerDelta, ObisValueFloat)
    assert realPowerDelta.raw_value == 0
    assert realPowerDelta.unit == PhysicalUnits.W

    assert isinstance(realPowerIn, ObisValueFloat)
    assert realPowerIn.raw_value == 0
    assert realPowerIn.unit == PhysicalUnits.W

    assert isinstance(realPowerOut, ObisValueFloat)
    assert realPowerOut.raw_value == 0
    assert realPowerOut.unit == PhysicalUnits.W

    assert isinstance(realEnergyIn, ObisValueFloat)
    assert realEnergyIn.raw_value == 0
    assert realEnergyIn.unit == PhysicalUnits.Wh

    assert isinstance(realEnergyOut, ObisValueFloat)
    assert realEnergyOut.raw_value == 0
    assert realEnergyOut.unit == PhysicalUnits.Wh

    assert isinstance(reactiveEnergyIn, ObisValueFloat)
    assert reactiveEnergyIn.raw_value == 0
    assert reactiveEnergyIn.unit == PhysicalUnits.varh

    assert isinstance(reactiveEnergyOut, ObisValueFloat)
    assert reactiveEnergyOut.raw_value == 0
    assert reactiveEnergyOut.unit == PhysicalUnits.varh

    assert isinstance(deviceNumber, ObisValueBytes)
    assert deviceNumber.raw_value == ""

    assert isinstance(logicalDeviceNumber, ObisValueBytes)
    assert logicalDeviceNumber.raw_value == ""


def t_Obisdata_no_wanted_values():
    """Test the ObisObisDataValue class."""

    my_wanted_values: list[str] = []
    my_supplier = SupplierTINETZ()
    frame1 = ""
    frame2 = ""
    my_key_hex_string = ""

    my_decrypt = Decrypt(my_supplier, frame1, frame2, my_key_hex_string)
    my_obisdata = ObisData(dec=my_decrypt, wanted_values=my_wanted_values)

    assert my_obisdata is not None
