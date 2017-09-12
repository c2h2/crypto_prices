from crypto_price_db import *

# turn on debug mode
sql_debug(True)
 
# map the models to the database 
# and create the tables, if they don't exist
db.generate_mapping(create_tables=True)

commit()
