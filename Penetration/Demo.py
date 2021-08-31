from threading import Thread

from Penetration.MesHandle import MesHandle
from Penetration.Server import ServerUDP



if __name__ == '__main__':
    server = ServerUDP()
    # mesHandle = MesHandle()
    # thread1 = Thread(target=mes_handle())
    print('Server waiting...')
    while True:
        task, back_ack, mes, address = server.wait()
        print("\tServre recive a message from %s -> %s" % (address, mes))

