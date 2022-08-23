# pip install tardis-dev
# requires Python >=3.6
from tardis_dev import datasets

f_hist = open("../Config/ftx_historical_market_data_api_key", "r")
historical_key = f_hist.readline().strip()
f_hist.close()
print(historical_key)

datasets.download(
    exchange="deribit",
    data_types=[
        "incremental_book_L2",
        "trades",
        "quotes",
        "derivative_ticker",
        "book_snapshot_25",
        "liquidations"
    ],
    from_date="2019-11-01",
    to_date="2019-11-02",
    symbols=["BTC-PERPETUAL", "ETH-PERPETUAL"],
    api_key="historical_key",
)
