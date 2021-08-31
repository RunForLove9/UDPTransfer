import random


class MesHandle(object):
    tasks = []



class UDPTransferProtocol(object):
    '''
    通信协议：为了保证数据的正常传输，我们需要模仿TCP协议，从应用层实现差错检测、超时重传等功能。
    所有消息均先通过编码后发送，接收时解码。
    传输格式为：int_str1_str2
    int 指不同的任务编号，-1值信息收到确认回复
    str1 指想要收到的确认码
    str2 正常消息内容
    '''
    def send(self, mes, address, socket):
        b_mes, ack = self.encoder(mes, task=1)
        socket.sendto(b_mes, address)
        print('----1----\tSend a mes....')
        self.wait(socket, address=address, ack=ack)

        # 如果没有收到回执，则重发消息，时间



    def sendAck(self, ack, address, socket):
        task = -1
        ack = ack
        mes = "None"
        mess = ".".join([str(task), str(ack), mes])
        b_mes = mess.encode('utf-8')
        print('----0----\tSend a ack....')
        socket.sendto(b_mes, address)

    def encoder(self, mes, task):
        ack = hash(mes + str(random.randint(0, 10000))) # int
        mess = ".".join([str(task), str(ack), mes])
        b_mes = mess.encode('utf-8')
        print('%s hash is -> %s' % (mes, ack))
        return b_mes, ack

    def decode(self, b_mes):
        mes = b_mes.decode('utf-8')
        mess = mes.split('.', 2)
        task = int(mess[0])
        ack = int(mess[1])
        mes = mess[2]
        return task, ack, mes


    def wait(self, socket, address=None, ack=0):
        data, back_address = socket.recvfrom(1024)
        task, back_ack, mes = self.decode(data)
        if task == -1:
            if hash(back_address) != hash(address) or ack != back_ack:
                raise UDPTransferException("ACK", "Ack not matched...")
        else:
            self.sendAck(back_ack, back_address, socket)
        return task, back_ack, mes, back_address


class UDPTransferException(Exception):  # 继承异常类
    def __init__(self, name, reason):
        self.name = name
        self.reason = reason







