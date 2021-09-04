
class UDPFileSender(object):
    def __init__(self, sender):
        self.sender = sender


    def readFile2bytes(self, file_name):
        file_bytes = None
        try:
            f = open(file_name, 'rb')
            file_bytes = f.read()
        except IOError:
            print("无法打开文件 -> ", file_name)
        return file_bytes

    def send(self, file_name, address=None):
        pass