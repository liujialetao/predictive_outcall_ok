from abc import ABC, abstractmethod

class Subscriber(ABC):

    @abstractmethod
    def update(self):  #继承ABC的子类，一定要完成update方法
        pass


class Subscriber01(Subscriber):

    def __init__(self, publisher):
        self.publisher = publisher
        publisher.attach(self)

    def update(self):
        print(self.__class__.__name__, ':', self.publisher.get_news())


class Subscriber02(Subscriber):

    def __init__(self, publisher):
        self.publisher = publisher
        publisher.attach(self)

    def update(self):
        print(self.__class__.__name__, ':', self.publisher.get_news())


class Subscriber03(Subscriber):

    def __init__(self, publisher):
        self.publisher = publisher
        publisher.attach(self)

    def update(self):
        print(self.__class__.__name__, ':', self.publisher.get_news())