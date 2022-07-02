import socket
import time
import os
import sys, getopt
import struct
import yaml
from yaml.loader import FullLoader

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "localhost"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# time = struct.pack(str("ll"), int(2), int(0))
# client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, time)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    # send_length = str(msg_length).encode(FORMAT) 
    # send_length += b' ' * (HEADER - len(send_length)) 
    # client.send(send_length)
    client.send(message)
    try:
        recv_msg = client.recv(2048).decode(FORMAT)
    except Exception as excep:
        print(excep)

    if(recv_msg == ''):
        print(f'READING (0) bytes:')
    # if(recv_msg == '\x00'):
    #     print(f"READING (0) bytes: ")
    else:
        print(f"READING ({len(recv_msg)}) bytes: \n{recv_msg}")
    #print(recv_msg)


def main():
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:p:",["ipaddr=","port="])
    except getopt.GetoptError:
        print(f'{sys.argv[0]} -i <IP Address/hostname> -p <Port Number>')
        sys.exit()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(f'{sys.argv[0]} -i <IP Address/hostname> -p <Port Number>')
            sys.exit()
        elif opt in ("-i", "--ipaddr"):
            print(f"IP Address/Hostname: {arg}")
            global SERVER
            SERVER = arg
        elif opt in ("-p", "--port"):
            print(f"Port: {arg}")
            global PORT
            PORT = arg

    '''
    with open('config.yaml', 'r') as f:
        doc = yaml.load(f,Loader=FullLoader)

    global SERVER
    SERVER = doc['IP_ADDR']

    global PORT
    PORT = doc['PORT']

    
    while True:
        data = input()
        if data.lower() == 'q':
            client.close()
            break
        print(f"WRITING ({len(data)}) bytes: \n{data}")
        send(data)
    
    '''
    with open('../samples/query-addr-A.txt') as sendqry:
        for line in sendqry:
            data = line.rstrip('\n')
            time.sleep(1)
            print(f"WRITING ({len(data)}) bytes: {data}")
            send(data)
    '''

if __name__ == '__main__':
    main()

