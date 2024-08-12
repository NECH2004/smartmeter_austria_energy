"""The Smartmeter definition."""
import binascii
import logging
import re
import time

import serial
from serial.serialutil import SerialException, SerialTimeoutException

from .decrypt import Decrypt
from .exceptions import (
    SmartmeterException,
    SmartmeterSerialException,
    SmartmeterTimeoutException,
)
from .obisdata import ObisData
from .supplier import Supplier, SUPPLIERS


class Smartmeter:
    """Connects and reads data from the smartmeter."""

    def __init__(
        self,
        supplier: Supplier,
        port: str,
        key_hex_string: str,
        interval: int = 1,
        baudrate: int = 2400,
        parity: str = serial.PARITY_NONE,
        stopbits: str = serial.STOPBITS_ONE,
        bytesize: str = serial.EIGHTBITS,
        serial_read_chunk_size: int = 100,
    ) -> None:
        self._supplier = supplier
        self._port: str = port
        self._key_hex_string = key_hex_string
        self._baudrate: int = baudrate
        self._parity: str = parity
        self._stopbits: str = stopbits
        self._bytesize: str = bytesize
        self._interval: int = interval
        self._serial_read_chunk_size: int = serial_read_chunk_size
        self._mySerial: serial.Serial = None
        self._logger = logging.getLogger(__name__)
        self._is_running: bool = False

    # read method was mainly taken from https://github.com/tirolerstefan/kaifa
    def read(self) -> ObisData:
        if self._is_running:
            return None

        try:
            self.__open_serial()

            is_running = self._mySerial.isOpen()
            self._is_running = is_running

            self._logger.debug("Start reading from serial.")

            stream = b""  # filled by serial device
            frame1 = b""  # parsed telegram1
            frame2 = b""  # parsed telegram2

            frame1_start_pos = -1  # pos of start bytes of telegram 1 (in stream)
            frame2_start_pos = -1  # pos of start bytes of telegram 2 (in stream)

            sleep_interval = 0.1
            self._logger.debug("Fetch next frame.")
            start_time = time.monotonic()
            max_stop_time = start_time + 5 * self._interval

            # "telegram fetching loop" (as long as we have found two full telegrams)
            # frame1 = first telegram (68fafa68), frame2 = second telegram (68727268)
            while is_running:
                self._logger.debug("Read in chunks.")
                if self._mySerial.inWaiting() > 0:
                    # Read in chunks. Each chunk will wait as long as specified by
                    # serial timeout. As the meters we tested send data every 5s the
                    # timeout must be <5. Lower timeouts make us fail quicker.
                    byte_chunk = self._mySerial.read(self._mySerial.inWaiting())
                    stream += byte_chunk
                    frame1_start_pos = stream.find(self._supplier.frame1_start_bytes)
                    frame2_start_pos = stream.find(self._supplier.frame2_start_bytes)

                    # fail as early as possible if we find the segment is not complete yet.
                    if (
                        (stream.find(self._supplier.frame1_start_bytes) < 0)
                        or (stream.find(self._supplier.frame2_start_bytes) <= 0)
                        or (stream[-1:] != self._supplier.frame2_end_bytes)
                        or (len(byte_chunk) == self._serial_read_chunk_size)
                    ):

                        self._logger.debug("Segment is not complete yet.")
                        actual_time = time.monotonic()
                        if actual_time < max_stop_time:
                            continue
                        else:
                            raise SmartmeterTimeoutException()

                    if frame2_start_pos != -1:
                        # frame2_start_pos could be smaller than frame1_start_pos
                        if frame2_start_pos < frame1_start_pos:
                            # start over with the stream from frame1 pos
                            stream = stream[frame1_start_pos : len(stream)]
                            continue

                        # we have found at least two complete telegrams
                        regex = binascii.unhexlify("28" + self._supplier.frame1_start_bytes_hex + "7c" + self._supplier.frame2_start_bytes_hex + "29")  # re = '(..|..)'
                        my_list = re.split(regex, stream)
                        my_list = list(filter(None, my_list))  # remove empty elements
                        # l after split (here in following example in hex)
                        # l = ['68fafa68', '53ff00...faecc16', '68727268', '53ff...3d16', '68fafa68', '53ff...d916', '68727268', '53ff.....']

                        # take the first two matching telegrams
                        for i, el in enumerate(my_list):
                            if el == self._supplier.frame1_start_bytes:
                                frame1 = my_list[i] + my_list[i + 1]
                                frame2 = my_list[i + 2] + my_list[i + 3]
                                break

                        # check for weird result -> exit
                        if (len(frame1) == 0) or (len(frame2) == 0):
                            self._logger.debug("Exit because of weird result.")
                            is_running = False

                        break

                # Optional, but recommended: sleep once per loop to let
                # other threads on your PC run during this time.
                time.sleep(sleep_interval)

                actual_time = time.monotonic()
                if actual_time < max_stop_time:
                    continue
                else:
                    raise SmartmeterTimeoutException()

            self._logger.debug("Next step is decrypting.")
            dec = Decrypt(self._supplier, frame1, frame2, self._key_hex_string)
            dec.parse_all()

            obisData = ObisData(dec, self._supplier.supplied_values)
            return obisData
        except Exception as exception:
            raise SmartmeterException() from exception
        finally:
            self._is_running = False
            self.__close_serial()

    def __open_serial(self):
        try:
            self._mySerial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                parity=self._parity,
                stopbits=self._stopbits,
                bytesize=self._bytesize,
                timeout=self._interval,
            )
        except SerialTimeoutException as ex:
            self._logger.debug("Timeout happened at closing.")
            raise SmartmeterTimeoutException(f"'{self._port}' has a timeout.") from ex
        except SerialException as ex:
            self._logger.debug("SerialException happened at closing.")
            raise SmartmeterSerialException(f"'{self._port}' cannot be opened.") from ex
        except Exception as ex:
            self._logger.debug("Exception happened at closing.")
            raise SmartmeterException(f"Connection to '{self._port}' failed.") from ex

    def __close_serial(self):
        try:
            self._mySerial.close()
        except Exception as ex:
            raise SmartmeterException(f"Closing port '{self._port}' failed.") from ex
