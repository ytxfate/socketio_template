#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  main.py  
@Desc :  启动文件
'''

# Standard library imports
# Third party imports
import eventlet
from loguru import logger
# Local application imports
from project.app import app
from project.config.sys_config import app_run_conf


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen((app_run_conf['HOST'], app_run_conf['PORT'])), app)
