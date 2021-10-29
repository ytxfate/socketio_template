#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  main.py  
@Desc :  启动文件
'''

# Standard library imports

# Third party imports
import eventlet
import redis
import socketio
from loguru import logger
# Local application imports
from conf.socketio_conf import SIO_NAMESPACE, SIO_ROOM_NAME

eventlet.monkey_patch()

# 本次测试推送 redis 订阅信息
redis_cli = redis.Redis("127.0.0.1", 6379, decode_responses=True)

sio = socketio.Server(async_mode='eventlet',
                      cors_allowed_origins="*",
                      logger=logger,
                      )
app = socketio.WSGIApp(sio,
                       static_files={'/': {'content_type': 'text/html',
                                           'filename': 'templates/index.html'}
                                     }
                       )


@sio.event
def connect(sid, environ):
    logger.info(f'connect : {sid}, join [{SIO_NAMESPACE}] room [{SIO_ROOM_NAME}]')
    sio.enter_room(sid, SIO_ROOM_NAME, namespace=SIO_NAMESPACE)

@sio.event
def my_message(sid, data):
    logger.info('message ', data)

@sio.event
def disconnect(sid):
    logger.info(f'disconnect : {sid}, leave [{SIO_NAMESPACE}] room [{SIO_ROOM_NAME}]')
    sio.leave_room(sid, SIO_ROOM_NAME, namespace=SIO_NAMESPACE)

def back_task():
    """后台任务实例
    """
    pub = redis_cli.pubsub()
    pub.subscribe("test")
    for p in pub.listen():
        users = sio.manager.rooms.get(SIO_NAMESPACE, {}).get(SIO_ROOM_NAME, {})
        user_size = len(users)
        if user_size > 0:
            logger.debug(f"push msg: {p}")
            sio.emit("server_response", p['data'], room=SIO_ROOM_NAME, namespace=SIO_NAMESPACE)
        else:
            logger.info("room has no client, skip...")
        sio.sleep() # 必加


if __name__ == '__main__':
    logger.info(f'Default NAMESPACE: {SIO_NAMESPACE}, Default Room Name: {SIO_ROOM_NAME}')
    sio.start_background_task(back_task)
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
