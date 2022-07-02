## About the Application

This application simulates as a serial interface device and can be used to test your serial interface application. 
<br /> The polling or status commands with their sample reponses can be entered in a text which will be used by the main simulator application to respond to commands sent to it from the NMS or any other application.
<br /> However, for the commands part, you need to create a separate module to handle device specific commands.
<br />_(The application has been developed and tested on a 'Ubunutu 20.04 LTS' system using Python 3 version 3.8.10)_

### The components of the application
#### When you navigate to the simulator directory you will find the following files - 

* config.yaml
    * This file contains the configurable items needed to run the main application.<br />
     The configuration items are :-
    1. `IP_ADDR`: IP Address of the host on which the application is running. Default is `localhost`
    2. `PORT`: The port number on which the application will run. Default is `5050`
    3. `FILENAME`: Here provide the file name that contains the sample query and response as per the device protocol. 
    For example for DoubleD DDA286: 
    The command/query `{AD}_` would get a response `{ADS@3@3@CBCBCB@B@@@@}o` from the device. <br />This type of command/query and response should be added to the file as - <br />
    `QRY: {AD}`<br />
    `RSP: {ADS@3@3@CBCBCB@B@@@@}`
        * _Notice that the last byte which is a checksum byte has been left out. The checksum if any would be calculated by the application._
    4. `STX`, `ETX`, `DEVICE_ADDRESS`, `CHECKSUM_USED` etc are related to the device communication protocol format and may change device to device or manufacturer to manufacturer.
    5. `DEVICE_MODEL` Here provide the name of the module created for handling commands and their responses which are specific to a particular device model. 
    <br />For example here provide the name of the python file doubledda286.py but without the '.py' as `doubledda286` for the DoubleD DA286 device model.
* debugsim.py
    * This is the main application which runs on the parameters configured in the config.yaml file. <br />_The application can be run using the command -_
        ```sh
        python3 debugsim.py
        ```
* client.py
    * This is a sample client application that you can use to test your newly created debug file. This application reads the IP Address and Port number from the config.yaml file. <br >_To run the client, use the following command -_
        ```sh
        python3 client.py
        ```


## Usage

Navigate to the directory where debugsim.py resides and run the following command - 
* python3
    ```sh
    python3 debugsim.py
    ```


## Known issues
- For Model DoubleD DDA286 command `K` for 'Acknowledge Alarms' has not been implemented.
- The `Client` applicaton gets disconnected when it receives zero bytes from the `debugsim` application. You have to restart the application to continue.
<br />*_A workaround is to make sure you send atleast a single byte of data to the client while testing with the Client application._