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

# aggregates (per minute)
client.subscribe("AM.*") # single ticker
# client.subscribe("AM.*") # all tickers
# client.subscribe("AM.AAPL") # single ticker
# client.subscribe("AM.AAPL", "AM.MSFT") # multiple tickers

def handle_msg(msgs: List[WebSocketMessage]):
    for m in msgs:
        print(m)

# print messages
client.run(handle_msg)
