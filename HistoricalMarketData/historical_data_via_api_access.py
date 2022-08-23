# pip install tardis-client
import asyncio
from tardis_client import TardisClient, Channel
f_hist = open("../Config/ftx_historical_market_data_api_key", "r")
historical_key = f_hist.readline().strip()
f_hist.close()
print(historical_key)

tardis_client = TardisClient(api_key=historical_key)

async def replay():
  # replay method returns Async Generator
  messages = tardis_client.replay(
    exchange="ftx",
    from_date="2020-01-01",
    to_date="2020-01-02",
    filters=[Channel(name="orderbook", symbols=["BTC-PERP"])]
#    filters=[Channel(name="orderbook", symbols=["BTC-PERP"]),Channel("trade", ["BTC-PERP"])]
  )

  # messages as provided by FTX real-time stream
  async for local_timestamp, message in messages:
    print(message)


asyncio.run(replay())
