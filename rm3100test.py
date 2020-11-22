from rm3100 import Sensor
import time


mag = Sensor(0)
while 1:
    print(mag.read_and_initiate())
    time.sleep(2)
