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

__REDIS_KEY_PREFIX = "socketio_server_v1.0"
# socketio uid and room name mapping hash
PROID_REDCHAN_MAPPING = f"{__REDIS_KEY_PREFIX}:proid_redchan_mapping.hash"
"""项目ID 与 订阅的 redis channel 的集合  
例：  
key             | value  
project_name_1  | ["chan_1", "chan_2"]  
project_name_2  | chan_3  
"""
