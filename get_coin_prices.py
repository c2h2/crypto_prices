from crypto_price_db import *
import requests
import simplejson
import time
import signal
import redis
import json
from poloniex import Poloniex
#from multiprocessing.pool import ThreadPool

#python2

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

redis_enabled = False
try:
    redis = redis.StrictRedis(host='localhost', port=6379, db=0)
except:
    redis_enabled = False

polo = Poloniex()
#pip install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.6.zip     

DFT_SLEEP_TIME=0.2
DFT_HTTP_CONN_TIME=10
real_mkts_raw_data={}


class CryptoPrice:
    def __init__(self):
        real_mkts_raw_data["jubi"] = {}
        real_mkts_raw_data["bitx"] = {}
        real_mkts_raw_data["okcn"] = {}
        real_mkts_raw_data["polo"] = {}
        real_mkts_raw_data["bitf"] = {}
        pass

    def get_jubi_price(self):
        url='http://www.jubi.com/api/v1/allticker/'
        http=requests.Session()
        while(True):
            try:
                with timeout(seconds=DFT_HTTP_CONN_TIME):
                    data = simplejson.loads(http.get(url).content)
                    real_mkts_raw_data["jubi"]=data
                    real_mkts_raw_data["jubi"]["created_at"]=datetime.datetime.now()
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
                with timeout(seconds=DFT_HTTP_CONN_TIME):
                    real_mkts_raw_data["bitx"]["btc_lsk"] = simplejson.loads(http.get(url0).content)
                    real_mkts_raw_data["bitx"]["btc_usdt"] = simplejson.loads(http.get(url1).content)
                    real_mkts_raw_data["bitx"]["eth_usdt"] = simplejson.loads(http.get(url2).content)
                    real_mkts_raw_data["bitx"]["created_at"] = datetime.datetime.now()
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
                with timeout(seconds=DFT_HTTP_CONN_TIME):
                    real_mkts_raw_data["okcn"]["btc_cny"] = simplejson.loads(http.get(url0).content)
                    real_mkts_raw_data["okcn"]["eth_cny"] = simplejson.loads(http.get(url1).content)
                    real_mkts_raw_data["okcn"]["etc_cny"] = simplejson.loads(http.get(url2).content)
                    real_mkts_raw_data["okcn"]["created_at"] = datetime.datetime.now()
                    time.sleep(DFT_SLEEP_TIME)
            except Exception, e:
                print str(e)

    def get_acx(self):
        url0 = 'https://acx.io/api/v2/tickers.json'
        http = requests.Session()
        while (True):
            try:
                with timeout(seconds=DFT_HTTP_CONN_TIME):
                    real_mkts_raw_data["acxi"] = simplejson.loads(http.get(url0).content)
                    real_mkts_raw_data["acxi"]["created_at"] = datetime.datetime.now()
                    time.sleep(DFT_SLEEP_TIME)
            except Exception, e:
                print str(e)


    def get_bitfinex(self):
        url0 = 'https://api.bitfinex.com/v1/pubticker/btcusd'
        url1 = 'https://api.bitfinex.com/v1/pubticker/ethusd'
        http = requests.Session()
        while (True):
            try:
                with timeout(seconds=DFT_HTTP_CONN_TIME):
                    real_mkts_raw_data["bitf"]["btc_usd"] = simplejson.loads(http.get(url0).content)
                    real_mkts_raw_data["bitf"]["eth_usd"] =  simplejson.loads(http.get(url1).content)
                    real_mkts_raw_data["bitf"]["created_at"] = datetime.datetime.now()
                    time.sleep(DFT_SLEEP_TIME)
            except Exception, e:
                print str(e)


    def get_polo(self):
        while (True):
            try:
                with timeout(seconds=DFT_HTTP_CONN_TIME):
                    real_mkts_raw_data["polo"] = polo.returnTicker()
                    real_mkts_raw_data["polo"]["created_at"] = datetime.datetime.now()
                    time.sleep(DFT_SLEEP_TIME)
            except Exception, e:
                print str(e)

    def process_raw_data(self):
        pass

    def output_txt(self):
        pass


