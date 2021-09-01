import socket
import threading
import time

from Penetration.MesHandle import UDPTransferProtocol


class ClientUDP(UDPTransferProtocol):
    SERVER_PORT = 20000
    SERVER_IP = "127.0.0.1"

    def __init__(self, server_ip=SERVER_IP, listen_port=SERVER_PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpTransfer = UDPTransferProtocol()
        print(self.socket)

        # self.socket.bind((server_ip, listen_port))

    def send(self, mes, address=None, socket=None):
        if address is None or socket is None:
            # print(id(self.socket))
            super().send(mes, (self.SERVER_IP, self.SERVER_PORT), self.socket)
        else:
            super().send(mes, address, socket)

    def wait(self, socket=None):
        if socket is None:
            return super().wait(self.socket)
        else:
            return super().wait(socket=socket)

    def close(self):
        self.socket.close()

c = ClientUDP()
def send():
    for i in range(100):
        c.send(mes='HHHHHHHHHHHHHHHHH '+str(i)+'...')
threading.Thread(target=send).start()
time.sleep(0.2)
while True:
    print("waiting...\n")
    c.wait()
