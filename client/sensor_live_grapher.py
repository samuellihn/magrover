import requests]
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

global pi_ip
pi_ip = "192.168.1.238"


# Create figure for plotting
fig = plt.figure()
axz = fig.add_subplot(3, 1, 3)
axy = fig.add_subplot(3, 1, 2, sharex=axz)
axx = fig.add_subplot(3, 1, 1, sharex=axz)


t_graph = []
mx = []
my = []
mz = []

# This function is called periodically from FuncAnimation
def animate(i, t_graph, mx, my, mz):

    # Read temperature (Celsius) from TMP102

    # Add x and y to lists
    data_request = requests.get(f"http://{pi_ip}:8080/livedata")
    data_row = data_request.text.split(", ")

    t_graph.append(f"{data_row[0]}:{data_row[1]}:{data_row[2]}.{data_row[3]}")
    mx.append(round(float(data_row[4]) * 1000 * 1000) / 1000)
    my.append(round(float(data_row[5]) * 1000 * 1000) / 1000)
    mz.append(round(float(data_row[6]) * 1000 * 1000) / 1000)

    t_graph = t_graph[-100:]
    mx = mx[-100:]
    my = my[-100:]
    mz = mz[-100:]

    # Draw x and y lists
    axx.clear()
    axx.plot(t_graph, mx)
    axy.clear()
    axy.plot(t_graph, my)
    axz.clear()
    axz.plot(t_graph, mz)

    # Format plot
    plt.setp(axx.get_xticklabels(), visible=False)
    plt.setp(axy.get_xticklabels(), visible=False)
    plt.setp(axz.get_xticklabels(), rotation=45.0)

    plt.title("RM3100 Sensor Data")
    axx.set_title("X")
    axy.set_title("Y")
    axz.set_title("Z")


# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(t_graph, mx, my, mz), interval=200)
plt.show()