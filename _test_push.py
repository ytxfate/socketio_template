#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@File :  test_push.py  
@Desc :  
'''

# Standard library imports
from string import ascii_letters
import random
import time
import json
# Third party imports
import redis
# Local application imports

# redis_cli = redis.Redis("test-redis-for-socketio", 6379, decode_responses=True) # use docker-compose links
redis_cli = redis.Redis("127.0.0.1", 6379, decode_responses=True)

# chans = ['test_1','test_2','test_3','test_4','test_5']
chans = ['01','02','03','04','05']
while 1:
    # chan = "ceshi-test" + random.sample(chans, 1)[0]
    chan = "ceshi_room" + random.sample(chans, 1)[0]
    # chan = "ceshi_room01"
    msg = "".join(random.sample(list(ascii_letters), 10))
    send_dict = {"data": msg, "uid": chan.replace("_room", "")}
    redis_cli.publish(chan, json.dumps(send_dict, ensure_ascii=True))
    print(chan, send_dict)
    time.sleep(0.2)
