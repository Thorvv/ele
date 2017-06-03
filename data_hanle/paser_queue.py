# coding=utf-8
import json
import multiprocessing
import string
from multiprocessing import Pool
from redis_rabbitmq import redis_rabbitmq


def insert_list(change_list, lock):
    while 1:
        if len(change_list) > 2:
            continue
        lock.acquire()
        if len(change_list) == 0:
            change_list.append({'period': 1, 'length': 0})
        else:
            period_list = sorted([cl['period'] for cl in change_list])
            newest_period = period_list[-1]
            change_list.append({'period': newest_period + 1, 'length': 0})
        lock.release()


def get_winner(change_list, n):
    # mysql = redis_rabbitmq.Mysql()
    myredis = redis_rabbitmq.MyRedis()
    while True:
        for cl in change_list:
            if cl['length'] == n:
                print "中奖！！"
                # 生成中奖券号
                winner_tickedid = 123
                myredis.redis.set(cl['period'], winner_tickedid)
                # 插入mysql纪录
                change_list.remove(cl)
                # 发送红包


def callback(ch, method, properties, body):
    get_message = json.loads(body)
    #print get_message

    if len(change_list) != 0:
        myredis = redis_rabbitmq.MyRedis()
        userid = get_message['userid'].encode('utf-8')
        success_time = get_message['success_time'].encode('utf-8')
        ticked_count = get_message['ticked_count'].encode('utf-8')
        ticked_count = string.atoi(ticked_count)
        lock.acquire()
        for period_dict in change_list:
            if period_dict['length'] + ticked_count <= n:
                last_index = period_dict['length'] + 1
                change_list.insert(0, {'period': period_dict['period'],
                                    'length': period_dict['length'] + ticked_count,
                                    })
                change_list.remove(period_dict)
                lock.release()
                print change_list
                try:
                    if ticked_count > 1:
                        for tid in range(ticked_count):
                            ticketid = last_index + tid
                            flag_time = success_time + '_' + str(tid)
                            print ticketid, type(ticketid)
                            myredis.redis.hmset(flag_time, {'period': period_dict['period'],
                                                'userid': userid, 'ticketid': ticketid})
                    else:
                        ticketid = last_index + 1
                        myredis.redis.hmset(success_time, {'period': period_dict['period'],
                                                'userid': userid, 'ticketid': ticketid})
                    # 发送红包
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except:
                    print 'write redis faild!'
                    ch.basic_reject(delivery_tag=method.delivery_tag)
                return
        ch.basic_reject(delivery_tag=method.delivery_tag)
    else:
        ch.basic_reject(delivery_tag=method.delivery_tag)


def client(n, change_list, lock, i):
    myrabbitmq = redis_rabbitmq.RabbitMq()
    myrabbitmq.channel.queue_declare(queue='task_queue1', durable=True)
    myrabbitmq.channel.basic_qos(prefetch_count=1)
    myrabbitmq.channel.basic_consume(callback,
                          queue='task_queue1',
                          no_ack=False
                          )
    myrabbitmq.channel.start_consuming()


if __name__ == '__main__':
    my_manager = multiprocessing.Manager()
    n = 20
    works = []
    lock = my_manager.Lock()
    change_list = my_manager.list()
    my_poor = Pool()
    my_poor.apply_async(insert_list, args=(change_list, lock))
    for i in range(2):
        my_poor.apply_async(client, args=(n, change_list, lock, i))
    my_poor.apply_async(get_winner, args=(change_list, n))
    my_poor.close()
    my_poor.join()

