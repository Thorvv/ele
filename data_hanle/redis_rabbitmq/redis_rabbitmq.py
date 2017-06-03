import pika
import redis
import MySQLdb


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


class Mysql(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host=HOST, user="xxx", passwd="xxx", db='xxx', charset="utf8")
        self.conn.autocommit(1)
        self.cursor = self.conn.cursor()