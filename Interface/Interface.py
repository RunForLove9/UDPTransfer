from abc import abstractmethod

# Subject interface
class Subject(object):
    def __init__(self):
        self.observers = []
        self.status = -1

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self):
        for observer in self.observers:
            observer.update()

    # notify the observers when the status is changed
    def change(self, status):
        self.status = status
        self.notify()


#　Observer interface
class IObservers(object):
    def __init__(self, subject):
        self.subject = subject
        pass

    def update(self):
        pass