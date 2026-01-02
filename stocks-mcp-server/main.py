import logging
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import yaml
import requests
import os
from dotenv import load_dotenv
from polygon_api_signatures import (
    get_ticker_price_api,
    get_ticker_details_api,
    get_last_trade_api,
    get_last_quote_api,
    get_aggregates_api,
    get_historic_trades_api
)

load_dotenv()

# Configure logging
LOG_ENABLED = os.getenv("MCP_SERVER_LOG_ENABLED", "true").lower() == "true"
logging.basicConfig(
    level=logging.INFO if LOG_ENABLED else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
app = FastAPI()

logger.info("MCP Server initializing...")
logger.info(f"Polygon API Key configured: {'Yes' if POLYGON_API_KEY else 'No'}")


class StockRequest(BaseModel):
    ticker: str

class TickerDetailsRequest(BaseModel):
    ticker: str

class LastTradeRequest(BaseModel):
    ticker: str

class LastQuoteRequest(BaseModel):
    ticker: str

class AggregatesRequest(BaseModel):
    ticker: str
    multiplier: int
    timespan: str
    from_date: str
    to_date: str
    limit: int

class HistoricTradesRequest(BaseModel):
    ticker: str
    date: str
    limit: int
    timestamp: int


def raise_polygon_error(r: requests.Response, tool_name: str):
    try:
        error_detail = r.json()
    except Exception:
        error_detail = r.text
    logger.error(f"[{tool_name}] Polygon API Error {r.status_code}: {error_detail}")
    raise HTTPException(status_code=400, detail={
        "status_code": r.status_code,
        "error": error_detail
    })


@app.get("/get_tool_defs")
def get_tool_defs():
    logger.info("Request received: GET /get_tool_defs")
    try:
        with open("mcp.yaml", "r") as f:
            tool_defs = yaml.safe_load(f)
        logger.info(f"Loaded {len(tool_defs.get('tools', []))} tool definitions")
        return JSONResponse(content=tool_defs)
    except Exception as e:
        logger.error(f"Failed to load tool definitions: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/tools/get_ticker_price")
def get_ticker_price(req: StockRequest):
    tool_name = "get_ticker_price"
    logger.info(f"[{tool_name}] Request received - ticker: {req.ticker}")

    url = get_ticker_price_api.format(ticker=req.ticker.upper(), api_key=POLYGON_API_KEY)
    logger.info(f"[{tool_name}] Calling Polygon API")

    r = requests.get(url)
    logger.info(f"[{tool_name}] Polygon response status: {r.status_code}")

    if r.status_code != 200:
        raise_polygon_error(r, tool_name)

    data = r.json()
    price = data["results"][0]["c"] if "results" in data and data["results"] else None
    timestamp = data["results"][0]["t"] if data["results"] else None

    result = {
        "ticker": req.ticker.upper(),
        "price": price,
        "timestamp": timestamp
    }
    logger.info(f"[{tool_name}] Response: ticker={result['ticker']}, price={result['price']}")
    return result


@app.post("/tools/get_ticker_details")
def get_ticker_details(req: TickerDetailsRequest):
    tool_name = "get_ticker_details"
    logger.info(f"[{tool_name}] Request received - ticker: {req.ticker}")

    url = get_ticker_details_api.format(ticker=req.ticker.upper(), api_key=POLYGON_API_KEY)
    logger.info(f"[{tool_name}] Calling Polygon API")

    r = requests.get(url)
    logger.info(f"[{tool_name}] Polygon response status: {r.status_code}")

    if r.status_code != 200:
        raise_polygon_error(r, tool_name)

    data = r.json().get("results", {})
    result = {
        "name": data.get("name"),
        "exchange": data.get("primary_exchange"),
        "locale": data.get("locale"),
        "market": data.get("market"),
        "type": data.get("type")
    }
    logger.info(f"[{tool_name}] Response: name={result['name']}, exchange={result['exchange']}")
    return result


@app.post("/tools/get_last_trade")
def get_last_trade(req: LastTradeRequest):
    tool_name = "get_last_trade"
    logger.info(f"[{tool_name}] Request received - ticker: {req.ticker}")

    url = get_last_trade_api.format(ticker=req.ticker.upper(), api_key=POLYGON_API_KEY)
    logger.info(f"[{tool_name}] Calling Polygon API")

    r = requests.get(url)
    logger.info(f"[{tool_name}] Polygon response status: {r.status_code}")

    if r.status_code != 200:
        raise_polygon_error(r, tool_name)

    data = r.json().get("results", {})
    result = {
        "price": data.get("p"),
        "size": data.get("s"),
        "timestamp": data.get("t")
    }
    logger.info(f"[{tool_name}] Response: price={result['price']}, size={result['size']}")
    return result


@app.post("/tools/get_last_quote")
def get_last_quote(req: LastQuoteRequest):
    tool_name = "get_last_quote"
    logger.info(f"[{tool_name}] Request received - ticker: {req.ticker}")

    url = get_last_quote_api.format(ticker=req.ticker.upper(), api_key=POLYGON_API_KEY)
    logger.info(f"[{tool_name}] Calling Polygon API")

    r = requests.get(url)
    logger.info(f"[{tool_name}] Polygon response status: {r.status_code}")

    if r.status_code != 200:
        raise_polygon_error(r, tool_name)

    data = r.json().get("results", {})
    result = {
        "askprice": data.get("ap"),
        "asksize": data.get("as"),
        "bidprice": data.get("bp"),
        "bidsize": data.get("bs"),
        "timestamp": data.get("t")
    }
    logger.info(f"[{tool_name}] Response: bid={result['bidprice']}, ask={result['askprice']}")
    return result


@app.post("/tools/get_aggregates")
def get_aggregates(req: AggregatesRequest):
    tool_name = "get_aggregates"
    logger.info(f"[{tool_name}] Request received - ticker: {req.ticker}, timespan: {req.timespan}, from: {req.from_date}, to: {req.to_date}")

    url = get_aggregates_api.format(
        ticker=req.ticker.upper(),
        multiplier=req.multiplier,
        timespan=req.timespan,
        from_date=req.from_date,
        to_date=req.to_date,
        limit=req.limit,
        api_key=POLYGON_API_KEY
    )
    logger.info(f"[{tool_name}] Calling Polygon API")

    r = requests.get(url)
    logger.info(f"[{tool_name}] Polygon response status: {r.status_code}")

    if r.status_code != 200:
        raise_polygon_error(r, tool_name)

    data = r.json()
    results = data.get("results", [])
    result = {"results": results}
    logger.info(f"[{tool_name}] Response: {len(results)} aggregate(s) returned")
    return result


@app.post("/tools/get_historic_trades")
def get_historic_trades(req: HistoricTradesRequest):
    tool_name = "get_historic_trades"
    logger.info(f"[{tool_name}] Request received - ticker: {req.ticker}, date: {req.date}, limit: {req.limit}")

    url = get_historic_trades_api.format(
        ticker=req.ticker.upper(),
        date=req.date,
        limit=req.limit,
        timestamp=req.timestamp,
        api_key=POLYGON_API_KEY
    )
    logger.info(f"[{tool_name}] Calling Polygon API")

    r = requests.get(url)
    logger.info(f"[{tool_name}] Polygon response status: {r.status_code}")

    if r.status_code != 200:
        raise_polygon_error(r, tool_name)

    data = r.json()
    results = data.get("results", [])
    result = {"results": results}
    logger.info(f"[{tool_name}] Response: {len(results)} trade(s) returned")
    return result
