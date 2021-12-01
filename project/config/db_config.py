#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  db_config.py  
@Desc :  数据库配置文件
'''

# ********** 数据库配置 ********** #
# redis 数据库
REDIS_CONF = {                  # 生产系统使用
    "HOST": "127.0.0.1",
    "PORT": 6379,
    "AUTH": False,              # AUTH 为 True 时需要进行 用户认证
    "PASSWORD": "xxx",
    "DECODE_RESPONSES": True    # 是否对查询结果进行编码处理
}
REDIS_CONF_T = {                # 测试系统使用
    "HOST": "127.0.0.1",
    "PORT": 6379,
    "AUTH": False,              # AUTH 为 True 时需要进行 用户认证
    "PASSWORD": "xxx",
    "DECODE_RESPONSES": True    # 是否对查询结果进行编码处理
}
