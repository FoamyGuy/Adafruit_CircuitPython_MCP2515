# SPDX-FileCopyrightText: Copyright (c) 2020 Bryan Siepert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""Python implementation of the CircuitPython core `canio` API"""
# pylint:disable=too-few-public-methods
import time


class Message:
    """A class representing a message to send on a `canio` bus
    """

    # pylint:disable=too-many-arguments,invalid-name,redefined-builtin
    def __init__(self, id, data=None, size=None, rtr=False, extended=False):
        """Create a `Message` to send

        Args:
            id (int): The numeric ID of the message
            data (bytes): The content of the message
            size (int): The amount of data requested, for an rtr
            rtr (bool): True if the message represents an rtr (Remote Transmission Request)
            extended (bool): True if the
        Raises:
            AttributeError: If `data` of type `bytes` is not provided for a non-RTR message
            AttributeError: If `data` is larger than 8 bytes
            AttributeError: If `size` is set for a non-RTR message
        """

        if size is not None and not rtr:
            raise AttributeError("non-RTR canio.Message should not set a `size`")

        self._rtr = None
        self._data = None
        self._id = None
        self.id = id
        self.data = data
        self.extended = extended
        self.size = size
        self.rtr = rtr

    @property
    def data(self):
        """The content of the message, or dummy content in the case of an rtr"""
        return self._data

    @data.setter
    def data(self, new_data):
        if (new_data is None) or (
            not (type(new_data) in [bytes, bytearray]) and not self.rtr
        ):

            raise AttributeError(
                "non-RTR canio.Message must have a `data` argument of type `bytes`"
            )
        if len(new_data) > 8:
            raise AttributeError(
                "`canio.Message` object data must be of length 8 or less"
            )
        # self.rtr = False
        # self._data = new_data
        self._data = bytearray(new_data)

    @property
    def rtr(self):
        """True if the message represents a remote transmission request (RTR). Setting rtr to true\
            zeros out data
        """
        return self._rtr

    @rtr.setter
    def rtr(self, is_rtr):
        if is_rtr and self.data:
            self.data = bytes(len(self._data))
        self._rtr = is_rtr


# import _canio
# import board
# import digitalio
# import time

# d = digitalio.DigitalInOut(board.LED)
# d.switch_to_output()

# standby = digitalio.DigitalInOut(board.CAN_STANDBY)
# standby.switch_to_output(False)

# c = _canio.CAN(rx=board.CAN_RX, tx=board.CAN_TX, baudrate=1000000)

# m = _canio.Message()
# l = c.listen(timeout=1)

# while True:
#     if l.readinto(m):
#         d.value = not d.value
#         print("received", m.id, m.rtr, m.size, m.data)
#     else:
#         print("Nothing received before timeout")
#### Leftovers from the initial version of the MCP lib, to be removed/replaced with canio classes

# with bus() as b, b.listen(timeout=.1) as l:
#     for size in sizes:
#         print("Test messages of size", size)
#         mo = Message(id=0x5555555, extended=True, rtr=True, size=size)
#         b.send(mo)
#         assert l.readinto(mi)
#         assert mi.rtr
#         assert mi.id == 0x5555555
#         assert mi.extended
#         assert len(mi.data) == size

# class canio.Listener
# https://circuitpython.readthedocs.io/en/latest/shared-bindings/canio/index.html#canio.Listener
# Listens for CAN message

# canio.Listener is not constructed directly, but instead by calling the Listen method of a canio.
# CAN object.

# timeout:float
# read(self)
# Reads a message, after waiting up to self.timeout seconds

# If no message is received in time, None is returned. Otherwise, a Message is returned.


# in_waiting(self)
# Returns the number of messages waiting

# __iter__(self)
# Returns self, unless the object is deinitialized

# __next__(self)
# Reads a message, after waiting up to self.timeout seconds

# If no message is received in time, raises StopIteration. Otherwise, a Message is returned.

# deinit(self)
# Deinitialize this object, freeing its hardware resources

# __enter__(self)
# Returns self, to allow the object to be used in a
# The with statement statement for resource control

# __exit__(self, unused1, unused2, unused3)
# Calls deinit()
class Timer:
    """A class to track timeouts, like an egg timer
    """

    def __init__(self, timeout=0.0):
        self._timeout = None
        self._start_time = None
        if timeout:
            self.rewind_to(timeout)

    @property
    def expired(self):
        """Returns the expiration status of the timer

        Returns:
            bool: True if more than `timeout` seconds has past since it was set
        """
        return (time.monotonic() - self._start_time) > self._timeout

    def rewind_to(self, new_timeout):
        """Re-wind the timer to a new timeout and start ticking"""
        self._timeout = float(new_timeout)
        self._start_time = time.monotonic()


class Listener:
    """Listens for a CAN message

        canio.Listener is not constructed directly, but instead by calling the `listen` method of a\
        canio.CAN object.
    """

    def __init__(self, bus_obj):
        self._timer = Timer()
        self._bus_obj = bus_obj

    @property
    def timeout(self):
        """The maximum amount of time in seconds that `read` or `readinto` will wait before giving\
            up"""
        return self._read_timeout

    @timeout.setter
    def timeout(self, timeout):
        self._read_timeout = float(timeout)

    def read(self):
        """Reads a message. If after waiting up to self.timeout seconds if no message is received,\
            None is returned. Otherwise, a Message is returned."""
        self._timer.rewind_to(self._read_timeout)
        while not self._timer.expired:
            if self._bus_obj.unread_message_count == 0:
                continue
            return self._bus_obj.read_message()
        return None

    def readinto(self, message):
        """Reads the next available message into the given `Message` instance.

        Args:
            message (Message): The message object to fill with received message

        Returns:
            bool: True if a message was received within `timeout` seconds.
            bool: False if no message was received within the timeout
        """
        next_message = self.read()
        if next_message is None:
            return False
        message.id = next_message.id
        message.extended = next_message.extended
        message.data = next_message.data
        message.rtr = next_message.rtr

        return True

    def in_waiting(self):
        """Returns the number of messages waiting"""

    def __iter__(self):
        """Returns self, unless the object is deinitialized"""

    def __next__(self):
        """Reads a message, after waiting up to self.timeout seconds"""
        return self.read()

    # If no message is received in time, raises StopIteration. Otherwise, a Message is returned.

    def deinit(self):
        """Deinitialize this object, freeing its hardware resources"""

    def __enter__(self):
        """Returns self, to allow the object to be used in a The with statement statement for\
            resource control"""
        return self

    def __exit__(self, unused1, unused2, unused3):
        """Calls deinit()"""
        self.deinit()


class CANIdentifier:
    """A class representing the ID of a `canio` message"""

    def __init__(self):
        self.id = None  # pylint:disable=invalid-name
        self.is_extended = False


class CANMessage:
    """A class representing a CAN bus message"""

    def __init__(self):
        self.bytes = bytearray(8)
        self.rtr = False
        self.can_id = CANIdentifier()
