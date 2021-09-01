import random
import socket
import threading
import time

from ConcreteClass.MessageSubject import SendMesObserver
from Penetration.MesHandle import UDPTransferProtocol


class ClientUDP(UDPTransferProtocol):
    SERVER_PORT = 20000
    SERVER_IP = "127.0.0.1"

    def __init__(self, server_ip=SERVER_IP, listen_port=SERVER_PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpTransfer = UDPTransferProtocol()
        print(self.socket)

        # self.socket.bind((server_ip, listen_port))

    def send(self, mes, mes_id, address=None, socket=None):
        if address is None or socket is None:
            # print(id(self.socket))
            super().send(mes, (self.SERVER_IP, self.SERVER_PORT), self.socket, mes_id)
        else:
            super().send(mes, address, socket, mes_id)

    def wait(self, socket=None):
        if socket is None:
            return super().wait(self.socket)
        else:
            return super().wait(socket=socket)

    def close(self):
        self.socket.close()


c = ClientUDP()
def send():
    c.send(mes='start connect', mes_id=0)
    observer = SendMesObserver(c.failed_mes_manager)
    c.failed_mes_manager.attach(observer)
    while True:
        send_mes = input("You has ")
        if send_mes == "-1":
            print(c.failed_mes_manager.mes)
        elif send_mes == "0":
            print(c.send_mes_manager.mes)
        else:
            c.send(mes=send_mes, mes_id=random.randint(0, 2048))




threading.Thread(target=send).start()

time.sleep(0.1)
while True:
    c.wait()
