#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  main.py  
@Desc :  启动文件
'''

# Standard library imports
import json
# Third party imports
import eventlet
import redis
import socketio
from loguru import logger
# Local application imports

__REDIS_KEY_PREFIX = "ceshi"
# socketio uid and room name mapping hash
SIO_UID_ROOM_HASH = f"{__REDIS_KEY_PREFIX}:uid_room_mapping.hash"
PSUB_CHANNEL = f"{__REDIS_KEY_PREFIX}-test*"

eventlet.monkey_patch()

# 本次测试推送 redis 订阅信息
# redis_cli = redis.Redis("test-redis-for-socketio", 6379, decode_responses=True) # use docker-compose links
redis_cli = redis.Redis("127.0.0.1", 6379, decode_responses=True)

sio = socketio.Server(async_mode='eventlet',
                      cors_allowed_origins="*",
                      logger=logger,
                      )
app = socketio.WSGIApp(sio,
                       static_files={'/': {'content_type': 'text/html',
                                           'filename': 'web/templates/index.html'},
                                     '/static': 'web/static'
                                     }
                       )


@sio.event
def connect(sid, environ):
    logger.info(f'connect : {sid}')

@sio.on("login")
def login(sid, data):
    """登录"""
    # 检验用户
    room_name = redis_cli.hget(SIO_UID_ROOM_HASH, data)
    if room_name is None:
        sio.disconnect(sid=sid)
        logger.info(f'room name get error, disconnect : {sid}')
    else:
        sio.enter_room(sid, room_name)
        logger.info(f'{sid} join room [{room_name}]')


@sio.event
def disconnect(sid):    
    room_names = sio.rooms(sid)
    for room_name in room_names:
        sio.leave_room(sid, room_name)
    logger.info(f'disconnect : {sid}, leave rooms {room_names}')


def back_task():
    """后台任务实例
    """
    pub = redis_cli.pubsub()
    pub.psubscribe(PSUB_CHANNEL)
    for p_res in pub.listen():
        # 判断消息类型
        if p_res.get("type") != 'pmessage':
            sio.sleep()
            continue
        # 判断数据格式是否正确
        res_data = p_res.get("data", "")
        try:
            res_data = json.loads(res_data, encoding='utf-8')
        except Exception as e:
            logger.exception(e)
            logger.error(res_data)
            sio.sleep()
            continue
        # 判断接收到的字符串是否为字典
        if not isinstance(res_data, dict):
            logger.warning(f'redis subscribe info is not dict: {res_data}')
            sio.sleep()
            continue
        # 判断必要字段是否存在
        if "uid" not in res_data or "data" not in res_data:
            logger.warning(f'Important fields[uid, data] are missing: {res_data}')
            sio.sleep()
            continue
        # 判断 room name 是否存在
        room_name = redis_cli.hget(SIO_UID_ROOM_HASH, res_data['uid'])
        if room_name is None:
            logger.warning(f'mismatch room name: {res_data}')
            sio.sleep()
            continue
        # 判断 room 是否无人
        room_users = sio.manager.rooms.get("/", {}).get(room_name, {})
        if len(room_users) <= 0:
            logger.info(f"room [{room_name}] has no client, skip...")
            sio.sleep() # 必加
            continue
        # 推送数据
        logger.debug(f"room [{room_name}] push msg: {res_data['data']}")
        sio.emit("server_response", res_data['data'], room=room_name)


if __name__ == '__main__':
    sio.start_background_task(back_task)
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
