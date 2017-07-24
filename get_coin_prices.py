import requests
import simplejson
import time
from multiprocessing.pool import ThreadPool
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
	
def get_wci():
	key='pUzGh85jp4fmwVYeLVW0k2bX0'
	url='https://www.worldcoinindex.com/apiservice/json?key='+key

	http=requests.Session()
	r = http.get(url)
	data = simplejson.loads(r.content)
	mkts = data['Markets']
	_mkts = {}
	for i in range(len(mkts)):
		#print mkts[i]
		_mkts[mkts[i]['Name']] = mkts[i]

	return _mkts


def run_sys():
	#multithread get data
	pool = ThreadPool(processes=4)

	async_result1 = pool.apply_async(update_price)
	async_result2 = pool.apply_async(get_okcoin_btc)
	async_result3 = pool.apply_async(get_okcoin_eth)
	async_result4 = pool.apply_async(get_wci)


	ticker = async_result1.get() 
	ok_btc = async_result2.get() 
	ok_eth = async_result3.get() 
	mkts = async_result4.get() 

	print "================"+ str( time.strftime("%Y-%m-%d %H:%M:%S") )+"====================="
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
	print "WCI_BTC: " + str(mkts["Bitcoin"])
	print "WCI_ETH: " + str(mkts["Ethereum"])
	print "WCI_DGB: " + str(mkts["Digibyte"])
	print "WCI_LSK: " + str(mkts["Lisk"])


while(1):
	run_sys()
	time.sleep(1)