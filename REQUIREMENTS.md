# GameStocks - Comprehensive Requirements Document

## Document Overview
**Project Name:** GameStocks
**Version:** 0.1
**Last Updated:** 2025-12-30
**Purpose:** Stock price query system using AI agent with MCP (Model Context Protocol) server integration

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Requirements](#architecture-requirements)
3. [Component Requirements](#component-requirements)
4. [API Integration Requirements](#api-integration-requirements)
5. [Data Requirements](#data-requirements)
6. [Security Requirements](#security-requirements)
7. [Operational Requirements](#operational-requirements)

---

## System Overview

### Purpose
The GameStocks system provides a conversational AI interface for querying real-time stock market data through natural language questions. It consists of two main components:
1. An AI Agent that processes user questions using Anthropic's Claude
2. An MCP Server that interfaces with Polygon.io stock data API

### Technology Stack
- **Language:** Python 3.13+
- **AI Model:** Anthropic Claude Sonnet 4 (claude-sonnet-4-20250514)
- **API Framework:** FastAPI
- **HTTP Server:** Uvicorn
- **External APIs:**
  - Polygon.io (stock market data)
  - Anthropic API (AI processing)
  - OpenAI API (configured but not actively used)

---

## Architecture Requirements

### REQ-ARCH-001: Two-Component Architecture
**Description:** The system must implement a decoupled architecture with two independent components:
- **stocks-agent/**: AI agent for natural language processing
- **stocks-mcp-server/**: REST API server for stock data retrieval

**Rationale:** Separation of concerns allows independent scaling and development of AI logic and data fetching capabilities.

### REQ-ARCH-002: HTTP-Based Communication
**Description:** The agent must communicate with the MCP server via HTTP REST API calls.
- Base URL: `http://localhost:8080`
- Protocol: JSON over HTTP
- Communication pattern: Synchronous request-response

### REQ-ARCH-003: Tool Discovery Pattern
**Description:** The system must implement a dynamic tool discovery mechanism where:
1. MCP server exposes tool definitions via `/get_tool_defs` endpoint
2. Agent fetches tool definitions at startup
3. Agent converts MCP tool format to Anthropic's tool format
4. Tools can be added/modified without agent code changes

---

## Component Requirements

## 1. MCP Server Component (stocks-mcp-server/)

### REQ-MCP-001: FastAPI Server Initialization
**Description:** The MCP server must:
- Initialize as a FastAPI application
- Run on port 8080
- Support hot-reload in development mode
- Load environment variables from .env file at startup

**Implementation Details:**
```python
from fastapi import FastAPI
app = FastAPI()
# Run with: uvicorn main:app --reload --port 8080
```

### REQ-MCP-002: Tool Definition Storage
**Description:** Tool definitions must be stored in a YAML configuration file (`mcp.yaml`) with the following structure:
- **schema_version:** Version of the schema format
- **id:** Unique identifier for the tool collection
- **name:** Human-readable name
- **description:** Overall purpose description
- **version:** Tool collection version
- **tools:** Array of tool definitions

**Tool Definition Schema:**
Each tool must contain:
- **id:** Unique tool identifier (e.g., "get_ticker_price")
- **description:** What the tool does
- **input_schema:** JSON Schema for input parameters
- **output_schema:** JSON Schema for output format

### REQ-MCP-003: Tool Definition Endpoint
**Description:** Must expose a GET endpoint at `/get_tool_defs` that:
- Reads and parses mcp.yaml file
- Returns complete tool definitions as JSON
- Logs successful load with tool count
- Returns 500 error with details if file cannot be loaded

### REQ-MCP-004: Polygon API Integration
**Description:** The server must maintain API endpoint templates in `polygon_api_signatures.py`:
- Templates use Python string formatting with placeholders: `{ticker}`, `{api_key}`, etc.
- Each template corresponds to a Polygon.io REST API endpoint
- API key is injected at runtime from environment variables

**API Templates Required:**
```python
get_ticker_price_api = "https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey={api_key}"
get_ticker_details_api = "https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={api_key}"
get_last_trade_api = "https://api.polygon.io/v2/last/trade/{ticker}?apiKey={api_key}"
get_last_quote_api = "https://api.polygon.io/v2/last/nbbo/{ticker}?apiKey={api_key}"
get_aggregates_api = "https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}?adjusted=true&sort=desc&limit={limit}&apiKey={api_key}"
get_historic_trades_api = "https://api.polygon.io/v2/ticks/stocks/trades/{ticker}/{date}?apiKey={api_key}&limit={limit}&timestamp={timestamp}"
```

### REQ-MCP-005: Request Models
**Description:** Must define Pydantic models for validating incoming requests:

**StockRequest:**
- ticker (str): Stock ticker symbol

**TickerDetailsRequest:**
- ticker (str): Stock ticker symbol

**LastTradeRequest:**
- ticker (str): Stock ticker symbol

**LastQuoteRequest:**
- ticker (str): Stock ticker symbol

**AggregatesRequest:**
- ticker (str): Stock ticker symbol
- multiplier (int): Time multiplier
- timespan (str): Time unit (minute, hour, day, week, month, quarter, year)
- from_date (str): Start date in YYYY-MM-DD format
- to_date (str): End date in YYYY-MM-DD format
- limit (int): Maximum number of results

**HistoricTradesRequest:**
- ticker (str): Stock ticker symbol
- date (str): Date in YYYY-MM-DD format
- limit (int): Maximum number of trades
- timestamp (int): Unix timestamp in milliseconds

### REQ-MCP-006: Tool Endpoint - Get Ticker Price
**Description:** POST endpoint at `/tools/get_ticker_price`

**Logic:**
1. Accept StockRequest with ticker symbol
2. Convert ticker to uppercase
3. Format Polygon API URL with ticker and API key
4. Make HTTP GET request to Polygon API
5. Handle HTTP errors by calling raise_polygon_error()
6. Extract price from `results[0]["c"]` (closing price)
7. Extract timestamp from `results[0]["t"]`
8. Return JSON: `{"ticker": str, "price": float, "timestamp": int}`
9. Log request, API call, response status, and result

### REQ-MCP-007: Tool Endpoint - Get Ticker Details
**Description:** POST endpoint at `/tools/get_ticker_details`

**Logic:**
1. Accept TickerDetailsRequest with ticker symbol
2. Convert ticker to uppercase
3. Call Polygon reference data API
4. Extract from response.results:
   - name: Company name
   - primary_exchange: Primary exchange
   - locale: Geographic locale
   - market: Market type
   - type: Security type
5. Return JSON with extracted fields
6. Log request and response details

### REQ-MCP-008: Tool Endpoint - Get Last Trade
**Description:** POST endpoint at `/tools/get_last_trade`

**Logic:**
1. Accept LastTradeRequest with ticker
2. Call Polygon last trade API
3. Extract from response.results:
   - p: Trade price
   - s: Trade size (number of shares)
   - t: Trade timestamp
4. Return: `{"price": float, "size": int, "timestamp": int}`

### REQ-MCP-009: Tool Endpoint - Get Last Quote
**Description:** POST endpoint at `/tools/get_last_quote`

**Logic:**
1. Accept LastQuoteRequest with ticker
2. Call Polygon NBBO (National Best Bid and Offer) API
3. Extract from response.results:
   - ap: Ask price
   - as: Ask size
   - bp: Bid price
   - bs: Bid size
   - t: Timestamp
4. Return: `{"askprice": float, "asksize": int, "bidprice": float, "bidsize": int, "timestamp": int}`

### REQ-MCP-010: Tool Endpoint - Get Aggregates
**Description:** POST endpoint at `/tools/get_aggregates`

**Logic:**
1. Accept AggregatesRequest with ticker, timespan, date range
2. Format URL with all parameters
3. Call Polygon aggregates API
4. Extract results array containing OHLCV data:
   - o: Open price
   - h: High price
   - l: Low price
   - c: Close price
   - v: Volume
   - t: Timestamp
5. Return: `{"results": [array of OHLCV objects]}`
6. Log count of aggregates returned

### REQ-MCP-011: Tool Endpoint - Get Historic Trades
**Description:** POST endpoint at `/tools/get_historic_trades`

**Logic:**
1. Accept HistoricTradesRequest with ticker, date, limit, timestamp
2. Call Polygon historic trades API
3. Extract results array of trade ticks:
   - p: Price
   - s: Size
   - t: Timestamp
4. Return: `{"results": [array of trade objects]}`
5. Log count of trades returned

### REQ-MCP-012: Error Handling
**Description:** Implement `raise_polygon_error()` function that:
1. Accepts requests.Response object and tool_name
2. Attempts to parse response as JSON, falls back to text
3. Logs error with tool name, status code, and detail
4. Raises HTTPException with status 400 and error details

### REQ-MCP-013: Logging Configuration
**Description:** The MCP server must implement structured logging:
- Log level: INFO when MCP_SERVER_LOG_ENABLED=true, WARNING otherwise
- Format: `"%(asctime)s [%(levelname)s] %(message)s"`
- Date format: `"%Y-%m-%d %H:%M:%S"`
- Log startup status including Polygon API key presence
- Log each incoming request with tool name and parameters
- Log each Polygon API call and response status
- Log each successful response with key data points
- Prefix all logs with `[{tool_name}]` for tool-specific operations

### REQ-MCP-014: Environment Variable Configuration
**Description:** Must load from .env file:
- POLYGON_API_KEY: Required for Polygon API authentication
- MCP_SERVER_LOG_ENABLED: Optional, defaults to "true"

---

## 2. Agent Component (stocks-agent/)

### REQ-AGENT-001: Anthropic Client Initialization
**Description:** The agent must:
- Initialize Anthropic client with API key from environment
- Configure MCP base URL (default: http://localhost:8080)
- Set default model: claude-sonnet-4-20250514
- Fetch tool definitions from MCP server at startup
- Exit with error if tool definitions cannot be loaded

### REQ-AGENT-002: Tool Definition Conversion
**Description:** Implement `convert_to_anthropic_tools()` function that:
1. Accepts dictionary of MCP tool definitions
2. Converts each to Anthropic tool format:
   ```python
   {
       "name": tool_id,
       "description": tool["description"],
       "input_schema": tool["input_schema"]
   }
   ```
3. Returns list of converted tool definitions

### REQ-AGENT-003: MCP Tool Invocation
**Description:** Implement `call_mcp_tool()` function that:
1. Accepts tool_id (string) and args (dict)
2. Constructs URL: `{MCP_BASE_URL}/tools/{tool_id}`
3. Makes POST request with JSON body containing args
4. Logs request URL and parameters
5. Handles HTTP errors by extracting error detail (JSON or text)
6. Raises RuntimeError with tool name and error detail on failure
7. Returns parsed JSON response on success
8. Logs successful response

### REQ-AGENT-004: Timestamp Utilities
**Description:** Implement utility functions:

**current_epoch_ms(timezone_str="UTC"):**
- Returns current time as epoch milliseconds in specified timezone
- Uses ZoneInfo for timezone handling

**datetime_from_epochts(epoch_ts_ms, timezone_str):**
- Converts epoch milliseconds to datetime object
- Converts from UTC to specified timezone
- Returns timezone-aware datetime

### REQ-AGENT-005: Response Formatting
**Description:** Implement `formatted_tool_response()` that formats tool results for human readability:

**For get_stock_price:**
- Format: "Ticker: {TICKER}, Price: ${PRICE}, Time: {YYYY-MM-DD HH:MM:SS TZ}"
- Timezone: America/Los_Angeles

**For get_ticker_details:**
- Format: "{NAME} ({TYPE} on {EXCHANGE}) - Market: {MARKET}, Locale: {LOCALE}"

**For get_last_trade:**
- Format: "Last trade: ${PRICE} (Size: {SIZE}) at {YYYY-MM-DD HH:MM:SS TZ}"

**For get_last_quote:**
- Format: "Bid: ${BIDPRICE} ({BIDSIZE}), Ask: ${ASKPRICE} ({ASKSIZE}), Time: {YYYY-MM-DD HH:MM:SS TZ}"

**For get_aggregates:**
- Format: "OHLC: {O}, {H}, {L}, {C} - Volume: {V}"
- Uses first result from array

**For get_historic_trades:**
- Format: "Trade: Price ${PRICE}, Size {SIZE} at {YYYY-MM-DD HH:MM:SS TZ}"
- Uses first result from array

**For unknown tools:**
- Return JSON.dumps(result)

**Error handling:**
- Catch formatting exceptions, log warning, return JSON dump as fallback

### REQ-AGENT-006: Agent Execution Loop
**Description:** Implement `run_agent(user_question)` function with the following logic:

**Initialization Phase:**
1. Log separator line and start message
2. Log user question
3. Convert MCP tools to Anthropic format
4. Initialize messages array with user question
5. Define system prompt for financial assistant role

**System Prompt:**
```
You are a financial assistant with access to stock data tools.
When the user asks about stock prices or financial data, use the available tools to fetch real-time information.
Always provide clear, helpful responses based on the data you retrieve.
```

**First Request:**
1. Call client.messages.create() with:
   - model: MODEL constant
   - max_tokens: 1024
   - system: system prompt
   - tools: converted tool list
   - messages: message array
2. Log model name and response stop_reason

**Tool Use Loop:**
1. While response.stop_reason == "tool_use":
   - Increment iteration counter
   - Extract all tool_use blocks from response.content
   - Log iteration number and tool count
   - Add assistant's response to messages
   - Initialize empty tool_results array

   For each tool use block:
   - Extract tool_name, tool_input, tool_use_id
   - Log tool name and parameters
   - Try:
     - Call call_mcp_tool(tool_name, tool_input)
     - Format result using formatted_tool_response()
     - Log formatted result
     - Append to tool_results: `{"type": "tool_result", "tool_use_id": id, "content": json.dumps(result)}`
   - Catch exceptions:
     - Log error
     - Append error result: `{"type": "tool_result", "tool_use_id": id, "content": "Error: {error}", "is_error": True}`

   - Add tool_results to messages with role="user"
   - Log sending results back to Claude
   - Call client.messages.create() again with updated messages
   - Log new stop_reason

**Finalization:**
1. Extract final text from response.content blocks with text attribute
2. Log completion with iteration count
3. Print response to console
4. Return final text

### REQ-AGENT-007: Main Entry Point
**Description:** The main block must:
1. Prompt user: "Ask a stock-related question:\n> "
2. Read user input
3. Call run_agent() with user question

### REQ-AGENT-008: Logging Configuration
**Description:** The agent must implement structured logging:
- Log level: INFO when AGENT_LOG_ENABLED=true, WARNING otherwise
- Format: `"%(asctime)s [%(levelname)s] %(message)s"`
- Date format: `"%Y-%m-%d %H:%M:%S"`
- Log initialization status
- Log MCP server connection and tool count
- Log each phase of agent execution with separators
- Log all Claude API interactions
- Log all tool invocations and results

### REQ-AGENT-009: Environment Variable Configuration
**Description:** Must load from .env file:
- ANTHROPIC_API_KEY: Required for Claude API
- AGENT_LOG_ENABLED: Optional, defaults to "true"

---

## 3. WebSocket Streaming Component (stocks-polygon-ws-stream/)

### REQ-WS-001: Component Overview
**Description:** Real-time streaming component using Polygon.io WebSocket API.
- **Status:** Restored and functional
- **Purpose:** Stream real-time market data (trades, quotes, aggregates)
- **Feed Type:** Delayed feed (suitable for free tier)
- **Market:** US Stocks

**Files:**
- `aggregates_min.py` - Per-minute aggregate bars
- `aggregates_sec.py` - Per-second aggregate bars
- `quotes.py` - Real-time bid/ask quotes
- `trades.py` - Real-time trade ticks

### REQ-WS-002: Environment Configuration
**Description:** All WebSocket scripts must load API credentials from environment:

**Implementation:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("POLYGON_API_KEY")
```

**Required Environment Variable:**
- POLYGON_API_KEY: Polygon.io API key (loaded from .env file)

### REQ-WS-003: WebSocket Client Initialization
**Description:** Each streaming script must initialize the Polygon WebSocket client:

**Implementation:**
```python
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, Feed, Market

client = WebSocketClient(
    api_key=os.getenv("POLYGON_API_KEY"),
    feed=Feed.Delayed,
    market=Market.Stocks
)
```

**Parameters:**
- **api_key:** Loaded from environment variable
- **feed:** Feed.Delayed (free tier compatible)
- **market:** Market.Stocks (US equities)

### REQ-WS-004: Minute Aggregates Stream
**File:** `aggregates_min.py`

**Description:** Stream per-minute OHLCV aggregate bars.

**Subscription Pattern:** `AM.*` (Aggregate Minute)

**Subscription Options:**
```python
client.subscribe("AM.*")           # All tickers
client.subscribe("AM.AAPL")        # Single ticker
client.subscribe("AM.AAPL", "AM.MSFT")  # Multiple tickers
```

**Message Handler Logic:**
1. Receive list of WebSocketMessage objects
2. Iterate through each message
3. Process/print aggregate data (open, high, low, close, volume)

**Data Fields Expected:**
- sym: Ticker symbol
- o: Open price
- h: High price
- l: Low price
- c: Close price
- v: Volume
- s: Start timestamp
- e: End timestamp

### REQ-WS-005: Second Aggregates Stream
**File:** `aggregates_sec.py`

**Description:** Stream per-second OHLCV aggregate bars.

**Subscription Pattern:** `A.*` (Aggregate Second)

**Subscription Options:**
```python
client.subscribe("A.*")            # All tickers
client.subscribe("A.AAPL")         # Single ticker
client.subscribe("A.AAPL", "A.MSFT")   # Multiple tickers
```

**Use Case:** High-frequency data for intraday analysis, more granular than minute bars.

### REQ-WS-006: Real-Time Quotes Stream
**File:** `quotes.py`

**Description:** Stream real-time National Best Bid and Offer (NBBO) quotes.

**Subscription Pattern:** `Q.*` (Quotes)

**Subscription Options:**
```python
client.subscribe("Q.*")            # All quotes
client.subscribe("Q.TSLA")         # Single ticker
client.subscribe("Q.TSLA", "Q.UBER")   # Multiple tickers
```

**Data Fields Expected:**
- sym: Ticker symbol
- bp: Bid price
- bs: Bid size
- ap: Ask price
- as: Ask size
- t: Timestamp

### REQ-WS-007: Real-Time Trades Stream
**File:** `trades.py`

**Description:** Stream real-time trade executions.

**Subscription Pattern:** `T.*` (Trades)

**Subscription Options:**
```python
client.subscribe("T.*")            # All trades
client.subscribe("T.TSLA")         # Single ticker
client.subscribe("T.TSLA", "T.UBER")   # Multiple tickers
```

**Data Fields Expected:**
- sym: Ticker symbol
- p: Trade price
- s: Trade size (shares)
- t: Timestamp
- c: Trade conditions
- x: Exchange ID

### REQ-WS-008: Message Handler Pattern
**Description:** All streaming scripts use a common callback pattern:

**Implementation:**
```python
from typing import List

def handle_msg(msgs: List[WebSocketMessage]):
    for m in msgs:
        print(m)

client.run(handle_msg)
```

**Logic:**
1. `client.run()` starts the WebSocket connection
2. Incoming messages trigger `handle_msg` callback
3. Messages arrive in batches (List)
4. Current implementation prints raw messages
5. Runs continuously until interrupted (Ctrl+C)

### REQ-WS-009: Streaming Startup
**Description:** To run any WebSocket stream:

**Steps:**
1. Ensure `.env` file contains valid POLYGON_API_KEY
2. Navigate to `stocks-polygon-ws-stream/` directory
3. Run desired script: `python trades.py`
4. Stream runs continuously, printing messages
5. Stop with Ctrl+C

**Example:**
```bash
cd stocks-polygon-ws-stream
python aggregates_min.py  # Stream minute bars
python trades.py          # Stream trades
```

### REQ-WS-010: Dependencies
**Description:** WebSocket component requires:
- `polygon-api-client` - Polygon.io Python client with WebSocket support
- `python-dotenv` - Environment variable loading

**Note:** Add to requirements.txt if not present:
```
polygon-api-client
```

### REQ-WS-011: Known Limitations
**Description:** Current WebSocket implementation limitations:
- **No persistence:** Messages are printed but not stored
- **No processing:** Raw message output only
- **No error handling:** Connection drops not handled gracefully
- **No reconnection:** Manual restart required on disconnect
- **Single stream:** Each script handles one data type
- **No integration:** Not connected to MCP server or agent

### REQ-WS-012: Future Enhancement Opportunities
**Description:** Potential improvements for WebSocket component:
1. Add message persistence (database, file, message queue)
2. Implement error handling and automatic reconnection
3. Create unified streaming service with multiple subscriptions
4. Integrate with MCP server for real-time tool responses
5. Add configurable ticker lists via environment or config file
6. Implement message filtering and transformation
7. Add logging with configurable verbosity

---

## API Integration Requirements

### REQ-API-001: Polygon.io REST API
**Description:** The system integrates with Polygon.io REST API v2 and v3:

**Authentication:**
- API key passed as query parameter: `?apiKey={key}`
- Key stored in environment variable POLYGON_API_KEY

**Rate Limiting:**
- Free tier: Limited to specific endpoints
- get_ticker_price endpoint confirmed as free tier
- Other endpoints may require paid subscription

**Endpoints Used:**
1. Previous Close (Aggregates): `/v2/aggs/ticker/{ticker}/prev`
2. Ticker Details: `/v3/reference/tickers/{ticker}`
3. Last Trade: `/v2/last/trade/{ticker}`
4. Last Quote (NBBO): `/v2/last/nbbo/{ticker}`
5. Aggregates: `/v2/aggs/ticker/{ticker}/range/{mult}/{timespan}/{from}/{to}`
6. Historic Trades: `/v2/ticks/stocks/trades/{ticker}/{date}`

### REQ-API-002: Anthropic Messages API
**Description:** Integration with Anthropic's Messages API:

**Model:** claude-sonnet-4-20250514

**Features Used:**
- Tool use capability
- System prompts
- Multi-turn conversations
- Streaming not used (standard request-response)

**Request Parameters:**
- model: String model identifier
- max_tokens: 1024
- system: String system prompt
- tools: Array of tool definitions
- messages: Array of message objects (role + content)

**Response Handling:**
- Extract stop_reason to determine if tools needed
- Parse content blocks for text and tool_use
- Handle tool_use blocks by ID

### REQ-API-003: OpenAI API
**Description:** OpenAI SDK is installed but not actively used:
- OPENAI_API_KEY configured in environment
- No active integration in current code
- May be intended for future features

---

## Data Requirements

### REQ-DATA-001: Stock Price Data
**Description:** Stock price data must include:
- Ticker symbol (uppercase, e.g., "AAPL", "TSLA")
- Price (float, USD)
- Timestamp (Unix epoch milliseconds)
- Source: Polygon previous day closing price

### REQ-DATA-002: Company Metadata
**Description:** Company details must include:
- Company name (string)
- Primary exchange (string, e.g., "NASDAQ")
- Locale (string, e.g., "us")
- Market type (string, e.g., "stocks")
- Security type (string, e.g., "CS" for common stock)

### REQ-DATA-003: Trade Data
**Description:** Individual trade data must include:
- Price (float)
- Size (integer, number of shares)
- Timestamp (Unix epoch milliseconds)

### REQ-DATA-004: Quote Data (NBBO)
**Description:** Quote data must include:
- Ask price (float)
- Ask size (integer)
- Bid price (float)
- Bid size (integer)
- Timestamp (Unix epoch milliseconds)

### REQ-DATA-005: Aggregate (OHLCV) Data
**Description:** Aggregate bars must include:
- Open price (o: float)
- High price (h: float)
- Low price (l: float)
- Close price (c: float)
- Volume (v: integer)
- Timestamp (t: Unix epoch milliseconds)

**Timespan Support:**
- minute, hour, day, week, month, quarter, year
- Multiplier to create N-unit bars

### REQ-DATA-006: Timestamp Handling
**Description:** All timestamps must:
- Be stored as Unix epoch milliseconds (integer)
- Be converted to datetime objects for display
- Default display timezone: America/Los_Angeles (Pacific Time)
- Format for display: "YYYY-MM-DD HH:MM:SS TZ"

---

## Security Requirements

### REQ-SEC-001: API Key Management
**Description:** All API keys must:
- Be stored in .env file (not committed to git)
- Be loaded via python-dotenv
- Never be hardcoded in source files
- Be validated for presence at startup

**Required Keys:**
- POLYGON_API_KEY
- ANTHROPIC_API_KEY
- OPENAI_API_KEY (optional)

### REQ-SEC-002: Environment Template
**Description:** Provide .env_template file with:
- Empty placeholders for all required keys
- Comments explaining each variable
- Log configuration options

**Template Format:**
```
POLYGON_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Logging configuration (set to "false" to disable logs)
AGENT_LOG_ENABLED=true
MCP_SERVER_LOG_ENABLED=true
```

### REQ-SEC-003: Git Security
**Description:** Repository must:
- Include .env in .gitignore
- Never commit actual API keys
- Provide .env_template for setup guidance

### REQ-SEC-004: Input Validation
**Description:** All user inputs must:
- Be validated by Pydantic models
- Have ticker symbols converted to uppercase
- Be sanitized before API calls

---

## Operational Requirements

### REQ-OPS-001: Python Environment Setup
**Description:** The system requires:
- Python 3.13 or higher
- Virtual environment (recommended name: myenv)
- Dependencies installed via requirements.txt

**Dependencies:**
```
fastapi
uvicorn
pydantic
python-dotenv
requests
PyYAML
anthropic
openai
```

### REQ-OPS-002: MCP Server Startup
**Description:** To run the MCP server:
1. Navigate to stocks-mcp-server directory
2. Execute: `uvicorn main:app --reload --port 8080`
3. Server must bind to localhost:8080
4. Reload mode enabled for development

### REQ-OPS-003: MCP Server Health Check
**Description:** Verify server is running with:
```bash
curl -X POST http://localhost:8080/tools/get_stock_price \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AMZN"}'
```

Expected: JSON response with ticker, price, timestamp

### REQ-OPS-004: Agent Startup
**Description:** To run the agent:
1. Open new terminal (MCP server must be running)
2. Navigate to stocks-agent directory
3. Execute: `python polygon_anthopic_agent.py`
4. Agent will initialize and prompt for question

### REQ-OPS-005: End-to-End Testing
**Description:** Verify full system with test question:
- Input: "What is the stock price of Elon Musk's company?"
- Expected: Agent identifies TSLA ticker, fetches price, returns formatted response

### REQ-OPS-006: Log File Management
**Description:** The system creates log directories:
- stocks-agent/logs/
- stocks-mcp-server/logs/

**Note:** Current implementation logs to console, not files. Directory structure exists for future enhancement.

### REQ-OPS-007: Error Reporting
**Description:** The system must provide clear error messages for:
- Missing environment variables
- Failed API connections
- Invalid API keys
- Polygon API errors (with status codes)
- Tool execution failures

### REQ-OPS-008: Development Workflow
**Description:** Standard development workflow:
1. Clone repository
2. Create and activate virtual environment
3. Copy .env_template to .env
4. Fill in API keys
5. Install dependencies: `pip install -r requirements.txt`
6. Start MCP server in one terminal
7. Start agent in another terminal
8. Test with sample questions

---

## Limitations and Known Issues

### REQ-LIMIT-001: WebSocket Streaming
**Description:** WebSocket streaming component is non-functional:
- Code exists in git history but is deleted
- Hardcoded API keys in original code
- No integration with MCP server or agent
- Not part of current system functionality

### REQ-LIMIT-002: API Tier Restrictions
**Description:** Polygon.io API limitations:
- Free tier: Only get_ticker_price confirmed working
- Other endpoints require paid subscription
- Rate limits apply based on subscription tier

### REQ-LIMIT-003: Single Question Mode
**Description:** Current agent implementation:
- Processes one question per execution
- No conversation history maintained
- No follow-up question capability
- README mentions planned enhancement: "Enable follow up questions by adding a loop & context"

### REQ-LIMIT-004: Tool Availability
**Description:** Only 6 tools currently implemented:
- get_ticker_price (confirmed free)
- get_ticker_details
- get_last_trade
- get_last_quote
- get_aggregates
- get_historic_trades

No support for:
- Options data
- Crypto data
- Forex data
- Technical indicators
- News/sentiment data

### REQ-LIMIT-005: Timezone Handling
**Description:** All display timestamps hardcoded to Pacific Time:
- No user preference for timezone
- No automatic detection of user timezone
- Could cause confusion for users in other timezones

---

## Future Enhancements (from README Timeline)

### REQ-FUTURE-001: Agent Code Understanding
**Date:** 7.28 (July 28, 2025)
**Description:** Fully understand and document agent code architecture

### REQ-FUTURE-002: MCP Server Understanding
**Date:** 7.28
**Description:** Fully understand and document MCP server architecture

### REQ-FUTURE-003: Conversation Loop
**Date:** 7.28
**Description:** Enable follow-up questions by:
- Adding conversation loop to agent
- Maintaining context between questions
- Supporting multi-turn conversations

---

## System Integration Flow

### REQ-FLOW-001: Startup Sequence
1. User activates Python virtual environment
2. User starts MCP server (uvicorn on port 8080)
3. MCP server loads tool definitions from mcp.yaml
4. MCP server confirms Polygon API key configured
5. User starts agent in separate terminal
6. Agent loads environment variables
7. Agent fetches tool definitions from MCP server
8. Agent converts tools to Anthropic format
9. Agent prompts user for question

### REQ-FLOW-002: Query Processing Flow
1. User enters natural language question
2. Agent sends question to Claude with tool definitions
3. Claude analyzes question and identifies needed tools
4. Claude returns tool_use blocks
5. Agent extracts tool name and parameters
6. Agent calls MCP server endpoint
7. MCP server validates request
8. MCP server calls Polygon API
9. Polygon returns data
10. MCP server formats response
11. MCP server returns JSON to agent
12. Agent formats data for readability
13. Agent sends tool results back to Claude
14. Claude formulates final answer
15. Agent prints response to user

### REQ-FLOW-003: Error Flow
1. Error occurs at any step
2. Component logs error with context
3. Error propagates to caller with details
4. Agent receives error result
5. Agent sends error to Claude as tool result
6. Claude acknowledges limitation and informs user
7. Agent displays Claude's error message

---

## Configuration Requirements

### REQ-CONFIG-001: Environment Variables
**Required:**
- POLYGON_API_KEY: String, obtained from polygon.io
- ANTHROPIC_API_KEY: String, obtained from anthropic.com

**Optional:**
- OPENAI_API_KEY: String, for future use
- AGENT_LOG_ENABLED: Boolean string ("true"/"false"), default "true"
- MCP_SERVER_LOG_ENABLED: Boolean string ("true"/"false"), default "true"

### REQ-CONFIG-002: Tool Definition Schema
**Description:** mcp.yaml must conform to schema:
```yaml
schema_version: "v1"
id: string
name: string
description: string
version: string
tools:
  - id: string (unique)
    description: string
    input_schema:
      type: object
      properties: {field_definitions}
      required: [field_list]
    output_schema:
      type: object
      properties: {field_definitions}
```

### REQ-CONFIG-003: Server Configuration
**MCP Server:**
- Host: localhost
- Port: 8080
- Reload: Enabled in development
- CORS: Not configured (same-origin only)

**Agent:**
- MCP Base URL: http://localhost:8080
- Model: claude-sonnet-4-20250514
- Max Tokens: 1024
- Temperature: Not specified (uses Claude default)

---

## Testing Requirements

### REQ-TEST-001: Unit Testing
**Description:** While no test files exist, the following should be testable:
- Tool definition parsing from YAML
- Tool format conversion (MCP to Anthropic)
- Response formatting functions
- Timestamp conversion utilities
- Error handling logic

### REQ-TEST-002: Integration Testing
**Description:** Test points for integration:
- Agent to MCP server communication
- MCP server to Polygon API communication
- Tool discovery and registration
- End-to-end query flow

### REQ-TEST-003: Manual Testing Scenarios
**Description:** Recommended test cases:
1. "What is the price of AAPL?" - Simple ticker query
2. "What is the stock price of Elon Musk's company?" - Entity resolution
3. Invalid ticker - Error handling
4. Multiple stock question - Multi-tool use
5. Historical data question - Date range handling

---

## Dependencies and External Systems

### REQ-DEP-001: Python Package Dependencies
**Production:**
- fastapi: Web framework for MCP server
- uvicorn: ASGI server
- pydantic: Data validation
- python-dotenv: Environment variable management
- requests: HTTP client
- PyYAML: YAML parsing
- anthropic: Claude API client
- openai: OpenAI client (unused)

**Development:**
- None specified (should add: pytest, black, mypy, etc.)

### REQ-DEP-002: External Service Dependencies
**Critical Path:**
- Polygon.io API: Stock market data source
- Anthropic API: AI model provider

**Optional:**
- OpenAI API: Not currently used

**Network Requirements:**
- Outbound HTTPS to api.polygon.io
- Outbound HTTPS to api.anthropic.com
- Localhost HTTP between agent and MCP server

### REQ-DEP-003: System Dependencies
**Required:**
- Python 3.13+
- Internet connection
- Terminal/shell access

**Operating System:**
- Tested on macOS (based on README)
- Should work on Linux and Windows with Python 3.13+

---

## Data Models

### REQ-MODEL-001: MCP Tool Definition Model
```yaml
Tool:
  id: string
  description: string
  input_schema: JSONSchema
  output_schema: JSONSchema
```

### REQ-MODEL-002: Anthropic Message Model
```python
Message:
  role: "user" | "assistant"
  content: string | list[ContentBlock]

ContentBlock:
  type: "text" | "tool_use" | "tool_result"
  # type-specific fields
```

### REQ-MODEL-003: Tool Use Model
```python
ToolUse:
  type: "tool_use"
  id: string
  name: string
  input: dict
```

### REQ-MODEL-004: Tool Result Model
```python
ToolResult:
  type: "tool_result"
  tool_use_id: string
  content: string
  is_error: boolean (optional)
```

---

## Performance Requirements

### REQ-PERF-001: Response Time
**Description:** Target response times:
- MCP server tool endpoint: < 2 seconds (depends on Polygon API)
- Agent to MCP server: < 100ms overhead
- Total user query response: < 5 seconds for single tool use

### REQ-PERF-002: Concurrency
**Description:** Current implementation:
- MCP server: Single-threaded (FastAPI default)
- Agent: Synchronous single query at a time
- No support for concurrent users

**Note:** FastAPI supports async but not used in current implementation

### REQ-PERF-003: Resource Usage
**Description:** Expected resource usage:
- Memory: < 200MB per component
- CPU: Minimal (IO-bound operations)
- Network: Dependent on query frequency

---

## Maintainability Requirements

### REQ-MAINT-001: Code Structure
**Description:** Code must maintain:
- Clear separation of concerns (agent vs server)
- Modular function design
- Descriptive variable and function names
- No hardcoded values (use constants or env vars)

### REQ-MAINT-002: Logging Standards
**Description:** All components must:
- Use Python logging module
- Include timestamps in logs
- Log at appropriate levels (INFO, WARNING, ERROR)
- Include contextual information (tool names, ticker symbols)
- Be configurable via environment variables

### REQ-MAINT-003: Documentation
**Description:** Repository must maintain:
- README with setup instructions
- .env_template for configuration
- Requirements document (this file)
- Inline comments for complex logic
- Function docstrings (currently minimal)

---

## Compliance and Standards

### REQ-COMP-001: API Rate Limiting
**Description:** Must respect Polygon.io rate limits:
- Free tier: 5 API calls per minute
- Implementation: No rate limiting currently implemented
- Risk: Could exceed quota and cause errors

### REQ-COMP-002: Data Usage
**Description:** Stock data usage must comply with:
- Polygon.io Terms of Service
- Market data redistribution restrictions
- No storage of historical data (real-time queries only)

### REQ-COMP-003: AI Model Usage
**Description:** Must comply with Anthropic's:
- Acceptable Use Policy
- API usage guidelines
- No sensitive data in prompts

---

## Deployment Requirements

### REQ-DEPLOY-001: Local Development
**Description:** System is designed for local development:
- No production deployment configuration
- Uses localhost for all inter-component communication
- No containerization (Docker) provided

### REQ-DEPLOY-002: Prerequisites Checklist
**Description:** Before running, must have:
- [ ] Python 3.13+ installed
- [ ] Polygon.io API key obtained
- [ ] Anthropic API key obtained
- [ ] Git repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured

### REQ-DEPLOY-003: Startup Order
**Description:** Components must start in order:
1. MCP Server (required first)
2. Agent (depends on MCP server)

Stopping order:
1. Agent (Ctrl+C)
2. MCP Server (Ctrl+C)

---

## Glossary

**MCP (Model Context Protocol):** Architecture pattern for exposing tools/APIs to AI models in a standardized way.

**Tool:** A function or API endpoint that an AI model can invoke to perform specific tasks.

**Tool Use:** When Claude identifies that it needs to call a tool to answer a user question.

**NBBO (National Best Bid and Offer):** The best available bid and ask prices across all exchanges.

**OHLCV:** Open, High, Low, Close, Volume - standard format for aggregate price data.

**Ticker:** Stock symbol (e.g., AAPL for Apple Inc., TSLA for Tesla Inc.).

**Aggregate:** Price data summarized over a time period (minute, hour, day, etc.).

**Epoch Milliseconds:** Unix timestamp in milliseconds since Jan 1, 1970 00:00:00 UTC.

**Free Tier:** Polygon.io subscription level with limited features.

**WebSocket:** Protocol for real-time bidirectional communication (not currently functional in this project).

---

## Version History

**v0.1 - Initial Implementation**
- Date: July 9, 2025 (First Commit)
- Basic MCP server with 6 tools
- Anthropic agent with single-question mode
- Polygon.io REST API integration

**v0.2 - Documentation Update**
- Date: July 28, 2025
- Updated README with plan
- Added timeline for future enhancements

**v0.3 - Current State**
- Date: December 30, 2025
- Removed non-functional WebSocket component
- Environment template modifications
- This requirements document created

---

## Summary

This requirements document captures the complete functionality of the GameStocks system as implemented in the codebase. The system successfully demonstrates:

1. **AI-Powered Stock Queries:** Natural language interface to stock market data
2. **Modular Architecture:** Separation of AI logic and data fetching
3. **Tool-Based Integration:** Dynamic tool discovery and execution
4. **Real-Time Data:** Live stock prices from Polygon.io
5. **Extensible Design:** Easy to add new tools via YAML configuration

**Core Value Proposition:** Allows users to ask stock-related questions in natural language and receive real-time data without knowing API endpoints or data formats.

**Target Users:** Developers, traders, or analysts who want programmatic access to stock data with conversational interface.

**Key Limitation:** Single-question mode limits usefulness for exploratory analysis (planned for enhancement).

---

**Document End**
