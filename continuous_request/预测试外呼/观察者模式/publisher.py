
class NewsPublisher:
    def __init__(self):
        self.__subscriber = dict()
        self.__last_news = None

    def attach(self, subscriber):
        self.__subscriber[id(subscriber)] = subscriber

    def dettach(self, subscriber):
        del self.__subscriber[id(subscriber)]

    def add_news(self, news):
        self.__last_news = news

    def get_news(self):
        return self.__last_news

    def notify(self):
        for _, subscriber in self.__subscriber.items():
            subscriber.update()