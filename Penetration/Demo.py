import time
from threading import Thread

from Penetration.MesHandle import MesHandle
from Penetration.Server import ServerUDP



if __name__ == '__main__':
    server = ServerUDP()
    # mesHandle = MesHandle()
    print('Server waiting...')
    while True:
        task, back_ack, mes, address, data = server.wait()

