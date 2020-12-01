import board
import busio
from digitalio import Direction
from adafruit_mcp230xx.mcp23017 import MCP23017
from onboard.rm3100 import RM3100

i2c = busio.I2C(board.SCL, board.SDA)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

if spi.try_lock():
    print("SPI Locked")

spi.configure(baudrate=5000)

mcp = MCP23017(i2c)
select = mcp.get_pin(0)
select.direction = Direction.OUTPUT

sensor = RM3100(select, spi)



