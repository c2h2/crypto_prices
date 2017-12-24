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




redis_enabled = True 
try:
    redis = redis.StrictRedis(host='localhost', port=6379, db=0)
except:
    redis_enabled = False

lookup_table=[["bitx","","" ]]

class Coin:
    def __init__(self, name, mkt):
        self.name=name
        self.mkt=mkt
        self.buys=[]
        self.sells=[]


class Market:
    def __init__(self, name):
        self.name=name
        self.coins={}



class MarketCalculator:
    def __init__(self):
        self.init_mkt()
        self.fetch_redis()


    def init_mkt(self):
        self.mkts = {}
        self.mkts["bitx"]={}
        self.mkts["polo"]={}
        self.mkts["bina"]={}


    def fetch_redis(self):
        old_ts=None
        while True:
            new_data_dict = simplejson.loads(redis.get('mkt_depth'))
            new_ts=new_data_dict['updated_at']

            if old_ts==new_ts:
                pass
            else:
                self.process_new_data(new_data_dict)

            time.sleep(0.02)

    def process_new_data(self, data):
        symbol = "lsk_btc"
        if symbol in self.mkts["bitx"]:
            pass
        else:
            self.mkts["bitx"][symbol]={}
            self.mkts["polo"][symbol]={}
            self.mkts["bina"][symbol]={}

        self.format_bitx(symbol, data)
        self.format_polo(symbol, data)
        self.format_bina(symbol, data)

        #print self.mkts["bina"]


    def format_bitx(self, symbol, data):
        bitx_sell_array = data["bitx"][symbol]['result']['sell']
        sells=[]
        for sell in bitx_sell_array:
            sells.append([sell["Rate"], sell["Quantity"]])

        self.mkts["bitx"][symbol]["sell"]=sells

        bitx_buy_array = data["bitx"][symbol]['result']['buy']
        buys = []
        for buy in bitx_buy_array:
            buys.append([buy["Rate"], buy["Quantity"]])

        self.mkts["bitx"][symbol]["buy"]=buys

    def format_polo(self, symbol, data):
        if "error" in data["polo"][symbol]:
            return

        polo_sell_array = data["polo"][symbol]["asks"]
        sells = []
        for sell in polo_sell_array:
            sells.append([float(sell[0]), sell[1]])

        self.mkts["polo"][symbol]["sell"] = sells

        polo_buy_array = data["polo"][symbol]["bids"]
        buys = []
        for buy in polo_buy_array:
            buys.append([float(buy[0]), float(buy[1])])

        self.mkts["polo"][symbol]["buy"]=buys

    def format_bina(self, symbol, data):
        bina_sell_array = data["bina"][symbol]["asks"]
        sells = []
        for sell in bina_sell_array:
            sells.append([float(sell[0]), sell[1]])

        self.mkts["bina"][symbol]["sell"] = sells

        bina_buy_array = data["bina"][symbol]["bids"]
        buys = []
        for buy in bina_buy_array:
            buys.append([float(buy[0]), float(buy[1])])

        self.mkts["bina"][symbol]["buy"] = buys


def main():
    mc = MarketCalculator()

main()