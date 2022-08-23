# requires Python >=3.6
# pip install tardis-dev

from tardis_dev import datasets, get_exchange_details
import logging

# optionally enable debug logs
# logging.basicConfig(level=logging.DEBUG)

exchange = 'ftx'
exchange_details = get_exchange_details(exchange)   
for symbol in exchange_details["datasets"]["symbols"]:
	symbol_id = symbol["id"]
	# skip groupped symbols
	if symbol_id in ['PERPETUALS', 'SPOT', 'FUTURES']:
		continue
	print(symbol_id)


