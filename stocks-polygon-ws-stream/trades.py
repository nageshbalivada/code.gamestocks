import os
from dotenv import load_dotenv
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Feed, Market
from typing import List

load_dotenv()

client = WebSocketClient(
	api_key=os.getenv("POLYGON_API_KEY"),
	feed=Feed.Delayed,
	market=Market.Stocks
	)

# trades
client.subscribe("T.*")
# client.subscribe("T.*")  # all trades
# client.subscribe("T.TSLA") # single tickers
# client.subscribe("T.TSLA", "T.UBER") # multiple tickers

def handle_msg(msgs: List[WebSocketMessage]):
    for m in msgs:
        print(m)

# print messages
client.run(handle_msg)
