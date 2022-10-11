# pip install tardis-dev
# requires Python >=3.6
from tardis_dev import datasets, get_exchange_details
import logging

import argparse
 
msg = "Called as SYMBOL FROMDATE TODATE"
 
# Initialize parser
parser = argparse.ArgumentParser(description = msg)
parser.add_argument("--exchange")
parser.add_argument("--symbol")
parser.add_argument("--fromDate")
parser.add_argument("--toDate")
parser.add_argument("--outputPath")
args = parser.parse_args()

exchange_ = args.exchange if args.exchange else 'ftx'
fromDate_ = args.fromDate if args.fromDate else "2019-11-01"
toDate_ = args.toDate if args.toDate else "2019-11-02"
symbol_ = args.symbol if args.symbol else "ETH-PERPETUAL"
output_path = args.outputPath if args.outputPath else '/NAS1/data/CryptoData/ftx'

exchange_details = get_exchange_details(exchange_)

f_hist = open("../Config/ftx_historical_market_data_api_key", "r")
historical_key = f_hist.readline().strip()
f_hist.close()
print(historical_key)

datasets.download(
    exchange=exchange_,
    data_types=[
        "trades",
        "book_snapshot_25",
        "book_ticker"
    ],
    from_date=fromDate_,
    to_date=toDate_,
    symbols=[symbol_],
    api_key=historical_key,
    download_dir = output_path,
)
