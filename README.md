# Instructions to run the project
1. Copy the whole folder along with the .env file to the Rpi.
2. Run the code using the `runme.sh` shell script using the below command:
    ```
    ./runme.sh
    ```
    This script creates a virtual environment, installs all the required dependencies and runs a tmux session with 5 split windows that each simulate a node and are running 5 different nodes.
3. [OPTIONAL] If the installation of the `cryptography` library fails; please follow the below set of commands to install rust:
    ```
    curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain stable -y
    PATH="/root/.cargo/bin:${PATH}"
    ```
    After the above commands, please restart a new session of terminal (close the old window) for the path settings to take effect. Again, perform the step 2 to successfully install all the libraries.
4. After a while, once all the nodes are synced up, launch a new seperate instance of the terminal, independent of the above tmux sessions. Run the following commands to get the data from the required node and sensor:
    ```
    source venv/bin/activate
    python3 actuator.py r1/temperature
    ```
    where, 
    - r1 -> name of the node to get the data from, can be changed to r2, r3, r4
    - temperature -> sensor data information to get. Choose from the following options: temperature, humidity, cec, compaction, nutrition, pH, salinity, pesticides
5. To run the code on different RPis, please run the following command
    ```
    ./start_system.sh
    ```
    The script automates the process of SSH login to four different Pis and executes the commands ./shell.sh 1, ./shell.sh 2, ./shell.sh 3, and ./shell.sh 4 on each respective Pi. Following this, it executes ./shell.sh 0 on the local Pi. It's important to note that for the script to run successfully, passwordless SSH access to the other four Pis must be set up from the local Pi. This involves transferring the local Pi's public key to the other four Pis, a task already completed on the Pi with the address rasp-008.berry.scss.tcd.ie.
    After a while, once all the nodes are synced up, launch a new seperate instance of the terminal. Run the following commands to get the data from the required node and sensor:
    ```
    python3 actuator.py r1/temperature
    ```
    r1 can be changed to r2, r3, r4
    temperature can be changed to humidity, cec, compaction, nutrition, pH, salinity, pesticides
6. To terminate a node's process, use the command
    ```
    ./terminate.sh
    ```
    To terminate all the nodes' processes, use the command
    ```
    ./terminate_system.sh
    ```
7. [OPTIONAL] If the command ./start_system.sh fails, to run the code on different RPis, please run the following command/shell script by passing the appropriate node number:
    ```
    ./shell.sh 0
    ```
    This starts the node 0 in the RPi it is run on. For node 1 do '`./shell.sh 1`' and so on for the other nodes.
