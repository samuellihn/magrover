import spidev
import board
import busio
import math
from digitalio import Direction
from adafruit_mcp230xx.mcp23017 import MCP23017

i2c = busio.I2C(board.SCL, board.SDA)


def to_bytes(integer):
    return divmod(integer, 0x100)


def twos_comp(val, bits=12):
    """compute the 2's complement of int value val"""
    if (val[0] & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val[0] = val[0] - (1 << bits)        # compute negative value
    return val[0]

class Sensor:
    def __init__(self, sensor_num, cycle_count=200):
        # init mcp23017
        mcp = [0, 0]
        mcp[0] = MCP23017(i2c, address=0x20 + 0)
        try:
            mcp[1] = MCP23017(i2c, address=0x20 + 1)
        except ValueError:
            print("Only one MCP detected")
        mcp_chip_number = math.floor(sensor_num / 16)
        mcp_pin_number = sensor_num % 16
        print(f"Pin {mcp_pin_number} at MCP {mcp_chip_number}")
        self.ssn = mcp[mcp_chip_number].get_pin(mcp_pin_number)
        self.ssn.direction = Direction.OUTPUT
        self.ssn.value = True

        # open spi bus
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.mode = 0
        self.spi.max_speed_hz = 500

        # select chip
        self.ssn.value = False

        # set cycle count registers
        self.cycle_count = hex(cycle_count)
        cycle_bytes = to_bytes(cycle_count)
        print(cycle_bytes)

        # [0] MSB [1] LSB
        # send cycle counts to registers
        self.spi.xfer([0x04, cycle_bytes[0], cycle_bytes[1], cycle_bytes[0], cycle_bytes[1], cycle_bytes[0], cycle_bytes[1]])
        self.ssn_switch()

        # initiate one measurement of all three axes, bit format 0b0zyx000
        self.spi.xfer([0x00, 0b0111000])

        # deselect chip
        self.ssn.value = True

    def ssn_switch(self):
        self.ssn.value = True
        self.ssn.value = False

    def read(self):

        # deselect chip
        self.ssn.value = True

        # poll until status byte returns true
        while True:
            self.ssn.value = False
            status = self.spi.readbytes(1)[0]
            print(f"Status is {status}")
            if status >= 128:
                # read bytes
                sensor_data_x = self.spi.readbytes(3)
                sensor_data_y = self.spi.readbytes(3)
                sensor_data_z = self.spi.readbytes(3)
                break
            else:
                # if measurement is not ready, reset ssn and try again
                self.ssn.value = True
                
        # deselect chip
        print(self.ssn.value)
        self.ssn.value = True
        
        # return values
        print(sensor_data_x, sensor_data_y, sensor_data_z)
        values = self.sensor_data_xyz(sensor_data_x, sensor_data_y, sensor_data_z)
        print(values)
        return values
    
    def process_sensor_data(self, sensor_data):
        raw_value = twos_comp(sensor_data)
        value_in_ut = raw_value / 8388608 * 800
        return value_in_ut

    def sensor_data_xyz(self, sensor_data_x, sensor_data_y, sensor_data_z):
        x_ut = self.process_sensor_data(sensor_data_x)
        y_ut = self.process_sensor_data(sensor_data_y)
        z_ut = self.process_sensor_data(sensor_data_z)
        return x_ut, y_ut, z_ut
    
    def initiate_new_measurement(self):
        self.ssn.value = False
        # initiate one measurement of all three axes, bit format 0b0zyx000
        self.spi.xfer([0x00, 0b0111000])
        self.ssn.value = True

#   Use this method for normal read
    def read_and_initiate(self):
        mx, my, mz = self.read()
        self.initiate_new_measurement()
        return mx, my, mz
        






