import time


# Turns a 2 byte long integer into two 1 byte integers
def int16_to_bytes(value):

    return divmod(value, 0x100)


# Register datatype containing a read and write address
class Register:

    def __init__(self, value):
        self.write = value.to_bytes(1, 'big')
        self.read = (value + 0x80).to_bytes(1, 'big')


# Partial register map for the PNI RM3100 Sensor
class RegisterMap:

    # To read from a register, send the read address and the data will appear on MISO
    # TO write to a register, send the write address followed by the value to be written

    # Register Map

    continuous_measurement = Register(0x01)
    continuous_data_rate = Register(0x0B)
    single_measurement = Register(0x00) # Format 0x0zyx0000
    status = Register(0x34)

    # Cycle Count Registers
    x_cycle_msb = Register(0x04)
    x_cycle_lsb = Register(0x05)
    y_cycle_msb = Register(0x06)
    y_cycle_lsb = Register(0x07)
    z_cycle_msb = Register(0x08)
    z_cycle_lsb = Register(0x09)

    # Measurement Registers
    mx_2 = Register(0x24)
    mx_1 = Register(0x25)
    mx_0 = Register(0x26)
    my_2 = Register(0x27)
    my_1 = Register(0x28)
    my_0 = Register(0x29)
    mz_2 = Register(0x2A)
    mz_1 = Register(0x2B)
    mz_0 = Register(0x2C)


class RM3100Measurement:

    x = 0
    y = 0
    z = 0

    def __init__(self, sensor_data):
        # Split raw sensor data
        x_bytes = sensor_data[0:3]
        y_bytes = sensor_data[3:6]
        z_bytes = sensor_data[7:9]

        # Converts twos compliment bytearrays to integers
        x_measurement = int.from_bytes(x_bytes, byteorder='big', signed=True)
        y_measurement = int.from_bytes(y_bytes, byteorder='big', signed=True)
        z_measurement = int.from_bytes(z_bytes, byteorder='big', signed=True)

        # Converts integers to measurements in microtesla +800 to -800
        self.x = self.to_microtesla(x_measurement)
        self.y = self.to_microtesla(y_measurement)
        self.z = self.to_microtesla(z_measurement)

    def to_microtesla(self, measurement):
        measurement *= 800
        measurement /= 8388608
        return measurement

    def to_dict(self):
        encode = {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }
        return encode

    def __str__(self):
        return f"[{self.x}, {self.y}, {self.z}]"


class RM3100:

    def __init__(self, select, spi):
        """
        Creates a RM3100 sensor object
        :param select: Chip select MCP pin to use
        :param spi: SPI bus to use
        """
        self.registers = RegisterMap()
        self.select_pin = select
        self.spi = spi

        self.select_pin.value = True

    def read(self, read_x=True, read_y=True, read_z=True):
        """
        Reads selected axes and returns a Measurement object with x, y, and z values in microteslas
        :param read_x: Whether to read X axis
        :param read_y: Whether to read Y axis
        :param read_z: Whether to read Z axis
        :return: Measurement object with measurements in uT
        """
        self.initiate_single_measurement(read_x, read_y, read_z)
        raw_measurement = self.read_measurement()
        measurement = RM3100Measurement(raw_measurement)
        return measurement

    # Sets the cycle count registers
    def set_cycle_count(self, cycle_x, cycle_y, cycle_z):
        """
        Sets the cycle count for the RM3100 sensor
        :param cycle_x: Cycle count value X
        :param cycle_y: Cycle count value Y
        :param cycle_z: Cycle count value Z
        """
        # Converts the parameters to a bytearray payload
        cycle_x_bytes = bytearray(int16_to_bytes(cycle_x))
        cycle_y_bytes = bytearray(int16_to_bytes(cycle_y))
        cycle_z_bytes = bytearray(int16_to_bytes(cycle_z))

        # Sends the payload to the cycle count registers
        self.select_pin.value = False
        self.spi.write(self.registers.x_cycle_msb.write)
        self.spi.write(cycle_x_bytes)
        self.spi.write(cycle_y_bytes)
        self.spi.write(cycle_z_bytes)

        self.select_pin.value = True

    # Initiates a single measurement from the sensor
    def initiate_single_measurement(self, x=True, y=True, z=True):
        """
        Initiates a single RM3100 measurement
        :param x: Whether to read X axis
        :param y: Whether to read Y axis
        :param z: Whether to read Z axis
        :return:
        """
        self.select_pin.value = False

        # Sends value depending on input values
        measurement_value = 0b00000000
        if x:
            measurement_value += 0b00010000
        if y:
            measurement_value += 0b00100000
        if z:
            measurement_value += 0b01000000
        self.spi.write(self.registers.single_measurement.write)
        self.spi.write(measurement_value.to_bytes(1, "big"))

        self.select_pin.value = True

    def read_measurement(self):
        """
        Reads a measurement from the sensor and returns a bytearray of length 9
        :return: A 9 byte ByteArray with 3 bytes for x, y, and z in big endian
        """
        is_ready = bytearray([0])
        while True:
            self.select_pin.value = False
            self.spi.write_readinto(self.registers.mx_2.read, is_ready)
            if int.from_bytes(is_ready, 'big') >= 0x80:
                break
            else:
                self.select_pin.value = True

        # Reads values
        read_buffer = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.spi.readinto(read_buffer)
        self.select_pin.value = True
        return read_buffer

