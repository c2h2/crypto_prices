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

def get_bittrex_lsk():
	url='https://bittrex.com/api/v1.1/public/getmarketsummary?market=btc-lsk'
	http=requests.Session()
	r = http.get(url)
	data = simplejson.loads(r.content)

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

			bittrex_price = get_bittrex_lsk()
			bittrex_ask = float(bittrex_price["result"][0]["Ask"])
			bittrex_bid = float(bittrex_price["result"][0]["Bid"])
			bittrex_last= float(bittrex_price["result"][0]["Last"])
			bittrex_spd = (bittrex_ask/bittrex_bid - 1.0) * 100.0
			bittrex_vol = float(bittrex_price["result"][0]["Volume"])

			output=[]
			#china price = jubi_lsk
			#polo price = okcoin/btc * btc/lsk

			#Bittrex_data{'PrevDay': 0.000721, 'Volume': 3177154.99847553, 'Last': 0.00097501, 'OpenSellOrders': 2950, 'TimeStamp': '2017-08-24T17:54:14.46', 'Bid': 0.00096405, 'Created': '2016-05-24T18:49:52.77', 'OpenBuyOrders': 1691, 'High': 0.00099107, 'MarketName': 'BTC-LSK', 'Low': 0.0007, 'Ask': 0.00097507, 'BaseVolume': 2644.59085876}

			jubi_lsk_ls = float(jubi_lsk["last"])
			jubi_hb = float(jubi_lsk["buy"])
			jubi_la = float(jubi_lsk["sell"])
			jubi_spd = (jubi_la/jubi_hb -1.0) * 100.0

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


			exrate_eth = float(ok_eth) / float(usdteth)
			exrate_btc = float(ok_btc) / float(usdtbtc)

			output.append("================LSK "+ str( time.strftime("%Y-%m-%d %H:%M:%S") )+"=====================")
		#	output.append("BTCDGB = " + ticker['BTC_DGB']['last'])
	#		output.append("BTCSC  = " + ticker['BTC_SC']['last'])
			output.append("POLO_BTCLSK = " + format(float(ticker['BTC_LSK']['last']), '.8f'))
			output.append("BITX_BTCLSK = " + format(bittrex_last, '.8f') + ", PB_DIFF = " + str('%.3f' % polo_bitx_lsk_diff) +"%")
			output.append(" ")
			output.append("JUBI_LSK = " + str(jubi_lsk["buy"])+", "+str(jubi_lsk["sell"])+ ", spread: "+ str('%.3f' % jubi_spd) +"%")
			output.append("POLO_LSK = " + str(format(polo_hb, '.8f'))    + ", " + str(format(polo_la, '.8f')) + ", spread: "+ str('%.3f' % polo_spd) +"%, vol24: $LSK "+ str(int(polo_vol)))
			output.append("BITX_LSK = " + str(format(bittrex_ask, '.8f'))+ ", " + str(format(bittrex_bid, '.8f')) + ", spread: "+ str('%.3f' % bittrex_spd) +"%, vol24: $LSK "+ str(int(bittrex_vol)))
			output.append(" ")
			output.append("OK-POLO_LSK/RMB = "+ str('%.3f' % ok_polo_lskrmb) + "       | JB-POLO_LSK/RMB = "+ str('%.3f' % jb_polo_lskrmb))
			output.append("OK-BITX_LSK/RMB = "+ str('%.3f' % ok_bitx_lskrmb) + "       | JB-BITX_LSK/RMB = "+ str('%.3f' % jb_bitx_lskrmb))
			output.append(" ")
			output.append("OK-JUBI_LSK/POLO_LSK = "+ str('%.2f' % lsk_diff_opj)+"%" + " | JB-JUBI_LSK/POLO_LSK = "+ str('%.2f' % lsk_diff_jpj)+"%")
			output.append("OK-JUBI_LSK/BITX_LSK = "+ str('%.2f' % lsk_diff_obj)+"%" + " | JB-JUBI_LSK/BITX_LSK = "+ str('%.2f' % lsk_diff_jbj)+"%")
			output.append("----------------  BTC & ETH  ------------------")
			
			output.append("POLO_USDT_BTC = " + str('%.2f' % float(usdtbtc)))
			output.append("POLO_USDT_ETH = " + str('%.2f' % float(usdteth)))
			output.append("OK_BTC = " + str(format(float(ok_btc),'.1f')) + " | OK_ETH = " + str(format(float(ok_eth),'.1f')))
			output.append("JB_BTC = " + str(format(float(jubi_btc["last"]),'.1f')) + " | JB_ETH = " + str(format(float(jubi_eth["last"]),'.1f')))
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
