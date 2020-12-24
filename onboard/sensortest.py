import json
import time
from datetime import datetime

import board
import busio
import requests
from adafruit_mcp230xx.mcp23017 import MCP23017
from digitalio import Direction
from sensor_array import SensorArray, MCPArray

global server_ip
server_ip = "192.168.1.61"

if __name__ == "__main__":

    i2c = busio.I2C(board.SCL, board.SDA)
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

    if spi.try_lock():
        print("SPI Locked")

    spi.configure(baudrate=100000)

    mcp = MCP23017(i2c)
    select1 = mcp.get_pin(0)
    select1.direction = Direction.OUTPUT

    sensor_array_dimensions = {
        "x": 1,
        "y": 1,
        "z": 1
    }

    mcp = MCPArray([0x20], i2c)
    sensor_array = SensorArray(sensor_array_dimensions, mcp, spi)

    payload = {"name": str(datetime.now())}
    payload.update({"dimensions": sensor_array_dimensions})

    r = requests.post(
        f"http://{server_ip}:8080/new/createtable",
        data=json.dumps(payload)
    )

    table_name = r.text

    while True:
        print("Starting measurement...")
        measurement = sensor_array.read(str(datetime.now()))
        r = requests.post(
            f"http://{server_ip}:8080/new/appendrow",
            params={"table": table_name},
            data=measurement
        )
        time.sleep(0.25)

