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

#python2

redis_enabled = True

polo = Poloniex()
#pip install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.6.zip

DFT_SLEEP_TIME=0.2
DFT_HTTP_CONN_TIME=10
real_mkts_raw_data={}
mkt_depth={}

##add timeout class
class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

##init redis
try:
    redis = redis.StrictRedis(host='localhost', port=6379, db=0)
    redis["real_mkts_raw_data"]={}
    redis["mkt_depth"]={}
except:
    redis_enabled = False

class CryptoDepthPrice:
    def __init__(self):
        mkt_depth["bitx_lsk"]={}
        mkt_depth["polo_lsk"]={}
        mkt_depth["bina_lsk"]={}
        mkt_depth["created_at"] = datetime.now()
        mkt_depth["updated_at"] = datetime.now()

    def update_ts(self):
        mkt_depth["updated_at"] = datetime.now()
        if (redis_enabled):
            redis.set("mkt_depth", json.dumps(mkt_depth, default=json_util.default))

    def get_polo_lsk(self):
        url = 'https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_LSK&depth=100'
        http = requests.Session()
        while (True):
            try:
                # with timeout(seconds=DFT_HTTP_CONN_TIME):
                data = simplejson.loads(http.get(url, timeout=DFT_HTTP_CONN_TIME).content)
                mkt_depth["polo_lsk"] = data
                mkt_depth["polo_lsk"]["created_at"] = datetime.now()
                self.update_ts()
                time.sleep(DFT_SLEEP_TIME)
            except Exception, e:
                print str(e)

    def get_bitx_lsk(self):
        url = 'https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-LSK&type=both'
        http = requests.Session()
        while (True):
            try:
                # with timeout(seconds=DFT_HTTP_CONN_TIME):
                data = simplejson.loads(http.get(url, timeout=DFT_HTTP_CONN_TIME).content)
                mkt_depth["bitx_lsk"] = data
                mkt_depth["bitx_lsk"]["created_at"] = datetime.now()
                self.update_ts()
                time.sleep(DFT_SLEEP_TIME)
            except Exception, e:
                print str(e)


    def multithread_update_prices(self, threads):
        #threads.append(threading.Thread(target=self.get_jubi))
        #threads.append(threading.Thread(target=self.get_okcoin))
        threads.append(threading.Thread(target=self.get_bitx_lsk))
        #threads.append(threading.Thread(target=self.get_acx))
        threads.append(threading.Thread(target=self.get_polo_lsk))
        #threads.append(threading.Thread(target=self.get_bitfinex))
        #threads.append(threading.Thread(target=self.get_bithumb))
        #threads.append(threading.Thread(target=self.get_binance))
        #threads.append(threading.Thread(target=self.print_mkt))


