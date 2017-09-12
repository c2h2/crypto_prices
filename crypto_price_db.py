import datetime
from decimal import Decimal
from pony.orm import *
 
#database = Database("sqlite","crypto_prices.sqlite", create_db=True)
db = Database()
db.bind(provider='postgres', user='', password='', host='localhost', database='crypto_prices')
#database.drop_all_tables(with_all_data=True)

########################################################################
class Prices(db.Entity):
    ticker_name = Required(str)
    price = Required(Decimal)
    created_at = Required(datetime.datetime, precision=6)

