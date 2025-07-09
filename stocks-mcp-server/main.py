from fastapi import FastAPI, HTTPException
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

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
app = FastAPI()


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

def raise_polygon_error(r: requests.Response):
    try:
        error_detail = r.json()
    except Exception:
        error_detail = r.text
    print(f"❌ Polygon API Error {r.status_code}: {error_detail}")
    raise HTTPException(status_code=400, detail={
        "status_code": r.status_code,
        "error": error_detail
    })

@app.get("/get_tool_defs")
def get_tool_defs():
    try:
        with open("mcp.yaml", "r") as f:
            tool_defs = yaml.safe_load(f)
        return JSONResponse(content=tool_defs)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/tools/get_ticker_price")
def get_ticker_price(req: StockRequest):
    url = get_ticker_price_api.format(ticker=req.ticker.upper(), api_key=POLYGON_API_KEY)
    r = requests.get(url)
    if r.status_code != 200:
        raise_polygon_error(r)
    data = r.json()
    price = data["results"][0]["c"] if "results" in data and data["results"] else None
    return {
        "ticker": req.ticker.upper(),
        "price": price,
        "timestamp": data["results"][0]["t"] if data["results"] else None
    }

@app.post("/tools/get_ticker_details")
def get_ticker_details(req: TickerDetailsRequest):
    url = get_ticker_details_api.format(ticker=req.ticker.upper(), api_key=POLYGON_API_KEY)
    r = requests.get(url)
    if r.status_code != 200:
        raise_polygon_error(r)
    data = r.json().get("results", {})
    return {
        "name": data.get("name"),
        "exchange": data.get("primary_exchange"),
        "locale": data.get("locale"),
        "market": data.get("market"),
        "type": data.get("type")
    }

@app.post("/tools/get_last_trade")
def get_last_trade(req: LastTradeRequest):
    url = get_last_trade_api.format(ticker=req.ticker.upper(), api_key=POLYGON_API_KEY)
    r = requests.get(url)
    if r.status_code != 200:
        raise_polygon_error(r)
    data = r.json().get("results", {})
    return {
        "price": data.get("p"),
        "size": data.get("s"),
        "timestamp": data.get("t")
    }

@app.post("/tools/get_last_quote")
def get_last_quote(req: LastQuoteRequest):
    url = get_last_quote_api.format(ticker=req.ticker.upper(), api_key=POLYGON_API_KEY)
    r = requests.get(url)
    if r.status_code != 200:
        raise_polygon_error(r)
    data = r.json().get("results", {})
    return {
        "askprice": data.get("ap"),
        "asksize": data.get("as"),
        "bidprice": data.get("bp"),
        "bidsize": data.get("bs"),
        "timestamp": data.get("t")
    }

@app.post("/tools/get_aggregates")
def get_aggregates(req: AggregatesRequest):
    url = get_aggregates_api.format(
        ticker=req.ticker.upper(),
        multiplier=req.multiplier,
        timespan=req.timespan,
        from_date=req.from_date,
        to_date=req.to_date,
        limit=req.limit,
        api_key=POLYGON_API_KEY
    )
    r = requests.get(url)
    if r.status_code != 200:
        raise_polygon_error(r)
    data = r.json()
    return {
        "results": data.get("results", [])
    }

@app.post("/tools/get_historic_trades")
def get_historic_trades(req: HistoricTradesRequest):
    url = get_historic_trades_api.format(
        ticker=req.ticker.upper(),
        date=req.date,
        limit=req.limit,
        timestamp=req.timestamp,
        api_key=POLYGON_API_KEY
    )
    r = requests.get(url)
    if r.status_code != 200:
        raise_polygon_error(r)
    data = r.json()
    return {
        "results": data.get("results", [])
    }
