# introdcue
## start
####It is very simple to use, just execute ./shell.sh 0 to start a node. Any number of nodes can be started in this system
#### command:  ./shell.sh 0  ./shell.sh 1  ./shell.sh 2   ./shell.sh 3  ./shell.sh 4

## Query data
####You can use this interface to access data:http://127.0.0.1:33351/r0/humidity http://localhost:33351/r0/humidity  
we can change the node r0 to r1 ... r5

#### you also can change temperature to wind speed or humidity

#### Terminate the process: ./terminate.sh

## Areas that can be modified:

You can define a utility class and place commonly used functions in it, such as hashstr, get_host_ip, to avoid duplicating these basic functions. Then, each Python file can reference this utility class.

The hashstr function can use a more complex hashing algorithm, such as SHA-256, to improve security.

You can write client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client = socket.SocketType(family=socket.AF_INET, type=socket.SOCK_STREAM), making it more understandable.

Both sensor.py and web.py define the class Client. You can write a separate file to define the class Client and import this class into sensor.py and web.py.

Write a script to real-time fetch weather information and store it in a CSV file. This brings it closer to a real sensor.

In web.py, instead of creating a Flask application, you can use a different framework or socket to create another application, generating a different display interface.

## Questions:

Can start a node on one device. The current issue is how to start multiple nodes on multiple devices.

Why do both sensor.py and client.py define class Client? Does this cause confusion?

What is the purpose of a.py and test.py? It seems that the project can run normally without these two files.

How to understand the numerous interfaces and ports in this project?

How is data displayed on the webpage extracted from the data table?

What is the structure of data packets? Where are they defined?

How to run this project on different devices, query sensor data transmitted to other devices on one device, and display this data?

Where are the interest array and Outface in interests.py input?

Why specify the code as Python 2.6? Is Python 3 not suitable?

What is the purpose of client.py? How to use client.py?

Where are the parameters in the Send_data(self, Infaces, fib, data) function in data.py passed from?

## Learning Record Update:

The webpage displaying data refreshes every few minutes, approximately three minutes, not in real-time. Time and information both refresh. Checking sensor.py indicates that this interval is specifically 200 seconds because of time.sleep(200). The node reads data from the sensor every 200 seconds.

Sensor-type data is data read by the node from the sensor. Interest-type data is obtained by directly changing the type of sensor-type data (Type: sensor->interest). Data-type data is data flowing between nodes. Therefore, interests.py seems redundant, as all interest-type data is directly generated from sensor-type data.

If there is an error in the program, it may be that the webpage port is occupied. Pay attention to modifying the port for displaying the webpage.

Unnecessary files to be removed: a.py (a simplified version of server.py for debugging server methods), client.py (replaced by sensor.py), test.py (a test file, currently empty), interests.py (interest-type data packets are directly generated from sensor-type data packets).


## Todo:

Modify the fib function in sensor.py to use table lookups or switch to a different shortest path algorithm, such as Dijkstra's algorithm.

Refactor the code by defining a utility class. Place commonly used functions like hashstr and get_host_ip into this class to avoid redundant code. Then, reference this utility class in each Python file.

Change the city names from r0/r1/r2 to actual cities, such as Dublin, Cork, Beijing, etc.

Fix the unit display issue in the webpage. The current units seem to be garbled.

Call a real-time weather data API instead of using sensor.py to read data from the table.

Optionally, shorten the data update interval. Reduce the time.sleep in sensor.py to make the program closer to real-time data acquisition.

Find a new application scenario for this project.

Resolve the issue of not being able to access the local area network (LAN) IP addresses during project runtime. The project prints the information:

Running on http://127.0.0.1:33351
Running on http://10.35.70.3:33351
Even with the school's VPN enabled, it's not possible to access these addresses through the browser. The following URLs also cannot be accessed:

http://127.0.0.1:33351/r0/temperature
http://10.35.70.3:33351/r0/temperature
I can only access the information on the webpage by using the following commands on the Raspberry Pi:

curl http://127.0.0.1:33351/r0/temperature
curl http://127.0.0.1:33351/r1/temperature
Accessing the information with the command:

curl http://10.35.70.3:33351/r0/temperature
also doesn't work.
The teacher has opened the following ports (see blackboard):

Open ports: 33000:34000/tcp ALLOW 10.35.70.0/24
3000:34000/udp ALLOW 10.35.70.0/24
In theory, even if it's not possible to access through the local browser, it should be possible to access by entering the command:

curl http://10.35.70.3:33351/r0/temperature
on the Raspberry Pi. This key issue needs to be resolved.
