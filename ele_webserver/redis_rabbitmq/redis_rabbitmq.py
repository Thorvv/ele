import pika
import redis


HOST = "127.0.0.1"
PORT = "6379"


class RabbitMq(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()


class MyRedis(object):
    def __init__(self):

        self.pool = redis.ConnectionPool(host=HOST, port=PORT, db=0)
        self.redis = redis.Redis(connection_pool=self.pool)