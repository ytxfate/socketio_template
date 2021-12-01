#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  sys_config.py  
@Desc :  系统配置
'''

# ********** 生产 与 测试 系统切换 ********** #
# True : 生产系统
# False: 测试系统
isFormalSystem = False

# 基本运行配置
app_run_conf = {
    "HOST": "0.0.0.0",
    "PORT": 5000,
}

__REDIS_KEY_PREFIX = "ceshi"
# socketio uid and room name mapping hash
SIO_UID_ROOM_HASH = f"{__REDIS_KEY_PREFIX}:uid_room_mapping.hash"
PSUB_CHANNEL = f"{__REDIS_KEY_PREFIX}-test*"
