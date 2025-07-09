from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Feed, Market
from typing import List

client = WebSocketClient(
	api_key="ksk7jS4bXeDeSd6JC3EX6WJYaHWOpzhs",
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
