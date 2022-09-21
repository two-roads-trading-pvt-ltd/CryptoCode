# pip install tardis-client
import asyncio
from tardis_client import TardisClient, Channel
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
fromDate_ = args.fromDate if args.fromDate else "2022-08-19"
toDate_ = args.toDate if args.toDate else "2022-08-20"
symbol_ = args.symbol if args.symbol else "BTC-PERP"


f_hist = open("../Config/ftx_historical_market_data_api_key", "r")
historical_key = f_hist.readline().strip()
f_hist.close()
print(historical_key)

tardis_client = TardisClient(api_key=historical_key)

async def replay():
  # replay method returns Async Generator
  messages = tardis_client.replay(
    exchange=exchange_,
    from_date=fromDate_,
    to_date=toDate_,
    filters=[Channel(name="orderbook", symbols=[symbol_])]
#    filters=[Channel(name="orderbook", symbols=["BTC-PERP"]),Channel("trade", ["BTC-PERP"])]
  )

  # messages as provided by FTX real-time stream
  async for local_timestamp, message in messages:
    print(message)


asyncio.run(replay())
