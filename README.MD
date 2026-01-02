# GameStocks

A conversational AI interface for querying real-time stock market data using natural language. Ask questions like "What is the stock price of Elon Musk's company?" and get real-time answers.

## Architecture

```
┌─────────────────┐     HTTP/JSON      ┌─────────────────┐     REST API      ┌─────────────────┐
│                 │ ◄───────────────►  │                 │ ◄──────────────►  │                 │
│   User Input    │                    │   MCP Server    │                   │   Polygon.io    │
│                 │                    │   (FastAPI)     │                   │   Stock API     │
└────────┬────────┘                    └─────────────────┘                   └─────────────────┘
         │
         │  Natural Language
         ▼
┌─────────────────┐
│                 │
│  Claude Agent   │
│  (Anthropic)    │
│                 │
└─────────────────┘
```

## Components

| Component | Description | Location |
|-----------|-------------|----------|
| **MCP Server** | FastAPI REST server exposing stock data tools | `stocks-mcp-server/` |
| **AI Agent** | Anthropic Claude agent for natural language queries | `stocks-agent/` |
| **WebSocket Streams** | Real-time market data streaming (trades, quotes, aggregates) | `stocks-polygon-ws-stream/` |

## Available Tools

The MCP Server exposes 6 tools for stock data retrieval:

| Tool | Description | Free Tier |
|------|-------------|-----------|
| `get_ticker_price` | Get latest stock price | Yes |
| `get_ticker_details` | Get company metadata (name, exchange, type) | No |
| `get_last_trade` | Get most recent trade (price, size, time) | No |
| `get_last_quote` | Get current bid/ask (NBBO) | No |
| `get_aggregates` | Get historical OHLCV bars | No |
| `get_historic_trades` | Get historical trade ticks | No |

## Tech Stack

- **Language:** Python 3.13+
- **AI Model:** Claude Sonnet 4 (claude-sonnet-4-20250514)
- **API Framework:** FastAPI + Uvicorn
- **External APIs:** Polygon.io (stock data), Anthropic (AI)

## Prerequisites

1. **Anthropic API Key** - Get from [anthropic.com](https://console.anthropic.com/)
2. **Polygon API Key** - Get from [polygon.io](https://polygon.io/) (free tier available)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/nageshbalivada/code.gamestocks.git
cd code.gamestocks

# Create virtual environment
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env_template .env
# Edit .env and add your API keys:
# - POLYGON_API_KEY=your_polygon_key
# - ANTHROPIC_API_KEY=your_anthropic_key
```

### 3. Start MCP Server

```bash
cd stocks-mcp-server
uvicorn main:app --reload --port 8080
```

### 4. Verify Server (optional)

```bash
curl -X POST http://localhost:8080/tools/get_stock_price \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AAPL"}'
```

### 5. Run Agent

Open a new terminal:

```bash
cd stocks-agent
python polygon_anthopic_agent.py
```

### 6. Ask Questions

```
Ask a stock-related question:
> What is the stock price of Elon Musk's company?
```

## WebSocket Streaming (Optional)

Stream real-time market data using Polygon WebSocket API:

```bash
cd stocks-polygon-ws-stream

# Stream per-minute aggregates
python aggregates_min.py

# Stream per-second aggregates
python aggregates_sec.py

# Stream real-time quotes
python quotes.py

# Stream real-time trades
python trades.py
```

**Note:** Streaming uses delayed feed (free tier compatible). Stop with Ctrl+C.

## Project Structure

```
gamestocks/
├── stocks-agent/
│   └── polygon_anthopic_agent.py   # Claude AI agent
├── stocks-mcp-server/
│   ├── main.py                     # FastAPI server
│   ├── mcp.yaml                    # Tool definitions
│   └── polygon_api_signatures.py   # API templates
├── stocks-polygon-ws-stream/
│   ├── aggregates_min.py           # Minute bar streaming
│   ├── aggregates_sec.py           # Second bar streaming
│   ├── quotes.py                   # Quote streaming
│   └── trades.py                   # Trade streaming
├── .env_template                   # Environment template
├── requirements.txt                # Python dependencies
├── REQUIREMENTS.md                 # Detailed requirements doc
└── README.md                       # This file
```

## Limitations

1. **Polygon Free Tier:** Only `get_ticker_price` is confirmed working on free tier. Other tools may require a paid subscription.
2. **Single Question Mode:** Agent processes one question per execution. No conversation history maintained.
3. **WebSocket Streams:** Currently output raw messages without persistence or processing.

## Documentation

See [REQUIREMENTS.md](REQUIREMENTS.md) for comprehensive technical requirements including:
- 88+ numbered requirements
- Full implementation logic for each component
- Data models and API specifications
- Error handling and security requirements

## Future Enhancements

- [ ] Enable follow-up questions with conversation context
- [ ] Add message persistence for WebSocket streams
- [ ] Integrate streaming with MCP server for real-time tools
- [ ] Add support for options, crypto, and forex data

## License

MIT
