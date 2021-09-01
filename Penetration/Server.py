import socket

from Penetration.MesHandle import UDPTransferProtocol


class ServerUDP(UDPTransferProtocol):
    SERVER_PORT = 20000
    SERVER_IP = "127.0.0.1"

    def __init__(self, server_ip=SERVER_IP, listen_port=SERVER_PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((server_ip, listen_port))
        self.data = None
        self.address = None

    def send(self, mes, address=None, socket=None):
        if address is None or socket is None:
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


# s = ServerUDP()
# s.wait()
