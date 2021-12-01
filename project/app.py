#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  app.py  
@Desc :  
'''

# Standard library imports
import json
# Third party imports
import eventlet
import socketio
from loguru import logger
# Local application imports
from project.utils.operate_redis import OperateRedis
from project.config.sys_config import SIO_UID_ROOM_HASH


eventlet.monkey_patch()

redis_cli = OperateRedis().get_conn()


sio = socketio.Server(
    async_mode='eventlet',
    cors_allowed_origins="*",
    logger=logger,
)
app = socketio.WSGIApp(
    sio,
    static_files={'/': {'content_type': 'text/html',
                        'filename': 'project/web/templates/index.html'
                        },
                  '/static': 'project/web/static'}
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
        before_room_users = sio.manager.rooms.get("/", {}).get(room_name, {})
        if len(before_room_users) <= 0:
            sio.start_background_task(back_task, room_name=room_name)
        sio.enter_room(sid, room_name)
        logger.info(f'{sid} join room [{room_name}]')


@sio.event
def disconnect(sid):    
    room_names = sio.rooms(sid)
    for room_name in room_names:
        sio.leave_room(sid, room_name)
    logger.info(f'disconnect : {sid}, leave rooms {room_names}')


def back_task(room_name: str):
    """后台任务实例
    """
    pub = redis_cli.pubsub()
    pub.subscribe(room_name)
    for p_res in pub.listen():
        # 判断消息类型
        if p_res.get("type") != 'message':
            sio.sleep()
            continue
        # 判断数据格式是否正确
        res_data = p_res.get("data", "")
        logger.info(f'res_data: {res_data}')
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
            return
        # 判断 room 是否无人
        room_users = sio.manager.rooms.get("/", {}).get(room_name, {})
        if len(room_users) <= 0:
            logger.info(f"room [{room_name}] has no client, skip...")
            sio.sleep() # 必加
            return
        # 推送数据
        logger.debug(f"room [{room_name}] push msg: {res_data['data']}")
        sio.emit("server_response", res_data['data'], room=room_name)

