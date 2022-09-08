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
args = parser.parse_args()

exchange_ = args.exchange if args.exchange else 'ftx'
fromDate_ = args.fromDate if args.fromDate else "2019-11-01"
toDate_ = args.toDate if args.toDate else "2019-11-02"
symbol_ = args.symbol if args.symbol else "ETH-PERPETUAL"

exchange_details = get_exchange_details(exchange)

f_hist = open("../Config/ftx_historical_market_data_api_key", "r")
historical_key = f_hist.readline().strip()
f_hist.close()
print(historical_key)

datasets.download(
    exchange=exchange_,
    data_types=[
        "incremental_book_L2",
        "trades",
        "quotes",
        "derivative_ticker",
        "book_snapshot_25",
        "liquidations"
    ],
    from_date=fromDate_,
    to_date=toDate_,
    symbols=[symbol],
    api_key="historical_key",
)
