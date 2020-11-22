import math
import rm3100


class MagArray:

    def __init__(self, cycle_count=200):
        self.mag = []
        # creates a 3d array of sensors
        for num in range(0, 26):
            self.mag[num % 3][(math.floor(num / 3)) % 3][math.floor(num / 9)] = rm3100.Sensor(num, cycle_count)

        self.mag_readings = []

    def read_values(self):
        mag_readings = []
        for x in range(0, 2):
            for y in range(0, 2):
                for z in range(0, 2)
                    mag_readings[x][y][z] = self.mag[x][y][z].read_and_initiate()
        return mag_readings

