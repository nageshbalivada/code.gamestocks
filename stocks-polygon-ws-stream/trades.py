from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Feed, Market
from typing import List

client = WebSocketClient(
	api_key="ksk7jS4bXeDeSd6JC3EX6WJYaHWOpzhs",
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
