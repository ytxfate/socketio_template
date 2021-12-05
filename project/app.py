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
from project.config.sys_config import PROID_REDCHAN_MAPPING


eventlet.monkey_patch()

opt_redis = OperateRedis()


sio = socketio.Server(
    async_mode='eventlet',
    cors_allowed_origins="*",
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
    return

@sio.on("login")
def login(sid, pid):
    """登录"""
    # 获取项目需要订阅的 redis channel
    logger.info(f'redis hash name: {PROID_REDCHAN_MAPPING}')
    redis_cli = opt_redis.get_conn()
    red_chans = redis_cli.hget(PROID_REDCHAN_MAPPING, pid)
    if red_chans is None:   # 未识别的项目id
        sio.disconnect(sid=sid)
        logger.error(f'check project id error, disconnect : {sid}')
        return
    try:
        if red_chans.startswith('[') and red_chans.endswith("]"):
            red_chans = json.loads(red_chans)
            if not isinstance(red_chans, list):
                raise TypeError("chans not list, must be list")
        else:
            red_chans = [red_chans]
    except Exception as e:  # 格式化channel名称失败
        logger.exception(e)
        logger.error(red_chans)
        sio.disconnect(sid=sid)
        logger.error(f'get project sub chans error, disconnect : {sid}')
        return
    # join room
    room_name = f"RN_{pid}"
    before_room_users = sio.manager.rooms.get("/", {}).get(room_name, {})
    sio.enter_room(sid, room_name)  # join room 排在任务开启之前
    if len(before_room_users) <= 0: # room 没人时开启后台推送任务
        sio.start_background_task(back_task,
                                  room_name=room_name,
                                  red_chans=red_chans)
    logger.info(f'{sid} join room [{room_name}]')
    return


@sio.event
def disconnect(sid):
    # 查找这个sid所有join的room
    room_names = sio.rooms(sid)
    for room_name in room_names:
        sio.leave_room(sid, room_name)
    logger.info(f'disconnect : {sid}, leave rooms {room_names}')
    return


def back_task(room_name: str, red_chans: list):
    """后台任务实例
    """
    # 判断 room 是否无人
    room_users = sio.manager.rooms.get("/", {}).get(room_name, {})
    logger.info(f"========== start room: {room_name} ,sub redis channel: {red_chans}")
    if len(room_users) <= 0:
        logger.info(f"room [{room_name}] has no client, stop...")
        sio.sleep() # 必加
        return

    redis_cli = opt_redis.get_conn()
    pub = redis_cli.pubsub()
    pub.subscribe(*red_chans)   # 订阅多个channel
    for p_res in pub.listen():
        # 判断消息类型
        if "message" not in p_res.get("type", ""):
            sio.sleep()
            continue
        # 判断数据格式是否正确
        logger.debug(f'p_res: {p_res}')
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
        # 判断 room 是否无人
        room_users = sio.manager.rooms.get("/", {}).get(room_name, {})
        if len(room_users) <= 0:
            pub.unsubscribe(*red_chans)
            sio.close_room(room=room_name)
            logger.info(f"room [{room_name}] has no client, close...")
            logger.info(f"========== close room: {room_name} ,close sub redis channel: {red_chans}")
            sio.sleep() # 必加
            break
        else:
            # 推送数据
            logger.debug(f"room [{room_name}] push msg: {res_data}")
            sio.emit("server_response", res_data, room=room_name)
    del pub
    logger.info(f'---------- now has sockets: {sio.eio.sockets}, rooms: {sio.manager.rooms}')
    return
