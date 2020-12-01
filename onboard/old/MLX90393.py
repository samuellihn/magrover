import time
import sched
import busio
import board
import math
import adafruit_mlx90393


def truncate(number, dec):
    if dec == 0:
        return math.trunc(number)
    factor = 10.0 ** dec
    return math.trunc(number * factor) / factor


class RoverSensor:

    def __init__(self, polling_rate=10, decimals=3, sensor_type="MLX90393"):
        # user parameters
        self.run_time = input("Enter the desired runtime in minutes: ")
        if self.run_time == "":
            self.run_time = -1

        self.run_time = float(self.run_time)

        filename_add = input("Enter anything you would like to add to the filename: ")
        # pollingRate in Hz, max 25
        self.polling_rate = polling_rate
        # number of decimals in sensor reading
        self.decimals = decimals

        # set up sensor, start counter, convert pollingRate to cycleTime
        print("Setting up, please wait")
        i2c_bus = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_mlx90393.MLX90393(i2c_bus, gain=adafruit_mlx90393.GAIN_1X)
        self.time_counter = 0

        # establish event scheduler
        self.scheduler = sched.scheduler(time.time, time.sleep)

        # create file with format "MLX90393 DD-MM-YY H:M:S"
        time_str = time.strftime("%d-%m-%Y %H:%M:%S")
        self.filename = sensor_type + " " + time_str + " " + filename_add + ".csv"
        f = open(self.filename, "a")
        f.write("Polling rate " + str(polling_rate) + " Hz test run on sensor ")
        f.write(sensor_type + " at " + time_str + "\n")
        f.write("Seconds,X (uT),Y (uT),Z (uT)\n")
        f.close()

    @property
    def time_decimals(self):
        return math.floor(self.polling_rate / 10)

    @property
    def run_time_in_seconds(self):
        return self.run_time * 60

    @property
    def cycle_time(self):
        return 1.0 / self.polling_rate

    # read sensor measurements
    def schedule_read_sensor(self):
        if self.time_counter <= self.run_time_in_seconds or self.run_time == -1:
            self.scheduler.enter(self.cycle_time, 1, self.read_sensor)

    # read sensor measurements
    def read_sensor(self):

        self.schedule_read_sensor()

        mx, my, mz = self.sensor.magnetic
        mag_x = str(truncate(float("{}".format(mx)), self.decimals))
        mag_y = str(truncate(float("{}".format(my)), self.decimals))
        mag_z = str(truncate(float("{}".format(mz)), self.decimals))

        f = open(self.filename, "a")
        f.write(str(truncate(self.time_counter, 2)) + "," + mag_x + "," + mag_y + "," + mag_z + "\n")
        f.close()
        print("Time: " + str(truncate(self.time_counter, self.time_decimals)) + " seconds")
        self.time_counter += self.cycle_time

    def run(self):

        self.schedule_read_sensor()
        self.scheduler.run()


# --------------------------------
if __name__ == "__main__":
    r = RoverSensor()
    r.run()
