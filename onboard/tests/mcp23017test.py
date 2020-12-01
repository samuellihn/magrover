import board
import busio
from digitalio import Direction
from adafruit_mcp230xx.mcp23017 import MCP23017
import time
i2c = busio.I2C(board.SCL, board.SDA)

mcp = MCP23017(i2c)
pin = []

for x in range(16):
    pin.append(0)

for x in range(8, 16):
    pin[x] = mcp.get_pin(x)
    pin[x].direction = Direction.OUTPUT

while 1:
    for x in range(8, 16):
        pin[x].value = True
        time.sleep(0.10)
        pin[x].value = False
        time.sleep(0.10)

