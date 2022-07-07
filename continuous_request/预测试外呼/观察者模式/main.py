
from publisher import NewsPublisher
from Subscribers import Subscriber01, Subscriber02, Subscriber03

def main():
    pub = NewsPublisher()
    sub01 = Subscriber01(pub)
    sub02 = Subscriber02(pub)
    sub03 = Subscriber03(pub)
    pub.add_news('It is the news No.1')
    pub.notify()
    print('=' * 100)
    pub.dettach(sub02)
    pub.add_news('It is the news No.2')
    pub.notify()

if __name__ == '__main__':
    main()
