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

# quotes
client.subscribe("Q.*")
# client.subscribe("Q.*")  # all quotes
# client.subscribe("Q.TSLA", "Q.UBER") # single ticker
# client.subscribe("Q.TSLA", "Q.UBER") # multiple tickers

def handle_msg(msgs: List[WebSocketMessage]):
    for m in msgs:
        print(m)

# print messages
client.run(handle_msg)
