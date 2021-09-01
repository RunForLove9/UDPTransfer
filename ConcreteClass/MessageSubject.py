from Interface.Interface import Subject, IObservers
import json


class MesManager(Subject):

    def __init__(self, mes=[]):
        self.mes = mes
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self):
        for observer in self.observers:
            observer.update()

    # notify the observers when the status is changed
    def change(self, operation, value=None, index=0):
        if operation == "add":
            self.mes.append(value)
        elif operation == "pop":
            if index >= len(self.mes):
                raise UDPTransferException("ReceiveMesManager", "Remove a erorr index...")
            else:
                self.mes.pop(index)
        if len(self.mes) >= 1000:
            jsonstr = json.dumps(self.mes)
            with open(r'./SendMesLog.json', 'a') as f:
                f.write(jsonstr)
            self.mes.clear()

        self.notify()

class FailedMesManager(Subject):

    def __init__(self, mes={}):
        self.mes = mes
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self):
        for observer in self.observers:
            observer.update()

    # notify the observers when the status is changed
    def change(self, operation, mes_id=None, value=None):
        if operation == "add":
            self.mes[mes_id] = value
        elif operation == "pop":
            if mes_id in self.mes.keys():
                self.mes.pop(mes_id)
            else:
                raise UDPTransferException("ReceiveMesManager", "Remove a erorr index...")
        # print(self.mes)
        self.notify()


#　Observer SendMesObserver
class SendMesObserver(IObservers):
    def __init__(self, subject):
        self.subject = subject

    def update(self):
        print("A message is failed send...")
        print(self.subject.mes)

class UDPTransferException(Exception):  # 继承异常类
    def __init__(self, name, reason):
        self.name = name
        self.reason = reason
