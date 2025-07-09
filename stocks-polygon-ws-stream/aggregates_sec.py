from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Feed, Market
from typing import List

client = WebSocketClient(
	api_key="ksk7jS4bXeDeSd6JC3EX6WJYaHWOpzhs",
	feed=Feed.Delayed,
	market=Market.Stocks
	)

# aggregates (per second)
client.subscribe("A.*") # single ticker
# client.subscribe("A.*") # all tickers
# client.subscribe("A.AAPL") # single ticker
# client.subscribe("A.AAPL", "AM.MSFT") # multiple tickers

def handle_msg(msgs: List[WebSocketMessage]):
    for m in msgs:
        print(m)

# print messages
client.run(handle_msg)
