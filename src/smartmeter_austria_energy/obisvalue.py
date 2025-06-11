"""Defines value objects for OBIS data."""

import math

from .constants import PhysicalUnits


class ObisValueFloat:
    """Defines value objects for floats."""

    def __init__(
        self, raw_value: float, unit: PhysicalUnits = PhysicalUnits(0), scale: int = 0
    ) -> None:
        self._raw_value = raw_value
        self._scale = scale
        self._unit = unit

    def __add__(self, other: "ObisValueFloat"):
        if self.unit == other.unit:
            x = self.value + other.value
            return ObisValueFloat(x, self.unit)
        return ObisValueFloat(math.nan)

    def __sub__(self, other: "ObisValueFloat"):
        if self.unit == other.unit:
            x = self.value - other.value
            return ObisValueFloat(x, self.unit)
        return ObisValueFloat(math.nan)

    @property
    def raw_value(self) -> float:
        """The unformatted OBIS value."""
        return self._raw_value

    @property
    def scale(self) -> float:
        """The scale factor of OBIS value."""
        return self._scale

    @property
    def unit(self) -> PhysicalUnits:
        """The physical unit of the OBIS value."""
        return self._unit

    @property
    def value(self) -> float:
        """The OBIS value."""
        return self._raw_value * 10**self._scale

    @property
    def value_string(self) -> str:
        """The OBIS value formatted including unit."""
        return f"{self.value} {self.unit.name}"


class ObisValueBytes:
    """Defines value objects for byte arrays."""

    def __init__(self, raw_value: bytes) -> None:
        self._raw_value = raw_value

    @property
    def raw_value(self) -> bytes:
        """The unformatted OBIS value."""
        return self._raw_value

    @property
    def value(self) -> str:
        """The OBIS value."""
        return self._raw_value.decode()