class CryptoTickerPrice:
    def __init__(self):
        #real_mkts_raw_data["jubi"] = {}
        #real_mkts_raw_data["okcn"] = {}
        real_mkts_raw_data["bitx"] = {}
        real_mkts_raw_data["polo"] = {}
        real_mkts_raw_data["bitf"] = {}
        real_mkts_raw_data["bith"] = {}
        real_mkts_raw_data["bina"] = {}
        real_mkts_raw_data["created_at"] = datetime.now()
        real_mkts_raw_data["updated_at"] = datetime.now()
        pass

    def update_ts(self):
        real_mkts_raw_data["updated_at"] = datetime.now()
        if(redis_enabled):
            redis["real_mkts_raw_data"]=real_mkts_raw_data

    def get_jubi(self):
        url='http://www.jubi.com/api/v1/allticker/'
        http=requests.Session()
        while(True):
            try:
                #with timeout(seconds=DFT_HTTP_CONN_TIME):
                data = simplejson.loads(http.get(url,timeout=DFT_HTTP_CONN_TIME).content)
                real_mkts_raw_data["jubi"]=data
                real_mkts_raw_data["jubi"]["created_at"]=datetime.now()
                update_ts()
                time.sleep(DFT_SLEEP_TIME)
            except Exception, e:
                print str(e)


    def get_bittrex(self):
        url0='https://bittrex.com/api/v1.1/public/getmarketsummary?market=btc-lsk'
        url1='https://bittrex.com/api/v1.1/public/getmarketsummary?market=usdt-btc'
        url2='https://bittrex.com/api/v1.1/public/getmarketsummary?market=usdt-eth'
        http = requests.Session()
        while (True):
            try:
                real_mkts_raw_data["bitx"]["btc_lsk"] = simplejson.loads(http.get(url0,timeout=DFT_HTTP_CONN_TIME).content)
                real_mkts_raw_data["bitx"]["btc_usdt"] = simplejson.loads(http.get(url1,timeout=DFT_HTTP_CONN_TIME).content)
                real_mkts_raw_data["bitx"]["eth_usdt"] = simplejson.loads(http.get(url2,timeout=DFT_HTTP_CONN_TIME).content)
                real_mkts_raw_data["bitx"]["created_at"] = datetime.now()
                self.update_ts()
                time.sleep(DFT_SLEEP_TIME)
            except Exception, e:
                print str(e)

    def get_okcoin(self):
        url0 = 'https://www.okcoin.cn/api/v1/ticker.do?symbol=btc_cny'
        url1 = 'https://www.okcoin.cn/api/v1/ticker.do?symbol=eth_cny'
        url2 = 'https://www.okcoin.cn/api/v1/ticker.do?symbol=etc_cny'
        http = requests.Session()
        while (True):
            try:
                real_mkts_raw_data["okcn"]["btc_cny"] = simplejson.loads(http.get(url0,timeout=DFT_HTTP_CONN_TIME).content)
                real_mkts_raw_data["okcn"]["eth_cny"] = simplejson.loads(http.get(url1,timeout=DFT_HTTP_CONN_TIME).content)
                real_mkts_raw_data["okcn"]["etc_cny"] = simplejson.loads(http.get(url2,timeout=DFT_HTTP_CONN_TIME).content)
                real_mkts_raw_data["okcn"]["created_at"] = datetime.now()
                self.update_ts()
                time.sleep(DFT_SLEEP_TIME)
            except Exception, e:
                print str(e)

    def get_acx(self):
        url0 = 'https://acx.io/api/v2/tickers.json'
        http = requests.Session()
        while (True):
            try:
                real_mkts_raw_data["acxi"] = simplejson.loads(http.get(url0,timeout=DFT_HTTP_CONN_TIME).content)
                real_mkts_raw_data["acxi"]["created_at"] = datetime.now()
                self.update_ts()
                time.sleep(DFT_SLEEP_TIME)
            except Exception, e:
                print str(e)


    def get_bitfinex(self):
        url0 = 'https://api.bitfinex.com/v1/pubticker/btcusd'
        url1 = 'https://api.bitfinex.com/v1/pubticker/ethusd'
        http = requests.Session()
        while (True):
            try:
                real_mkts_raw_data["bitf"]["btc_usd"] = simplejson.loads(http.get(url0,timeout=DFT_HTTP_CONN_TIME).content)
                real_mkts_raw_data["bitf"]["eth_usd"] =  simplejson.loads(http.get(url1,timeout=DFT_HTTP_CONN_TIME).content)
                real_mkts_raw_data["bitf"]["created_at"] = datetime.now()
                self.update_ts()
                time.sleep(DFT_SLEEP_TIME+1)
            except Exception, e:
                print str(e)


    def get_polo(self):
        while (True):
            try:
                real_mkts_raw_data["polo"] = polo.returnTicker()
                real_mkts_raw_data["polo"]["created_at"] = datetime.now()
                self.update_ts()
                time.sleep(DFT_SLEEP_TIME)
            except Exception, e:
                print str(e)

    def get_bithumb(self):
        url0 = 'https://api.bithumb.com/public/ticker/ALL'
        http = requests.Session()
        while (True):
            try:
                real_mkts_raw_data["bith"] = simplejson.loads(http.get(url0,timeout=DFT_HTTP_CONN_TIME).content)
                real_mkts_raw_data["bith"]["created_at"] = datetime.now()
                self.update_ts()
                time.sleep(DFT_SLEEP_TIME)
            except Exception, e:
                print str(e)

    def get_binance(self):
        url0= 'https://api.binance.com/api/v1/ticker/allPrices'
        url1= 'https://api.binance.com/api/v1/ticker/24hr?symbol=LSKBTC'
        http = requests.Session()
        while (True):
            try:
                temp_data_array = simplejson.loads(http.get(url0,timeout=DFT_HTTP_CONN_TIME).content)
                temp_hash = {}
                i=0
                for i in range(len(temp_data_array)):
                    temp_hash[temp_data_array[i]["symbol"]]=temp_data_array[i]["price"]

                lsk_vol = simplejson.loads(http.get(url1,timeout=DFT_HTTP_CONN_TIME).content)
                real_mkts_raw_data["bina"] = temp_hash
                real_mkts_raw_data["bina"]["LSKBTC_VOL"] = lsk_vol
                real_mkts_raw_data["bina"]["created_at"] = datetime.now()
                self.update_ts()
                time.sleep(DFT_SLEEP_TIME)
            except Exception as e:
               exc_type, exc_obj, exc_tb = sys.exc_info()
               fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
               print(exc_type, fname, exc_tb.tb_lineno)
        


    def process_raw_data(self):
        pass

    def output_txt(self):
        pass

    def print_mkt(self):
        while(True):
            #print str(real_mkts_raw_data)
            f=open('../prices_json.txt', 'w')
            f.write(json.dumps(real_mkts_raw_data, default=json_util.default))
            f.close()
            time.sleep(1)

    def multithread_update_prices(self, threads):
        #threads.append(threading.Thread(target=self.get_jubi))
        #threads.append(threading.Thread(target=self.get_okcoin))
        threads.append(threading.Thread(target=self.get_bittrex))
        threads.append(threading.Thread(target=self.get_acx))
        threads.append(threading.Thread(target=self.get_polo))
        threads.append(threading.Thread(target=self.get_bitfinex))
        threads.append(threading.Thread(target=self.get_bithumb))
        threads.append(threading.Thread(target=self.get_binance))
        threads.append(threading.Thread(target=self.print_mkt))



#db.generate_mapping(create_tables=True)
def main():
    threads=[]

    ctp=CryptoTickerPrice()
    ctp.multithread_update_prices(threads)

    cdp=CryptoDepthPrice()
    cdp.multithread_update_prices(threads)

    for t in threads:
        t.daemon = True
        t.start()

    # keep main thread live
    while True:
        time.sleep(1)

    for t in threads:
        t.join()



main()
