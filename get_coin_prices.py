import requests
import simplejson
import time
from poloniex import Poloniex
polo = Poloniex()
#pip install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.6.zip     

def get_okcoin_eth():
	url='https://www.okcoin.cn/api/v1/ticker.do?symbol=eth_cny'
	http=requests.Session()
	r = http.get(url)
	data = simplejson.loads(r.content)

	return data['ticker']['last']

def get_okcoin_btc():
	url='https://www.okcoin.cn/api/v1/ticker.do?symbol=btc_cny'
	http=requests.Session()
	r = http.get(url)
	data = simplejson.loads(r.content)

	return data['ticker']['last']


def update_price(): 
	return polo.returnTicker()
	





def run_sys():
	ticker = update_price()
	ok_btc = get_okcoin_btc()
	ok_eth = get_okcoin_eth()

	print "====================================="
	print "BTCDGB = " + ticker['BTC_DGB']['last']
	print "BTCLSK = " + ticker['BTC_LSK']['last']

	usdtbtc = ticker['USDT_BTC']['last']   
	usdteth = ticker['USDT_ETH']['last']

	print "USDT_BTC = " + usdtbtc  
	print "USDT_ETH = " + usdteth
	print "CNY_BTC = " + ok_btc
	print "CNY_ETH = " + ok_eth
	print "BTC EXCHANGE RATE  = " + str(float(ok_btc) / float(usdtbtc))
	print "ETH EXCHANGE RATE  = " + str(float(ok_eth) / float(usdteth))

	#print "RATIO =  " + str(float(usdtbtc) / float(usdteth))


while(1):
	run_sys()
	time.sleep(1)