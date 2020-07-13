import time
import sched
import busio
import board
import math
import adafruit_mlx90393

#user parameters
#pollingRate in Hz, max 25
pollingRate = 25
#number of decimals in sensor reading
decimals = 3

#set up sensor, start counter, convert pollingRate to cycleTime
print("Setting up, please wait")
I2C_BUS = busio.I2C(board.SCL, board.SDA)
SENSOR = adafruit_mlx90393.MLX90393(I2C_BUS, gain=adafruit_mlx90393.GAIN_1X)
timecounter = 0
cycleTime = 1 / pollingRate

#establish event scheduler
s = sched.scheduler(time.time, time.sleep)

#create file with format "MLX90393 DD-MM-YY H:M:S"
timestr = time.strftime("%d-%m-%Y %H:%M:%S")
filename = "MLX90393 " + timestr + ".csv"
f = open(filename, "a")
f.write("Seconds,X (uT),Y (uT),Z (uT)\n")
f.close()

#truncate function
def truncate(number, dec):
    if decimals == 0:
        return math.trunc(number)
    factor = 10.0 ** dec
    return math.trunc(number * factor) / factor

#read sensor measurements
def sensorRead(sc):
    global timecounter
    global cycleTime
    global decimals
    f = open(filename, "a")
    MX, MY, MZ = SENSOR.magnetic
    magX = str(truncate(float("{}".format(MX)), decimals))
    magY = str(truncate(float("{}".format(MY)), decimals))
    magZ = str(truncate(float("{}".format(MZ)), decimals))
    f.write(str(truncate(timecounter, 2)) + "," + magX + "," + magY + "," + magZ + "\n")
    s.enter(cycleTime, 1, sensorRead, (sc,))
    f.close()
    print("Time: " + str(truncate(timecounter, 2)) + " seconds")
    timecounter += cycleTime

s.enter(cycleTime, 1, sensorRead, (s,))
s.run()