def run_sys():
    #multithread get data
    try:
        with timeout(seconds=19):
            ticker = update_price()
            ok_btc = get_okcoin_btc()
            ok_eth = get_okcoin_eth()
            acx_hash = get_acx()

            bittrex_price = get_bittrex_lsk()
            bittrex_btc_price = get_bittrex_btc()
            bittrex_eth_price = get_bittrex_eth()
            #mkts = get_wci()

            bitf_btc_usd = float(get_bitfinex_btc())

            jubi_prices = get_jubi_price()
            jubi_lsk = jubi_prices["lsk"]
            jubi_btc = jubi_prices["btc"]
            jubi_eth = jubi_prices["eth"]
            


            bittrex_ask = float(bittrex_price["result"][0]["Ask"])
            bittrex_bid = float(bittrex_price["result"][0]["Bid"])
            bittrex_last= float(bittrex_price["result"][0]["Last"])
            bittrex_spd = (bittrex_ask/bittrex_bid - 1.0) * 100.0
            bittrex_vol = float(bittrex_price["result"][0]["Volume"])
            bittrex_usdt = float(bittrex_btc_price["result"][0]["Last"])

            bittrex_eth_usdt = float(bittrex_eth_price["result"][0]["Last"])

            output=[]
            #china price = jubi_lsk
            #polo price = okcoin/btc * btc/lsk

            #Bittrex_data{'PrevDay': 0.000721, 'Volume': 3177154.99847553, 'Last': 0.00097501, 'OpenSellOrders': 2950, 'TimeStamp': '2017-08-24T17:54:14.46', 'Bid': 0.00096405, 'Created': '2016-05-24T18:49:52.77', 'OpenBuyOrders': 1691, 'High': 0.00099107, 'MarketName': 'BTC-LSK', 'Low': 0.0007, 'Ask': 0.00097507, 'BaseVolume': 2644.59085876}

            jubi_lsk_ls = float(jubi_lsk["last"])
            jubi_hb = float(jubi_lsk["buy"])
            jubi_la = float(jubi_lsk["sell"])
            jubi_vol = float(jubi_lsk["vol"])
            jubi_spd = (jubi_la/jubi_hb -1.0) * 100.0
            p=Prices(ticker_name="jubi_lsk_cny", price=jubi_lsk_ls, created_at=datetime.datetime.now())
            commit()

            polo_ls = float(ticker['BTC_LSK']['last'])
            polo_hb = float(ticker['BTC_LSK']['highestBid'])
            polo_la = float(ticker['BTC_LSK']['lowestAsk'])
            polo_vol = float(ticker['BTC_LSK']['quoteVolume'])
            polo_spd = (polo_la/polo_hb -1.0) * 100.0

            ok_polo_lskrmb = float(ok_btc) * polo_ls
            jb_polo_lskrmb = float(jubi_btc["last"]) * polo_ls

            ok_bitx_lskrmb = float(ok_btc) * bittrex_last
            jb_bitx_lskrmb = float(jubi_btc["last"]) * bittrex_last

            polo_bitx_lsk_diff = (bittrex_last/float(ticker['BTC_LSK']['last'])-1.0)*100.0

            usdtbtc = ticker['USDT_BTC']['last']   
            usdteth = ticker['USDT_ETH']['last']

            lsk_diff_opj = jubi_lsk_ls/ok_polo_lskrmb * 100.0 #ok polo jb
            lsk_diff_jpj = jubi_lsk_ls/jb_polo_lskrmb * 100.0 #jb polo jb

            lsk_diff_obj = jubi_lsk_ls / ok_bitx_lskrmb * 100.0 #ok bitx jb
            lsk_diff_jbj = jubi_lsk_ls / jb_bitx_lskrmb * 100.0 #jb bitx jb

            polo_lsk_usd = float(ticker['BTC_LSK']['last']) * float(usdtbtc)
            bitx_lsk_usd = float(bittrex_last) * float(bittrex_usdt)


            exrate_eth = float(ok_eth) / float(usdteth)
            exrate_btc = float(ok_btc) / float(usdtbtc)

            acx_btc_aud_hb = float(acx_hash['btcaud']['ticker']['buy'])
            acx_btc_aud_ls = float(acx_hash['btcaud']['ticker']['last'])
            acx_btc_aud_la = float(acx_hash['btcaud']['ticker']['sell'])

            exrate_aud_cny_btc = float(ok_btc) / float(acx_btc_aud_ls)
            exrate_aud_usd_btc = float(usdtbtc) / float(acx_btc_aud_ls)
            

            output.append("================ UTC Ticker Time: "+ str( time.strftime("%Y-%m-%d %H:%M:%S") )+" | SRC: Poloniex, Bittrex, jubi.com, Bitfinex, acx.io =====================")
        #    output.append("BTCDGB = " + ticker['BTC_DGB']['last'])
    #        output.append("BTCSC  = " + ticker['BTC_SC']['last'])
            output.append("POLO_LAST = " + format(float(ticker['BTC_LSK']['last']), '.8f') + ", $"+format(polo_lsk_usd, ".3f") +", BP_DIFF = "+str('%.3f' % -polo_bitx_lsk_diff) +"%")
            output.append("BITX_LAST = " + format(bittrex_last, '.8f') + ", $"+format(bitx_lsk_usd, ".3f") + ", PB_DIFF = " + str('%.3f' % polo_bitx_lsk_diff) +"%")
            output.append("JUBI_LAST = CNY " + format(float(jubi_lsk["last"]),'.2f'))
            output.append(" ")
            output.append("JUBI_LSK = " + str(jubi_lsk["buy"])+", "+str(jubi_lsk["sell"])+ ", spread: "+ str('%.3f' % jubi_spd) +"%, vol24: $LSK "+str(int(jubi_vol)) )
            output.append("POLO_LSK = " + str(format(polo_hb, '.8f'))    + ", " + str(format(polo_la, '.8f')) + ", spread: "+ str('%.3f' % polo_spd) +"%, vol24: $LSK "+ str(int(polo_vol)))
            output.append("BITX_LSK = " + str(format(bittrex_bid, '.8f'))+ ", " + str(format(bittrex_ask, '.8f')) + ", spread: "+ str('%.3f' % bittrex_spd) +"%, vol24: $LSK "+ str(int(bittrex_vol)))
            output.append(" ")
            output.append("OK-POLO_LSK/CNY = "+ str('%.3f' % ok_polo_lskrmb) +", " + str('%.2f' % lsk_diff_opj)+"%  | JB-POLO_LSK/CNY = "+ str('%.3f' % jb_polo_lskrmb)+ ", " + str('%.2f' % lsk_diff_jpj)+"%")
            output.append("OK-BITX_LSK/CNY = "+ str('%.3f' % ok_bitx_lskrmb) +", " + str('%.2f' % lsk_diff_obj)+"%  | JB-BITX_LSK/CNY = "+ str('%.3f' % jb_bitx_lskrmb)+ ", " + str('%.2f' % lsk_diff_jbj)+"%")
            output.append(" ")
            output.append("----------------  BTC & ETH  ------------------")
            

            output.append("POLO_BTC_USDT = " + str('%.2f' % float(usdtbtc)) + " | BITX_BTC_USDT = " + str('%.2f' % float(bittrex_usdt)) + " | BITF_BTC_USD = " + str('%.2f' % float(bitf_btc_usd)))
            output.append("POLO_ETH_USDT = " + str('%.2f' % float(usdteth)) + "  | BITX_ETH_USDT = " + str('%.2f' % float(bittrex_eth_usdt)))


            output.append("OK_BTC = " + str(format(float(ok_btc),'.1f')) + " | OK_ETH = " + str(format(float(ok_eth),'.1f')))
            output.append("JB_BTC = " + str(format(float(jubi_btc["last"]),'.1f')) + " | JB_ETH = " + str(format(float(jubi_eth["last"]),'.1f')))
            output.append("AC_BTC = " + str(format(acx_btc_aud_ls,".1f"))) 
            output.append("CALC BTC_USDT/BTC_CNY EXCHANGE RATE  = " + str(str('%.3f' % exrate_btc)))
            output.append("CALC ETH_USDT/ETC_CNY EXCHANGE RATE  = " + str(str('%.3f' % exrate_eth)))
            output.append("CALC BTC_AUD /BTC_CNY EXCHANGE RATE  = " + str(str('%.3f' % exrate_aud_cny_btc)))
            output.append("CALC BTC_AUD /BTC_USD EXCHANGE RATE  = " + str(str('%.3f' % exrate_aud_usd_btc)))
            #output.append("WCI_BTC: " + str(mkts["Bitcoin"]))
            #output.append("WCI_ETH: " + str(mkts["Ethereum"]))
            #output.append("WCI_LTC: " + str(mkts["Litecoin"]))
            #output.append("WCI_DSH: " + str(mkts["Dash"]))
            #output.append("WCI_DGB: " + str(mkts["Digibyte"]))
            #output.append("WCI_LSK: " + str(mkts["Lisk"]))

            lines = "\n".join(output)
            f = open('../prices.txt', 'w')
            f.write(lines)
            print lines

    except Exception,e:
        print str(e)
        return

@db_session
def main():

    while(1):
        run_sys()
        time.sleep(0.5)

#db.generate_mapping(create_tables=True)
#main()

pf=CryptoPrice()
