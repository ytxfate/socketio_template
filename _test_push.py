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

redis_cli = redis.Redis("127.0.0.1", 6379, decode_responses=True)

chans = ['test_1','test_2','test_3','test_4','test_5']
while 1:
    chan = "ceshi-test" + random.sample(chans, 1)[0]
    msg = "".join(random.sample(list(ascii_letters), 10))
    redis_cli.publish(chan, json.dumps({"data": msg, "uid": "ceshi01"}, ensure_ascii=True))
    print(chan, msg)
    time.sleep(1)
