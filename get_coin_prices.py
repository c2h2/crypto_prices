import requests
import simplejson
import time
import signal
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
	try:
		with timeout(seconds=5):
			ticker = update_price()
			ok_btc = get_okcoin_btc()
			ok_eth = get_okcoin_eth() 
			mkts = get_wci() 

			output=[]

			output.append("================"+ str( time.strftime("%Y-%m-%d %H:%M:%S") )+"=====================")
			output.append("BTCDGB = " + ticker['BTC_DGB']['last'])
			output.append("BTCLSK = " + ticker['BTC_LSK']['last'])

			usdtbtc = ticker['USDT_BTC']['last']   
			usdteth = ticker['USDT_ETH']['last']

			output.append("USDT_BTC = " + usdtbtc)
			output.append("USDT_ETH = " + usdteth)
			output.append("CNY_BTC = " + ok_btc)
			output.append("CNY_ETH = " + ok_eth)
			output.append("BTC EXCHANGE RATE  = " + str(float(ok_btc) / float(usdtbtc)))
			output.append( "ETH EXCHANGE RATE  = " + str(float(ok_eth) / float(usdteth)))
			output.append("WCI_BTC: " + str(mkts["Bitcoin"]))
			output.append("WCI_ETH: " + str(mkts["Ethereum"]))
			#output.append("WCI_LTC: " + str(mkts["Litecoin"]))
			output.append("WCI_DSH: " + str(mkts["Dash"]))
			output.append("WCI_DGB: " + str(mkts["Digibyte"]))
			output.append("WCI_LSK: " + str(mkts["Lisk"]))

			lines = "\n".join(output)
			f = open('../prices.txt', 'w')
			f.write(lines)
			print lines

	except:
		print "Exception Occurred, Retry..."
		return



while(1):
	run_sys()
	time.sleep(1)
