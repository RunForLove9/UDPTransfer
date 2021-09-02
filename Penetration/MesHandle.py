import _thread
import random
import threading
import time
from copy import deepcopy

from ConcreteClass.MessageSubject import MesManager, FailedMesManager


class MesHandle(object):
    tasks = []


class UDPTransferProtocol(object):
    mes_queue = {}  # 发送消息队列
    receive_mes_queue = {}  # 接受消息队列
    mutex = threading.Lock()
    REPEAT_TIME = 0.5
    SEND_FAILED_TIME = 2.0
    receive_mes_manager = MesManager()
    send_mes_manager = MesManager()
    failed_mes_manager = FailedMesManager()
    '''
    通信协议：为了保证数据的正常传输，我们需要模仿TCP协议，从应用层实现差错检测、超时重传等功能。
    所有消息均先通过编码后发送，接收时解码。
    传输格式为：int_str1_str2
    int 指不同的任务编号，-1值信息收到确认回复
    str1 指想要收到的确认码
    str2 正常消息内容
    '''

    def send(self, mes, address, socket, mes_id=0):
        thread = threading.Thread(target=self.send_help, args=(mes, address, socket, 1, mes_id))
        thread.start()
        # 如果没有收到回执，则重发消息，时间

    def send_help(self, mes, address, socket, task=1, mes_id=0, is_byte=2, mes_type=1):
        if isinstance(mes, int):
            mes = str(mes)
            mes_type = 1
            is_byte = 2
        if isinstance(mes, bytes) or isinstance(mes_type, bytearray):
            is_byte = 1
        b_mes, ack = self.encoder(mes, task=task, is_byte=is_byte, mes_type=mes_type)
        # print('\n\t'+str(task)+' : send a mes to ', address, ' : ', b_mes)
        socket.sendto(b_mes, address)
        start_time = time.time()
        self.mutex.acquire()  # 上锁
        self.mes_queue[ack] = (socket, address, ack, b_mes)
        self.mutex.release()  # 解锁
        while True:
            time.sleep(self.REPEAT_TIME)
            # 如果消确认消息中没有此ack，代表已经收到。
            if ack not in self.mes_queue.keys():
                send_mark = True
                break
            # 否则进入重发
            keep_time = time.time() - start_time
            if keep_time < self.SEND_FAILED_TIME:
                socket.sendto(b_mes, address)
                # print('\n\twe repaet to send a mes to ', address, ' : ', b_mes)
                self.mutex.acquire()  # 上锁
                self.mes_queue[ack] = (socket, address, ack, b_mes)
                self.mutex.release()  # 解锁
            else:
                send_mark = False
                self.failed_mes_manager.change(operation="add", mes_id=mes_id, value=(mes, address))
                print("We can't connect with server, please check your network......................")
                self.mutex.acquire()  # 上锁
                self.mes_queue.pop(ack)
                self.mutex.release()  # 释放
                break
        if send_mark is True and task == 1:
            self.send_mes_manager.change(operation="add", value=(1, mes_id, mes, address))
            print("send a mes : ", mes)
        elif send_mark is False and task == 1:
            self.send_mes_manager.change(operation="add", value=(2, mes_id, mes, address))
            print("failed send a mes : ", mes)
        return send_mark

    def sendAck(self, ack, address, socket, task=2, mes_id=0, is_byte=2, mes_type=1):
        task = 2
        ack = ack
        mes = ack
        # mess = ".".join([str(task), str(ack), mes])
        # b_mes = mess.encode('utf-8')
        thread = threading.Thread(target=self.send_help, args=(mes, address, socket, task, mes_id, is_byte, mes_type))
        thread.start()

    def sendAck2Ack(self, ack, address, socket, task=3, mes_id=0, is_byte=2, mes_type=1):
        task = 3
        ack = ack
        mes = str(ack)
        b_mes = bytearray()
        task = task.to_bytes(4, 'big')
        b_mes.extend(task)
        b_mes.extend(ack.to_bytes(8, 'big'))
        b_mes.extend(is_byte.to_bytes(2, 'big'))
        b_mes.extend(mes_type.to_bytes(2, 'big'))
        b_mes.extend(len(mes).to_bytes(4, 'big'))
        b_mes.extend(mes.encode('utf-8'))
        b_mes = bytes(b_mes)
        socket.sendto(b_mes, address)

    def encoder(self, mes, task, is_byte=2, mes_type=1):
        """
        对发送的消息进行编码处理
        :param mes: 要发送的消息实体 -> 可能是 str， 也有可能是 bytes
        :param task: UDP包标志，1 为正常消息， -1 为ack确认包， -2 为确认ack的确认包
        :return: 返回编码好的字节码数组， 与其对应的ack识别码
        """
        if is_byte == 1:
            barray = bytearray()
            barray.extend(mes)
            barray.extend(str(random.randint(0, 10000)).encode('utf-8'))
            barray = bytes(barray)
            ack = abs(hash(barray))  # int 正数
        elif is_byte == 2:
            ack = abs(hash(mes + str(str(random.randint(0, 10000)))))
            mes = mes.encode('utf-8')
        b_mes = bytearray()
        task = task.to_bytes(4, 'big')
        b_mes.extend(task)
        ack = ack.to_bytes(8, 'big')
        b_mes.extend(ack)
        is_byte = is_byte.to_bytes(2, 'big')
        b_mes.extend(is_byte)
        mes_type = mes_type.to_bytes(2, 'big')
        b_mes.extend(mes_type)
        mes_length = len(mes_type)
        mes_length = mes_length.to_bytes(4, 'big')
        b_mes.extend(mes_length)
        b_mes.extend(mes)
        b_mes = bytes(b_mes)
        return_ack = int.from_bytes(ack, 'big')
        return b_mes, return_ack

    def decode(self, b_mes):
        mes_bytes = bytearray(b_mes)
        task = int.from_bytes(mes_bytes[:4], 'big')
        ack = int.from_bytes(mes_bytes[4:12], 'big')
        is_byte = int.from_bytes(mes_bytes[12:14], 'big')
        mes_type = int.from_bytes(mes_bytes[14:16], 'big')
        mes_length = int.from_bytes(mes_bytes[16:20], 'big')
        mes = mes_bytes[20:]
        if is_byte == 2:
            mes = mes.decode('utf-8')
        return task, ack, is_byte, mes_type, mes_length, mes

    def wait(self, socket):
        try:
            data, back_address = socket.recvfrom(1024*1024)
        except:
            # print("We can't connect with server, please check your network...")
            return
        task, back_ack, is_byte, mes_type, mes_length, mes = self.decode(data)
        # print('receive a mes -> ', mes,'  with ack ', back_ack)
        if task == 2:
            mes = int(mes)
            if mes in self.mes_queue.keys():
                socket, address, ack, b_mes = self.mes_queue[mes]
                if hash(back_address) != hash(address):
                    raise UDPTransferException("ACK", "Ack not matched...")
                self.mutex.acquire()  # 上锁
                self.mes_queue.pop(mes)
                self.mutex.release()  # 释放
                self.sendAck2Ack(back_ack, address, socket)
        elif task == 3:  # 确认收到，则可以将确认消息从确认队列移除
            mes = int(mes)
            if mes in self.mes_queue.keys():
                # print("there is task -2")
                socket, address, ack, b_mes = self.mes_queue[mes]
                task, back_ack, is_byte, mes_type, mes_length, mes = self.decode(b_mes)
                original_mes_ack = int(mes)
                if original_mes_ack in list(self.receive_mes_queue.keys()):
                    is_received, mes_info, address_from, _ = self.receive_mes_queue[original_mes_ack]
                    self.receive_mes_manager.change(operation="add", value=(mes_info, address_from))
                    print('Receive a mes from ', address_from, ' -> ', mes_info)
                    self.mutex.acquire()  # 上锁
                    self.receive_mes_queue.pop(original_mes_ack)
                    self.mutex.release()  # 释放
                if hash(back_address) != hash(address):
                    raise UDPTransferException("ACK", "Ack not matched...")
                self.mutex.acquire()  # 上锁
                self.mes_queue.pop(ack)
                self.mutex.release()  # 释放
        else:
            if back_ack in self.mes_queue.keys():
                pass
            else:
                self.receive_mes_queue[back_ack] = (-1, mes, back_address, socket)
                threading.Thread(self.sendAck(back_ack, back_address, socket)).start()
        return task, back_ack, mes, back_address, data


class UDPTransferException(Exception):  # 继承异常类
    def __init__(self, name, reason):
        self.name = name
        self.reason = reason
