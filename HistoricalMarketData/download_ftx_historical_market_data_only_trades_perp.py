# requires Python >=3.6
# pip install tardis-dev

from tardis_dev import datasets, get_exchange_details
import logging
import argparse
from datetime import datetime
from datetime import date
import time

# optionally enable debug logs
# logging.basicConfig(level=logging.DEBUG)

msg = "Called as SYMBOL FROMDATE TODATE"
# Initialize parser
parser = argparse.ArgumentParser(description = msg)
parser.add_argument("--exchange")
parser.add_argument("--outputPath")
args = parser.parse_args()

exchange_ = args.exchange if args.exchange else 'ftx'
output_path = args.outputPath if args.outputPath else '/NAS1/subham/CryptoData/ftx/perpetual'
exchange_details = get_exchange_details(exchange_)   

f_hist = open("../Config/ftx_historical_market_data_api_key", "r")
historical_key = f_hist.readline().strip()
f_hist.close()
print(historical_key)

# iterate over and download all data for every symbol
for symbol in exchange_details["datasets"]["symbols"]:
    # alternatively specify datatypes explicitly ['trades', 'incremental_book_L2', 'quotes'] etc
    # see available options https://docs.tardis.dev/downloadable-csv-files#data-types
    symbol_id = symbol["id"]
    symbol_type = symbol["type"]
    av_from_date =  str(symbol["availableSince"])
    av_to_date = str(symbol["availableTo"])
    #av_from_date =  "2022-01-01T00:00:00.000Z"
    #av_to_date = "2022-09-01T00:00:00.000Z"
    from_date_format = datetime.strptime(av_from_date,  "%Y-%m-%dT%H:%M:%S.%fZ")
    from_unix_sec = int(time.mktime(from_date_format.timetuple()))
    to_date_format = datetime.strptime(av_to_date,  "%Y-%m-%dT%H:%M:%S.%fZ")
    to_unix_sec = int(time.mktime(to_date_format.timetuple()))

    if to_unix_sec < 1640995200:
        continue
    if from_unix_sec <= 1640995200:
        av_from_date = "2022-01-01T00:00:00.000Z"
    
    # skip groupped symbols
    if symbol_id in ['PERPETUALS', 'SPOT', 'FUTURES']:
        continue
    if symbol_type != "perpetual":
        continue

    print(f"Downloading {exchange_} trades for {symbol_id} from {av_from_date} to {av_to_date}")

    # each CSV dataset format is documented at https://docs.tardis.dev/downloadable-csv-files#data-types
    # see https://docs.tardis.dev/downloadable-csv-files#download-via-client-libraries for full options docs
    datasets.download(
        exchange = exchange_,
        data_types = ["trades"],
        from_date =  av_from_date,
        to_date = av_to_date,
        symbols = [symbol_id],
        # TODO set your API key here
        api_key = historical_key,
        # path where CSV data will be downloaded into
        download_dir = output_path,
    )
