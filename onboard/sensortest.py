import board
import busio
import time
from digitalio import Direction
from adafruit_mcp230xx.mcp23017 import MCP23017
from rm3100 import RM3100
import web


class LiveData:
    def GET(self):
        measurements = sensor.read()
        return f"{time.time()}, {measurements.x}, {measurements.y}, {measurements.z}"

if __name__ == "__main__":

    i2c = busio.I2C(board.SCL, board.SDA)
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

    if spi.try_lock():
        print("SPI Locked")

    spi.configure(baudrate=5000)

    mcp = MCP23017(i2c)
    select1 = mcp.get_pin(0)
    select1.direction = Direction.OUTPUT

    select2 = mcp.get_pin(1)
    select2.direction = Direction.OUTPUT

    sensor = RM3100(select1, spi)

    urls = (
        '/livedata', 'LiveData'
    )
    app = web.application(urls, globals())
    app.run()


