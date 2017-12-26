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
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Cog, Print



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
    def __init__(self, _screen):
        self.screen = _screen
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

    def order_book_view(self, symbol, _mkts, amt=0):
        if amt!=0:
            self.group_order_book(symbol,_mkts,amt)
            key = symbol+str(amt)
        else:
            key = symbol

        sell_array_lens=[]
        buy_array_lens=[]

        for mkt in _mkts:
            sell_array_lens.append(len(self.mkts[mkt][key]["sell"]))
            buy_array_lens.append( len(self.mkts[mkt][key]["buy"] ))


        sep_line_index=max(sell_array_lens)+1
        self.screen.clear()
        self.screen.print_at("-"*150, 0, sep_line_index) #hoz line
        i=0
        for mkt in _mkts:
            self.screen.print_at(mkt, i*50, 0)
            j=0
            sells = self.mkts[mkt][key]["sell"]
            sells.sort(key=lambda x: float(x[0]), reverse=True)
            offset = max(sell_array_lens)-len(self.mkts[mkt][key]["sell"])
            for sell in sells:
                self.screen.print_at("S " + str(round(sell[0], 8)), i * 50, 1+j + offset,  colour=3) #price
                self.screen.print_at(str(round(sell[1], 8)), i * 50 + 15, 1+j + offset) #amount
                j+=1


            buys = self.mkts[mkt][key]["buy"]
            buys.sort(key=lambda x: float(x[0]), reverse=True)
            j=0
            for buy in buys:
                self.screen.print_at("B " + str(round(buy[0], 8)), i * 50, sep_line_index + j+1, colour=2)  # price
                self.screen.print_at(str(round(buy[1], 8)), i * 50 + 15, sep_line_index + j+1)  # amount
                j += 1

            i += 1

        self.screen.refresh()
        time.sleep(2)



    def group_order_book(self, symbol, _mkts, amt=1): #amt is amount of first coin
        for mkt in _mkts:
            order_book=self.mkts[mkt][symbol]
            self.mkts[mkt][symbol+str(amt)]={}

            self.mkts[mkt][symbol+str(amt)]["sell"]=[]
            self.mkts[mkt][symbol+str(amt)]["buy"]=[]

            vol=0.0
            agg_price=0.0
            for each_sell in order_book["sell"]:
                vol += each_sell[1]
                agg_price += each_sell[0] * each_sell[1]
                if vol<=amt:
                    pass
                else:
                    self.mkts[mkt][symbol + str(amt)]["sell"].append([round(agg_price/vol, 8), round(vol,1)])
                    vol=0.0
                    agg_price=0.0

            vol = 0.0
            agg_price = 0.0
            for each_buy in order_book["buy"]:
                vol += each_buy[1]
                agg_price += each_buy[0] * each_buy[1]
                if vol <= amt:
                    pass
                else:
                    self.mkts[mkt][symbol + str(amt)]["buy"].append([round(agg_price / vol, 8), round(vol, 1)])
                    vol = 0.0
                    agg_price = 0.0



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
        redis.set("mkt_fmt_depth", json.dumps(self.mkts, default=json_util.default))
        self.order_book_view("lsk_btc",["bitx","polo","bina"],100)

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
            sells.append([float(sell[0]), float(sell[1])])

        self.mkts["bina"][symbol]["sell"] = sells

        bina_buy_array = data["bina"][symbol]["bids"]
        buys = []
        for buy in bina_buy_array:
            buys.append([float(buy[0]), float(buy[1])])

        self.mkts["bina"][symbol]["buy"] = buys

def run_screen(screen):
    MarketCalculator(screen)


if __name__ == "__main__":
    Screen.wrapper(run_screen)

