import board
import busio
import time
from digitalio import Direction
from adafruit_mcp230xx.mcp23017 import MCP23017
from rm3100 import RM3100

i2c = busio.I2C(board.SCL, board.SDA)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)



if spi.try_lock():
    print("SPI Locked")

spi.configure(baudrate=5000)


mcp = MCP23017(i2c)
select = mcp.get_pin(0)
select.direction = Direction.OUTPUT


sensor = RM3100(select, spi)

while True:
    sensor_measurement = sensor.read()
    print("\033[H\033[J")
    print(f'X: {sensor_measurement.x} uT,\tY: {sensor_measurement.y} uT,\tZ: {sensor_measurement.z} uT')
    time.sleep(0.25)
