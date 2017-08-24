import requests
import simplejson
import time
import signal
import redis
import json
from poloniex import Poloniex
#from multiprocessing.pool import ThreadPool

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

redis_enabled = True
try:
	redis = redis.StrictRedis(host='localhost', port=6379, db=0)
except:
	redis_enabled = False

polo = Poloniex()
#pip install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.6.zip     

def get_jubi_price():
 	url='http://www.jubi.com/api/v1/allticker/'
 	http=requests.Session()
 	r = http.get(url)
 	data=simplejson.loads(r.content)
 	if(redis_enabled):
  		redis["jubi_mkts"]=data

  	return data


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
	print(r.content)
	data = simplejson.loads(r.content)

	mkts = data['Markets']
	_mkts = {}
	for i in range(len(mkts)):
		#print mkts[i]
		_mkts[mkts[i]['Name']] = mkts[i]
  
	if (redis_enabled):	
		redis["mkts"]=json.dumps(_mkts)
	
	return _mkts


def run_sys():
	#multithread get data
	try:
		with timeout(seconds=19):
			ticker = update_price()
			ok_btc = get_okcoin_btc()
			ok_eth = get_okcoin_eth() 
			#mkts = get_wci()
			jubi_prices = get_jubi_price()
			jubi_lsk = jubi_prices["lsk"]
			jubi_btc = jubi_prices["btc"]
			jubi_eth = jubi_prices["eth"]

			output=[]
			#china price = jubi_lsk
			#polo price = okcoin/btc * btc/lsk

			jubi_lsk_ls = float(jubi_lsk["last"])
			jubi_hb = float(jubi_lsk["buy"])
			jubi_la = float(jubi_lsk["sell"])
			jubi_spd = (jubi_la/jubi_hb -1.0) * 100.0

			polo_ls = float(ticker['BTC_LSK']['last'])
			polo_hb = float(ticker['BTC_LSK']['highestBid'])
			polo_la = float(ticker['BTC_LSK']['lowestAsk'])
			polo_spd = (polo_la/polo_hb -1.0) * 100.0

			ok_polo_lskrmb = float(ok_btc) * polo_ls
			jb_polo_lskrmb = float(jubi_btc["last"]) * polo_ls

			usdtbtc = ticker['USDT_BTC']['last']   
			usdteth = ticker['USDT_ETH']['last']

			lsk_diff_opj = jubi_lsk_ls/ok_polo_lskrmb * 100.0 #ok polo jb
			lsk_diff_jpj = jubi_lsk_ls/jb_polo_lskrmb * 100.0 #jb polo jb

			exrate_eth = float(ok_eth) / float(usdteth)
			exrate_btc = float(ok_btc) / float(usdtbtc)

			output.append("================"+ str( time.strftime("%Y-%m-%d %H:%M:%S") )+"=====================")
		#	output.append("BTCDGB = " + ticker['BTC_DGB']['last'])
	#		output.append("BTCSC  = " + ticker['BTC_SC']['last'])
			output.append("BTCLSK = " + ticker['BTC_LSK']['last'])
			
			output.append("JUBI_LSK = " + str(jubi_lsk["buy"])+", "+str(jubi_lsk["sell"])+ ", spread: "+ str('%.3f' % jubi_spd) +"%")
			output.append("POLO_LSK = " + str(polo_hb)+", "+str(polo_la) + ", spread: "+ str('%.3f' % polo_spd) +"%")
			output.append("OK|POLO_LSK/RMB = "+ str(ok_polo_lskrmb))
			output.append("JB|POLO_LSK/RMB = "+ str(jb_polo_lskrmb))
			output.append("OK|JUBI_LSK/POLO_LSK = "+ str('%.4f' % lsk_diff_opj)+"%")
			output.append("JB|JUBI_LSK/POLO_LSK = "+ str('%.4f' % lsk_diff_jpj)+"%")
			


			output.append("POLO_USDT_BTC = " + usdtbtc)
			output.append("POLO_USDT_ETH = " + usdteth)
			output.append("OK_BTC = " + ok_btc)
			output.append("OK_ETH = " + ok_eth)
			output.append("JB_BTC = " + str(jubi_btc["last"]))
			output.append("JB_ETH = " + str(jubi_eth["last"]))
			output.append("CALC BTC_USDT/BTC_CNY EXCHANGE RATE  = " + str(str('%.3f' % exrate_btc)))
			output.append("CALC ETH_USDT/ETC_CNY EXCHANGE RATE  = " + str(str('%.3f' % exrate_eth)))
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



while(1):
	run_sys()
	time.sleep(1)
