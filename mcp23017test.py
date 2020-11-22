import board
import busio
from digitalio import Direction
from adafruit_mcp230xx.mcp23017 import MCP23017
import time
i2c = busio.I2C(board.SCL, board.SDA)

mcp = MCP23017(i2c)
pin = [0, 0, 0, 0]
pin[0] = mcp.get_pin(6)
pin[1] = mcp.get_pin(7)
pin[2] = mcp.get_pin(8)
pin[3] = mcp.get_pin(9)
cs = mcp.get_pin(0)
cs.direction = Direction.OUTPUT
for x in range(4):
    pin[x].direction = Direction.OUTPUT
while 1:
    for x in range(4):
        pin[x].value = True
        cs.value = True
        time.sleep(0.10)
        pin[x].value = False
        cs.value = False
        time.sleep(0.10)

