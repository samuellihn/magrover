import board
import busio
from digitalio import Direction
from adafruit_mcp230xx.mcp23017 import MCP23017
from rm3100 import RM3100

import os
import math
import json


class MCPArray:

    mcp_arr = []

    def __init__(self, addr_array, i2c):
        """
        Creates an array of MCP chips that indexes itself
        :param addr_array: Array of I2C addresses to assign the chips
        :param i2c: I2C bus to use
        """
        for addr in addr_array:
            self.mcp_arr.append(MCP23017(i2c, address=addr))

    def get_pin(self, number):
        """
        Returns a pin from the MCP array
        :param number: desired index of pin
        :return: A MCP pin object
        """
        mcp_index = math.floor(number / 16)
        mcp_pin = number % 16
        pin = self.mcp_arr[mcp_index].get_pin(mcp_pin)
        pin.direction = Direction.OUTPUT
        return pin

    def get_pin_3d(self, x_index, y_index, z_index, dimensions):
        """
        Returns a MCP pin object given a 3d index
        :param dimensions: dimensions of the sensor array
        :return:
        """
        index = x_index * dimensions["x"] * dimensions["y"] + y_index * dimensions["x"] + z_index
        return self.get_pin(index)

class SensorArrayMeasurement:

    def __init__(self, dimensions, timestamp):
        self.data = []
        self.time = timestamp
        for x in range(dimensions["x"]):
            self.data.append([])
            for y in range(dimensions["y"]):
                self.data[x].append([])
                for z in range(dimensions["z"]):
                    self.data[x][y].append(None)

class SensorArray:

    sensors = []
    chip_selects = []

    def __init__(self, dimensions, mcp_array, spi):
        """
        A three dimensional array of RM3100 sensors
        :param dimensions: Dimensions of sensor array
        :param mcp_array: MCPArray object for chip selects
        :param spi: SPI bus to use
        """
        self.dimensions = dimensions
        self.mcp_array = mcp_array

        for x in range(self.dimensions["x"]):
            self.chip_selects.append([])
            for y in range(self.dimensions["y"]):
                self.chip_selects[x].append([])
                for z in range(self.dimensions["z"]):
                    self.chip_selects[x][y].append(self.mcp_array.get_pin_3d(x, y, z, self.dimensions))

        for x in range(self.dimensions["x"]):
            self.sensors.append([])
            for y in range(self.dimensions["y"]):
                self.sensors[x].append([])
                for z in range(self.dimensions["z"]):
                    self.sensors[x][y].append(RM3100(self.chip_selects[x][y][z], spi))

    def read(self, time):
        """
        Reads the entire array of sensors and returns a JSON string with data
        :return:
        """
        measurement = SensorArrayMeasurement(self.dimensions, time)
        for x in range(self.dimensions["x"]):
            for y in range(self.dimensions["y"]):
                for z in range(self.dimensions["z"]):
                    measurement.data[x][y][z] = (self.sensors[x][y][z].read().to_dict())

        try:
            os.remove("measurement.json.tmp")
        except FileNotFoundError:
            pass

        return json.dumps(measurement.__dict__)



