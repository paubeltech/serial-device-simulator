import socket
import threading
import time
import os
import sys, getopt
import yaml
from yaml.loader import FullLoader
import struct

HEADER = 1024
PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
FILENAME = '../samples/da-286-addr-A.txt'
STX = None
ETX = None
DEVICE_ADDR = None
CHECKSUM = None
DEV_MODEL = None
device_module = None

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(('',PORT))

def check_and_return_line_in_file(msg,command=False):
    """
    This function returns the corresponding response from the 
    debug file for the query/command sent to the simulator.
    """
    found = False
    if not command:
        msg = device_module.strip_msg_as_per_dbg_file(msg)
    msg = "QRY: {}".format(msg)

    with open(FILENAME) as search:
        for line in search:
            line = line.rstrip('\n')  # remove '\n' at end of line
            if found == True:
                if 'RSP: ' in line:
                    line = line.replace('RSP: ', '')
                    # print(f'line: {line}')
                    return line
                else:
                    if command: return line
                    print(f"WRITING ({len('0')}) bytes: \n{''}")
                    return '\x00'.encode(FORMAT)
            if msg == line:
                found = True

    return ''


def replace_rsp_in_file(act_rsp, new_rsp):
    """
    This function replaces any response in the file with 
    the new response.
    """
    # Read in the file
    with open(FILENAME, 'r') as file :
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace(act_rsp, new_rsp)

    # Write the file out again
    with open(FILENAME, 'w') as file:
        file.write(filedata)

def handle_client(conn, addr):
    """
    This function handles all the client connections.
    """
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        try:
            msg = conn.recv(HEADER).decode(FORMAT)
            if len(msg) <= 0:
                break
        except ConnectionResetError:
            print('Connection reset by peer')
            connected = False
            conn.close()
        except:
            print('Disconnected from client')
            connected = False
            conn.close()

        if msg == DISCONNECT_MESSAGE:
            connected = False

        print(f"READING ({len(msg)}) bytes: \n{msg}")
        
        new_msg = check_and_return_line_in_file(msg)

        if(new_msg == ''):            
            new_msg = device_module.get_rsp_for_cmd(msg)

        new_msg = device_module.build_return_packet(new_msg)

        print(f"WRITING ({len(new_msg)}) bytes: \n{new_msg}")
        try:
            conn.send(new_msg.encode(FORMAT))
        except BrokenPipeError:
            print('Connection broken')
            connected = False
        except Exception as excep:
            print(excep)
            connected = False

    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] Simulator is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        # conn.settimeout(5.0)
        # conn.setblocking(0)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() -1}")


def set_gobal_params():
    """
    Reads the configuration yaml file and sets them to the 
    Global variables.
    """
    with open('config.yaml', 'r') as f:
            doc = yaml.load(f,Loader=FullLoader)

    global SERVER
    SERVER = doc['IP_ADDR']

    global PORT
    PORT = doc['PORT']

    global FILENAME
    FILENAME = doc['FILENAME']

    global STX
    STX = doc['STX']

    global ETX
    ETX = doc['ETX']

    global DEVICE_ADDR
    DEVICE_ADDR = doc['DEVICE_ADDR']

    global CHECKSUM
    CHECKSUM = doc['CHECKSUM_USED']

    global DEV_MODEL
    DEV_MODEL = doc['DEV_MODEL']

    global device_module
    try:
        device_module = __import__(DEV_MODEL)
    except ModuleNotFoundError as excp:
        print(excp)
        sys.exit()


def main():
    set_gobal_params()
    
    # Sets Global parameters in the relevant module.
    device_module.set_protocol_packet_vars(STX, ETX, DEVICE_ADDR, CHECKSUM)

    print("[STARTING] Simulator is starting...")
    print(f"IP Address/Hostname: {SERVER}")
    print(f"Port: {PORT}")
    print(f"Filename: {FILENAME}")
    print(f"Stx: {STX}, Dev Addr: {DEVICE_ADDR}, Etx: {ETX} \
            Checksum: {CHECKSUM}")
    print(f"Device Model: {DEV_MODEL}")
    start()


if __name__ == '__main__':
    main()
