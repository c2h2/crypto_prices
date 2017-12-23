#from crypto_price_db import * #disable db recording.
import requests
import simplejson
import time
import signal
import redis
import json
import sys
import os
from datetime import datetime
from poloniex import Poloniex
import threading
from bson import json_util #need bson and pymongo
#from multiprocessing.pool import ThreadPool
import pickle




redis_enabled = True 
try:
    redis = redis.StrictRedis(host='localhost', port=6379, db=0)
except:
    redis_enabled = False




old_ts=None
while True:
    new_data_dict = simplejson.loads(redis.get('mkt_depth'))
    new_ts=new_data_dict['updated_at']

    if old_ts==new_ts:
        pass
    else:
        print(new_data_dict)

    time.sleep(0.02)

