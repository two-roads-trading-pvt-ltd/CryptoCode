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
	data_types = symbol["dataTypes"]
	from_date =  symbol["availableSince"]
	to_date = symbol["availableTo"]
	# skip groupped symbols
	if symbol_id in ['PERPETUALS', 'SPOT', 'FUTURES']:
		continue
	print(f"Downloading {exchange} {data_types} for {symbol_id} from {from_date} to {to_date}")


