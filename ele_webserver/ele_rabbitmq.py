from flask import Flask
from flask import request
from redis_rabbitmq import redis_rabbitmq
import json
import pika
from gevent import monkey
monkey.patch_all()
app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def hello_world():
    if request.method == 'GET':
        userid = request.args.get('userid')
        success_time = request.args.get('success_time')
        ticked_count = request.args.get('ticked_count')
        client_data = {'userid': userid, 'success_time': success_time, 'ticked_count': ticked_count}
        client_data = json.dumps(client_data)

        myrabbitmq.channel.queue_declare(queue='task_queue1', durable=True)
        myrabbitmq.channel.basic_publish(exchange='',
                                         routing_key='task_queue1',
                                         body=client_data,
                                         properties=pika.BasicProperties(
                                             delivery_mode=2,
                                         ))

    return 'send ok'


if __name__ == '__main__':
    myrabbitmq = redis_rabbitmq.RabbitMq()
    app.run()
    myrabbitmq.connection.close()
