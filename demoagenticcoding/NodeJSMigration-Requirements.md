# GameStocks - Node.js Migration Requirements

## Document Overview

**Project:** GameStocks Python to Node.js Migration
**Target Stack:** TypeScript + Express.js
**Sessions:** 9 coding sessions (~1-2 hours each)
**Source:** Based on REQUIREMENTS.md from Python implementation

---

## Migration Architecture

### Python → Node.js Mapping

| Python Component | Node.js Equivalent |
|-----------------|-------------------|
| FastAPI | Express.js |
| Pydantic | Zod |
| python-dotenv | dotenv |
| requests | axios |
| PyYAML | yaml (js-yaml) |
| anthropic | @anthropic-ai/sdk |
| polygon-api-client | @polygon.io/client-js |
| logging | winston |
| ZoneInfo | date-fns-tz |

### Target Folder Structure

```
gamestocks-nodejs/
├── src/
│   ├── mcp-server/
│   │   ├── index.ts
│   │   ├── config/
│   │   │   └── mcp.yaml
│   │   ├── routes/
│   │   │   ├── toolDefs.ts
│   │   │   └── tools/
│   │   │       ├── index.ts
│   │   │       ├── getTickerPrice.ts
│   │   │       ├── getTickerDetails.ts
│   │   │       ├── getLastTrade.ts
│   │   │       ├── getLastQuote.ts
│   │   │       ├── getAggregates.ts
│   │   │       └── getHistoricTrades.ts
│   │   ├── services/
│   │   │   └── polygonApi.ts
│   │   ├── schemas/
│   │   │   └── requests.ts
│   │   ├── middleware/
│   │   │   ├── errorHandler.ts
│   │   │   └── logger.ts
│   │   └── types/
│   │       └── index.ts
│   ├── agent/
│   │   ├── index.ts
│   │   ├── cli.ts
│   │   ├── core/
│   │   │   └── agentLoop.ts
│   │   ├── services/
│   │   │   ├── anthropicClient.ts
│   │   │   └── mcpClient.ts
│   │   ├── utils/
│   │   │   ├── toolConverter.ts
│   │   │   ├── timestamp.ts
│   │   │   └── responseFormatter.ts
│   │   └── types/
│   │       └── index.ts
│   └── websocket/
│       ├── client.ts
│       ├── streams/
│       │   ├── trades.ts
│       │   ├── quotes.ts
│       │   ├── aggregatesMin.ts
│       │   └── aggregatesSec.ts
│       └── handlers/
│           └── messageHandler.ts
├── src/__tests__/
│   ├── mcp-server/
│   ├── agent/
│   ├── mocks/
│   └── e2e/
├── package.json
├── tsconfig.json
├── jest.config.js
├── .env.template
├── .eslintrc.js
├── .prettierrc
└── README.md
```

---

# SESSION 1: Project Foundation & Setup

## Goal
Initialize the Node.js/TypeScript project with all configuration files and folder structure.

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Code editor (VS Code recommended)

## Requirements

### REQ-NODE-001: Project Initialization
**Description:** Create a new Node.js project with TypeScript support.

**Steps:**
1. Create project directory: `gamestocks-nodejs`
2. Initialize npm: `npm init -y`
3. Install TypeScript and build tools

**Commands:**
```bash
mkdir gamestocks-nodejs
cd gamestocks-nodejs
npm init -y
```

### REQ-NODE-002: TypeScript Configuration
**Description:** Configure TypeScript for Node.js development.

**File:** `tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

### REQ-NODE-003: Package Dependencies
**Description:** Install all required production and development dependencies.

**File:** `package.json` (dependencies section)
```json
{
  "name": "gamestocks-nodejs",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev:server": "tsx watch src/mcp-server/index.ts",
    "dev:agent": "tsx src/agent/index.ts",
    "dev:ws:trades": "tsx src/websocket/streams/trades.ts",
    "dev:ws:quotes": "tsx src/websocket/streams/quotes.ts",
    "build": "tsc",
    "start:server": "node dist/mcp-server/index.js",
    "start:agent": "node dist/agent/index.js",
    "test": "jest",
    "lint": "eslint src --ext .ts",
    "format": "prettier --write src/**/*.ts"
  },
  "dependencies": {
    "express": "^4.18.2",
    "@anthropic-ai/sdk": "^0.24.0",
    "@polygon.io/client-js": "^7.3.2",
    "axios": "^1.6.0",
    "dotenv": "^16.3.1",
    "winston": "^3.11.0",
    "yaml": "^2.3.4",
    "zod": "^3.22.4",
    "date-fns": "^3.0.0",
    "date-fns-tz": "^2.0.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0",
    "tsx": "^4.6.0",
    "@typescript-eslint/eslint-plugin": "^6.13.0",
    "@typescript-eslint/parser": "^6.13.0",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0",
    "jest": "^29.7.0",
    "@types/jest": "^29.5.11",
    "ts-jest": "^29.1.1"
  }
}
```

**Installation Command:**
```bash
npm install express @anthropic-ai/sdk @polygon.io/client-js axios dotenv winston yaml zod date-fns date-fns-tz

npm install -D @types/express @types/node typescript tsx @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint prettier jest @types/jest ts-jest
```

### REQ-NODE-004: Environment Configuration
**Description:** Create environment variable template.

**File:** `.env.template`
```env
# Polygon.io API
POLYGON_API_KEY=

# Anthropic API
ANTHROPIC_API_KEY=

# OpenAI API (optional, for future use)
OPENAI_API_KEY=

# Server Configuration
MCP_SERVER_PORT=8080
MCP_BASE_URL=http://localhost:8080

# Logging
MCP_SERVER_LOG_ENABLED=true
AGENT_LOG_ENABLED=true
LOG_LEVEL=info
```

### REQ-NODE-005: ESLint Configuration
**Description:** Configure ESLint for TypeScript.

**File:** `.eslintrc.js`
```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
  ],
  plugins: ['@typescript-eslint'],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
  env: {
    node: true,
    es2022: true,
  },
  rules: {
    '@typescript-eslint/explicit-function-return-type': 'warn',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'no-console': 'warn',
  },
};
```

### REQ-NODE-006: Prettier Configuration
**Description:** Configure Prettier for code formatting.

**File:** `.prettierrc`
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

### REQ-NODE-007: Git Ignore
**Description:** Configure files to ignore in git.

**File:** `.gitignore`
```
node_modules/
dist/
.env
*.log
.DS_Store
coverage/
```

## Acceptance Criteria
- [ ] Project initializes without errors
- [ ] TypeScript compiles successfully (`npm run build`)
- [ ] All dependencies install without conflicts
- [ ] ESLint runs without configuration errors
- [ ] Folder structure matches specification

## Deliverables
1. `package.json` with all dependencies
2. `tsconfig.json` configured
3. `.env.template` with all variables
4. `.eslintrc.js` and `.prettierrc`
5. `.gitignore`
6. Empty folder structure created

---

# SESSION 2: MCP Server - Core Infrastructure

## Goal
Set up the Express.js server with tool definition loading and core middleware.

## Prerequisites
- Session 1 completed
- Dependencies installed

## Requirements

### REQ-MCP-TS-001: Express Server Initialization
**Description:** Create the main Express application entry point.

**File:** `src/mcp-server/index.ts`
```typescript
import express, { Express } from 'express';
import dotenv from 'dotenv';
import { logger } from './middleware/logger';
import { errorHandler } from './middleware/errorHandler';
import { toolDefsRouter } from './routes/toolDefs';
import { toolsRouter } from './routes/tools';

dotenv.config();

const app: Express = express();
const PORT = process.env.MCP_SERVER_PORT || 8080;

// Middleware
app.use(express.json());
app.use(logger);

// Routes
app.get('/get_tool_defs', toolDefsRouter);
app.use('/tools', toolsRouter);

// Error handling
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  console.log(`[MCP Server] Running on port ${PORT}`);
  console.log(`[MCP Server] Polygon API Key: ${process.env.POLYGON_API_KEY ? 'Configured' : 'MISSING'}`);
});

export default app;
```

### REQ-MCP-TS-002: TypeScript Type Definitions
**Description:** Define TypeScript interfaces for tool definitions.

**File:** `src/mcp-server/types/index.ts`
```typescript
export interface ToolInputSchema {
  type: 'object';
  properties: Record<string, {
    type: string;
    description?: string;
  }>;
  required: string[];
}

export interface ToolOutputSchema {
  type: 'object';
  properties: Record<string, {
    type: string;
    description?: string;
  }>;
}

export interface ToolDefinition {
  id: string;
  description: string;
  input_schema: ToolInputSchema;
  output_schema: ToolOutputSchema;
}

export interface MCPConfig {
  schema_version: string;
  id: string;
  name: string;
  description: string;
  version: string;
  tools: ToolDefinition[];
}

export interface StockPriceResponse {
  ticker: string;
  price: number;
  timestamp: number;
}

export interface TickerDetailsResponse {
  name: string;
  primary_exchange: string;
  locale: string;
  market: string;
  type: string;
}

export interface TradeResponse {
  price: number;
  size: number;
  timestamp: number;
}

export interface QuoteResponse {
  askprice: number;
  asksize: number;
  bidprice: number;
  bidsize: number;
  timestamp: number;
}

export interface AggregateBar {
  o: number;  // open
  h: number;  // high
  l: number;  // low
  c: number;  // close
  v: number;  // volume
  t: number;  // timestamp
}

export interface AggregatesResponse {
  results: AggregateBar[];
}

export interface HistoricTradesResponse {
  results: TradeResponse[];
}
```

### REQ-MCP-TS-003: Tool Definition Loading
**Description:** Load and parse tool definitions from YAML file.

**File:** `src/mcp-server/config/mcp.yaml`
```yaml
schema_version: "v1"
id: polygon-stock-tools
name: Polygon Stock Data Tools
description: Tools for fetching stock market data from Polygon.io API
version: "1.0.0"
tools:
  - id: get_ticker_price
    description: Get the latest stock price for a given ticker symbol
    input_schema:
      type: object
      properties:
        ticker:
          type: string
          description: Stock ticker symbol (e.g., AAPL, TSLA)
      required:
        - ticker
    output_schema:
      type: object
      properties:
        ticker:
          type: string
        price:
          type: number
        timestamp:
          type: integer

  - id: get_ticker_details
    description: Get company details for a given ticker symbol
    input_schema:
      type: object
      properties:
        ticker:
          type: string
          description: Stock ticker symbol
      required:
        - ticker
    output_schema:
      type: object
      properties:
        name:
          type: string
        primary_exchange:
          type: string
        locale:
          type: string
        market:
          type: string
        type:
          type: string

  - id: get_last_trade
    description: Get the most recent trade for a ticker
    input_schema:
      type: object
      properties:
        ticker:
          type: string
          description: Stock ticker symbol
      required:
        - ticker
    output_schema:
      type: object
      properties:
        price:
          type: number
        size:
          type: integer
        timestamp:
          type: integer

  - id: get_last_quote
    description: Get the most recent NBBO quote for a ticker
    input_schema:
      type: object
      properties:
        ticker:
          type: string
          description: Stock ticker symbol
      required:
        - ticker
    output_schema:
      type: object
      properties:
        askprice:
          type: number
        asksize:
          type: integer
        bidprice:
          type: number
        bidsize:
          type: integer
        timestamp:
          type: integer

  - id: get_aggregates
    description: Get aggregate bars (OHLCV) for a ticker over a date range
    input_schema:
      type: object
      properties:
        ticker:
          type: string
          description: Stock ticker symbol
        multiplier:
          type: integer
          description: Size of the timespan multiplier
        timespan:
          type: string
          description: Size of the time window (minute, hour, day, week, month, quarter, year)
        from_date:
          type: string
          description: Start date in YYYY-MM-DD format
        to_date:
          type: string
          description: End date in YYYY-MM-DD format
        limit:
          type: integer
          description: Maximum number of results
      required:
        - ticker
        - multiplier
        - timespan
        - from_date
        - to_date
        - limit
    output_schema:
      type: object
      properties:
        results:
          type: array

  - id: get_historic_trades
    description: Get historic trades for a ticker on a specific date
    input_schema:
      type: object
      properties:
        ticker:
          type: string
          description: Stock ticker symbol
        date:
          type: string
          description: Date in YYYY-MM-DD format
        limit:
          type: integer
          description: Maximum number of results
        timestamp:
          type: integer
          description: Unix timestamp in milliseconds
      required:
        - ticker
        - date
        - limit
        - timestamp
    output_schema:
      type: object
      properties:
        results:
          type: array
```

**File:** `src/mcp-server/routes/toolDefs.ts`
```typescript
import { Request, Response, Router } from 'express';
import { readFileSync } from 'fs';
import { parse } from 'yaml';
import path from 'path';
import { MCPConfig } from '../types';

const router = Router();

export const getToolDefs = (_req: Request, res: Response): void => {
  try {
    const configPath = path.join(__dirname, '../config/mcp.yaml');
    const fileContents = readFileSync(configPath, 'utf8');
    const config: MCPConfig = parse(fileContents);

    console.log(`[get_tool_defs] Loaded ${config.tools.length} tool definitions`);
    res.json(config);
  } catch (error) {
    console.error('[get_tool_defs] Error loading tool definitions:', error);
    res.status(500).json({
      error: 'Failed to load tool definitions',
      detail: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

router.get('/', getToolDefs);

export { router as toolDefsRouter };
```

### REQ-MCP-TS-004: Logging Middleware
**Description:** Implement request logging using Winston.

**File:** `src/mcp-server/middleware/logger.ts`
```typescript
import { Request, Response, NextFunction } from 'express';
import winston from 'winston';

const isLoggingEnabled = process.env.MCP_SERVER_LOG_ENABLED !== 'false';

export const winstonLogger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.printf(({ timestamp, level, message }) => {
      return `${timestamp} [${level.toUpperCase()}] ${message}`;
    })
  ),
  transports: [
    new winston.transports.Console({
      silent: !isLoggingEnabled,
    }),
  ],
});

export const logger = (req: Request, _res: Response, next: NextFunction): void => {
  if (isLoggingEnabled) {
    winstonLogger.info(`${req.method} ${req.path} - ${JSON.stringify(req.body)}`);
  }
  next();
};
```

### REQ-MCP-TS-005: Error Handler Middleware
**Description:** Implement centralized error handling.

**File:** `src/mcp-server/middleware/errorHandler.ts`
```typescript
import { Request, Response, NextFunction } from 'express';
import { winstonLogger } from './logger';

export interface AppError extends Error {
  statusCode?: number;
  detail?: string;
}

export const errorHandler = (
  err: AppError,
  _req: Request,
  res: Response,
  _next: NextFunction
): void => {
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  winstonLogger.error(`[Error] ${statusCode} - ${message}`);

  res.status(statusCode).json({
    error: message,
    detail: err.detail || null,
  });
};

export const createError = (statusCode: number, message: string, detail?: string): AppError => {
  const error: AppError = new Error(message);
  error.statusCode = statusCode;
  error.detail = detail;
  return error;
};
```

## Acceptance Criteria
- [ ] Server starts on port 8080
- [ ] GET /get_tool_defs returns tool definitions from YAML
- [ ] Logging shows requests when enabled
- [ ] Environment variables load correctly
- [ ] TypeScript compiles without errors

## Deliverables
1. `src/mcp-server/index.ts` - Main server file
2. `src/mcp-server/types/index.ts` - Type definitions
3. `src/mcp-server/config/mcp.yaml` - Tool definitions
4. `src/mcp-server/routes/toolDefs.ts` - Tool definition endpoint
5. `src/mcp-server/middleware/logger.ts` - Logging middleware
6. `src/mcp-server/middleware/errorHandler.ts` - Error handling

## Testing Commands
```bash
# Start server
npm run dev:server

# Test tool definitions endpoint
curl http://localhost:8080/get_tool_defs
```

---

# SESSION 3: MCP Server - Stock Tools Part 1

## Goal
Implement the first 3 Polygon API tool endpoints with request validation.

## Prerequisites
- Session 2 completed
- MCP Server running

## Requirements

### REQ-MCP-TS-006: Zod Request Schemas
**Description:** Define request validation schemas using Zod.

**File:** `src/mcp-server/schemas/requests.ts`
```typescript
import { z } from 'zod';

export const StockRequestSchema = z.object({
  ticker: z.string().min(1).max(10).transform(val => val.toUpperCase()),
});

export const TickerDetailsRequestSchema = z.object({
  ticker: z.string().min(1).max(10).transform(val => val.toUpperCase()),
});

export const LastTradeRequestSchema = z.object({
  ticker: z.string().min(1).max(10).transform(val => val.toUpperCase()),
});

export const LastQuoteRequestSchema = z.object({
  ticker: z.string().min(1).max(10).transform(val => val.toUpperCase()),
});

export const AggregatesRequestSchema = z.object({
  ticker: z.string().min(1).max(10).transform(val => val.toUpperCase()),
  multiplier: z.number().int().positive(),
  timespan: z.enum(['minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']),
  from_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be YYYY-MM-DD'),
  to_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be YYYY-MM-DD'),
  limit: z.number().int().positive().max(50000),
});

export const HistoricTradesRequestSchema = z.object({
  ticker: z.string().min(1).max(10).transform(val => val.toUpperCase()),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be YYYY-MM-DD'),
  limit: z.number().int().positive().max(50000),
  timestamp: z.number().int(),
});

// Type exports
export type StockRequest = z.infer<typeof StockRequestSchema>;
export type TickerDetailsRequest = z.infer<typeof TickerDetailsRequestSchema>;
export type LastTradeRequest = z.infer<typeof LastTradeRequestSchema>;
export type LastQuoteRequest = z.infer<typeof LastQuoteRequestSchema>;
export type AggregatesRequest = z.infer<typeof AggregatesRequestSchema>;
export type HistoricTradesRequest = z.infer<typeof HistoricTradesRequestSchema>;
```

### REQ-MCP-TS-007: Polygon API Service
**Description:** Create a service layer for Polygon API calls.

**File:** `src/mcp-server/services/polygonApi.ts`
```typescript
import axios, { AxiosResponse } from 'axios';
import { winstonLogger } from '../middleware/logger';
import { createError } from '../middleware/errorHandler';

const POLYGON_BASE_URL = 'https://api.polygon.io';

const getApiKey = (): string => {
  const apiKey = process.env.POLYGON_API_KEY;
  if (!apiKey) {
    throw createError(500, 'POLYGON_API_KEY not configured');
  }
  return apiKey;
};

export const handlePolygonError = (error: unknown, toolName: string): never => {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.error || error.response?.data || error.message;
    winstonLogger.error(`[${toolName}] Polygon API error: ${error.response?.status} - ${JSON.stringify(detail)}`);
    throw createError(400, `Polygon API error for ${toolName}`, JSON.stringify(detail));
  }
  throw error;
};

export const polygonApi = {
  async getTickerPrice(ticker: string): Promise<AxiosResponse> {
    const url = `${POLYGON_BASE_URL}/v2/aggs/ticker/${ticker}/prev?adjusted=true&apiKey=${getApiKey()}`;
    winstonLogger.info(`[get_ticker_price] Calling Polygon API for ${ticker}`);
    return axios.get(url);
  },

  async getTickerDetails(ticker: string): Promise<AxiosResponse> {
    const url = `${POLYGON_BASE_URL}/v3/reference/tickers/${ticker}?apiKey=${getApiKey()}`;
    winstonLogger.info(`[get_ticker_details] Calling Polygon API for ${ticker}`);
    return axios.get(url);
  },

  async getLastTrade(ticker: string): Promise<AxiosResponse> {
    const url = `${POLYGON_BASE_URL}/v2/last/trade/${ticker}?apiKey=${getApiKey()}`;
    winstonLogger.info(`[get_last_trade] Calling Polygon API for ${ticker}`);
    return axios.get(url);
  },

  async getLastQuote(ticker: string): Promise<AxiosResponse> {
    const url = `${POLYGON_BASE_URL}/v2/last/nbbo/${ticker}?apiKey=${getApiKey()}`;
    winstonLogger.info(`[get_last_quote] Calling Polygon API for ${ticker}`);
    return axios.get(url);
  },

  async getAggregates(
    ticker: string,
    multiplier: number,
    timespan: string,
    fromDate: string,
    toDate: string,
    limit: number
  ): Promise<AxiosResponse> {
    const url = `${POLYGON_BASE_URL}/v2/aggs/ticker/${ticker}/range/${multiplier}/${timespan}/${fromDate}/${toDate}?adjusted=true&sort=desc&limit=${limit}&apiKey=${getApiKey()}`;
    winstonLogger.info(`[get_aggregates] Calling Polygon API for ${ticker}`);
    return axios.get(url);
  },

  async getHistoricTrades(
    ticker: string,
    date: string,
    limit: number,
    timestamp: number
  ): Promise<AxiosResponse> {
    const url = `${POLYGON_BASE_URL}/v2/ticks/stocks/trades/${ticker}/${date}?apiKey=${getApiKey()}&limit=${limit}&timestamp=${timestamp}`;
    winstonLogger.info(`[get_historic_trades] Calling Polygon API for ${ticker}`);
    return axios.get(url);
  },
};
```

### REQ-MCP-TS-008: Get Ticker Price Endpoint
**Description:** Implement POST /tools/get_ticker_price endpoint.

**File:** `src/mcp-server/routes/tools/getTickerPrice.ts`
```typescript
import { Request, Response, NextFunction } from 'express';
import { StockRequestSchema } from '../../schemas/requests';
import { polygonApi, handlePolygonError } from '../../services/polygonApi';
import { winstonLogger } from '../../middleware/logger';
import { StockPriceResponse } from '../../types';

export const getTickerPrice = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const validatedData = StockRequestSchema.parse(req.body);
    const { ticker } = validatedData;

    winstonLogger.info(`[get_ticker_price] Request for ticker: ${ticker}`);

    const response = await polygonApi.getTickerPrice(ticker);
    const result = response.data.results[0];

    const stockPrice: StockPriceResponse = {
      ticker: ticker,
      price: result.c,  // closing price
      timestamp: result.t,
    };

    winstonLogger.info(`[get_ticker_price] ${ticker}: $${stockPrice.price}`);
    res.json(stockPrice);
  } catch (error) {
    if (error instanceof Error && error.name === 'ZodError') {
      res.status(400).json({ error: 'Validation error', detail: error.message });
      return;
    }
    handlePolygonError(error, 'get_ticker_price');
    next(error);
  }
};
```

### REQ-MCP-TS-009: Get Ticker Details Endpoint
**Description:** Implement POST /tools/get_ticker_details endpoint.

**File:** `src/mcp-server/routes/tools/getTickerDetails.ts`
```typescript
import { Request, Response, NextFunction } from 'express';
import { TickerDetailsRequestSchema } from '../../schemas/requests';
import { polygonApi, handlePolygonError } from '../../services/polygonApi';
import { winstonLogger } from '../../middleware/logger';
import { TickerDetailsResponse } from '../../types';

export const getTickerDetails = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const validatedData = TickerDetailsRequestSchema.parse(req.body);
    const { ticker } = validatedData;

    winstonLogger.info(`[get_ticker_details] Request for ticker: ${ticker}`);

    const response = await polygonApi.getTickerDetails(ticker);
    const result = response.data.results;

    const details: TickerDetailsResponse = {
      name: result.name,
      primary_exchange: result.primary_exchange,
      locale: result.locale,
      market: result.market,
      type: result.type,
    };

    winstonLogger.info(`[get_ticker_details] ${ticker}: ${details.name}`);
    res.json(details);
  } catch (error) {
    if (error instanceof Error && error.name === 'ZodError') {
      res.status(400).json({ error: 'Validation error', detail: error.message });
      return;
    }
    handlePolygonError(error, 'get_ticker_details');
    next(error);
  }
};
```

### REQ-MCP-TS-010: Get Last Trade Endpoint
**Description:** Implement POST /tools/get_last_trade endpoint.

**File:** `src/mcp-server/routes/tools/getLastTrade.ts`
```typescript
import { Request, Response, NextFunction } from 'express';
import { LastTradeRequestSchema } from '../../schemas/requests';
import { polygonApi, handlePolygonError } from '../../services/polygonApi';
import { winstonLogger } from '../../middleware/logger';
import { TradeResponse } from '../../types';

export const getLastTrade = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const validatedData = LastTradeRequestSchema.parse(req.body);
    const { ticker } = validatedData;

    winstonLogger.info(`[get_last_trade] Request for ticker: ${ticker}`);

    const response = await polygonApi.getLastTrade(ticker);
    const result = response.data.results;

    const trade: TradeResponse = {
      price: result.p,
      size: result.s,
      timestamp: result.t,
    };

    winstonLogger.info(`[get_last_trade] ${ticker}: $${trade.price} (${trade.size} shares)`);
    res.json(trade);
  } catch (error) {
    if (error instanceof Error && error.name === 'ZodError') {
      res.status(400).json({ error: 'Validation error', detail: error.message });
      return;
    }
    handlePolygonError(error, 'get_last_trade');
    next(error);
  }
};
```

### REQ-MCP-TS-011: Tools Router
**Description:** Create router to combine all tool endpoints.

**File:** `src/mcp-server/routes/tools/index.ts`
```typescript
import { Router } from 'express';
import { getTickerPrice } from './getTickerPrice';
import { getTickerDetails } from './getTickerDetails';
import { getLastTrade } from './getLastTrade';
// Part 2 endpoints will be added in Session 4
// import { getLastQuote } from './getLastQuote';
// import { getAggregates } from './getAggregates';
// import { getHistoricTrades } from './getHistoricTrades';

const router = Router();

router.post('/get_ticker_price', getTickerPrice);
router.post('/get_ticker_details', getTickerDetails);
router.post('/get_last_trade', getLastTrade);
// router.post('/get_last_quote', getLastQuote);
// router.post('/get_aggregates', getAggregates);
// router.post('/get_historic_trades', getHistoricTrades);

export { router as toolsRouter };
```

## Acceptance Criteria
- [ ] POST /tools/get_ticker_price returns stock price
- [ ] POST /tools/get_ticker_details returns company info
- [ ] POST /tools/get_last_trade returns last trade data
- [ ] Invalid requests return 400 with validation errors
- [ ] Polygon API errors are handled gracefully

## Deliverables
1. `src/mcp-server/schemas/requests.ts` - Zod schemas
2. `src/mcp-server/services/polygonApi.ts` - Polygon API service
3. `src/mcp-server/routes/tools/getTickerPrice.ts`
4. `src/mcp-server/routes/tools/getTickerDetails.ts`
5. `src/mcp-server/routes/tools/getLastTrade.ts`
6. `src/mcp-server/routes/tools/index.ts` - Router

## Testing Commands
```bash
# Test get_ticker_price
curl -X POST http://localhost:8080/tools/get_ticker_price \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AAPL"}'

# Test get_ticker_details
curl -X POST http://localhost:8080/tools/get_ticker_details \
     -H "Content-Type: application/json" \
     -d '{"ticker": "TSLA"}'

# Test get_last_trade
curl -X POST http://localhost:8080/tools/get_last_trade \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AMZN"}'
```

---

# SESSION 4: MCP Server - Stock Tools Part 2

## Goal
Implement the remaining 3 Polygon API tool endpoints.

## Prerequisites
- Session 3 completed
- First 3 tool endpoints working

## Requirements

### REQ-MCP-TS-012: Get Last Quote Endpoint
**Description:** Implement POST /tools/get_last_quote endpoint.

**File:** `src/mcp-server/routes/tools/getLastQuote.ts`
```typescript
import { Request, Response, NextFunction } from 'express';
import { LastQuoteRequestSchema } from '../../schemas/requests';
import { polygonApi, handlePolygonError } from '../../services/polygonApi';
import { winstonLogger } from '../../middleware/logger';
import { QuoteResponse } from '../../types';

export const getLastQuote = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const validatedData = LastQuoteRequestSchema.parse(req.body);
    const { ticker } = validatedData;

    winstonLogger.info(`[get_last_quote] Request for ticker: ${ticker}`);

    const response = await polygonApi.getLastQuote(ticker);
    const result = response.data.results;

    const quote: QuoteResponse = {
      askprice: result.ap,
      asksize: result.as,
      bidprice: result.bp,
      bidsize: result.bs,
      timestamp: result.t,
    };

    winstonLogger.info(`[get_last_quote] ${ticker}: Bid $${quote.bidprice}, Ask $${quote.askprice}`);
    res.json(quote);
  } catch (error) {
    if (error instanceof Error && error.name === 'ZodError') {
      res.status(400).json({ error: 'Validation error', detail: error.message });
      return;
    }
    handlePolygonError(error, 'get_last_quote');
    next(error);
  }
};
```

### REQ-MCP-TS-013: Get Aggregates Endpoint
**Description:** Implement POST /tools/get_aggregates endpoint.

**File:** `src/mcp-server/routes/tools/getAggregates.ts`
```typescript
import { Request, Response, NextFunction } from 'express';
import { AggregatesRequestSchema } from '../../schemas/requests';
import { polygonApi, handlePolygonError } from '../../services/polygonApi';
import { winstonLogger } from '../../middleware/logger';
import { AggregatesResponse } from '../../types';

export const getAggregates = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const validatedData = AggregatesRequestSchema.parse(req.body);
    const { ticker, multiplier, timespan, from_date, to_date, limit } = validatedData;

    winstonLogger.info(`[get_aggregates] Request for ${ticker}: ${multiplier} ${timespan} from ${from_date} to ${to_date}`);

    const response = await polygonApi.getAggregates(
      ticker, multiplier, timespan, from_date, to_date, limit
    );

    const aggregates: AggregatesResponse = {
      results: response.data.results || [],
    };

    winstonLogger.info(`[get_aggregates] ${ticker}: Returned ${aggregates.results.length} bars`);
    res.json(aggregates);
  } catch (error) {
    if (error instanceof Error && error.name === 'ZodError') {
      res.status(400).json({ error: 'Validation error', detail: error.message });
      return;
    }
    handlePolygonError(error, 'get_aggregates');
    next(error);
  }
};
```

### REQ-MCP-TS-014: Get Historic Trades Endpoint
**Description:** Implement POST /tools/get_historic_trades endpoint.

**File:** `src/mcp-server/routes/tools/getHistoricTrades.ts`
```typescript
import { Request, Response, NextFunction } from 'express';
import { HistoricTradesRequestSchema } from '../../schemas/requests';
import { polygonApi, handlePolygonError } from '../../services/polygonApi';
import { winstonLogger } from '../../middleware/logger';
import { HistoricTradesResponse } from '../../types';

export const getHistoricTrades = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const validatedData = HistoricTradesRequestSchema.parse(req.body);
    const { ticker, date, limit, timestamp } = validatedData;

    winstonLogger.info(`[get_historic_trades] Request for ${ticker} on ${date}`);

    const response = await polygonApi.getHistoricTrades(ticker, date, limit, timestamp);

    const trades: HistoricTradesResponse = {
      results: (response.data.results || []).map((t: { p: number; s: number; t: number }) => ({
        price: t.p,
        size: t.s,
        timestamp: t.t,
      })),
    };

    winstonLogger.info(`[get_historic_trades] ${ticker}: Returned ${trades.results.length} trades`);
    res.json(trades);
  } catch (error) {
    if (error instanceof Error && error.name === 'ZodError') {
      res.status(400).json({ error: 'Validation error', detail: error.message });
      return;
    }
    handlePolygonError(error, 'get_historic_trades');
    next(error);
  }
};
```

### REQ-MCP-TS-015: Update Tools Router
**Description:** Add remaining endpoints to router.

**File:** `src/mcp-server/routes/tools/index.ts` (updated)
```typescript
import { Router } from 'express';
import { getTickerPrice } from './getTickerPrice';
import { getTickerDetails } from './getTickerDetails';
import { getLastTrade } from './getLastTrade';
import { getLastQuote } from './getLastQuote';
import { getAggregates } from './getAggregates';
import { getHistoricTrades } from './getHistoricTrades';

const router = Router();

router.post('/get_ticker_price', getTickerPrice);
router.post('/get_ticker_details', getTickerDetails);
router.post('/get_last_trade', getLastTrade);
router.post('/get_last_quote', getLastQuote);
router.post('/get_aggregates', getAggregates);
router.post('/get_historic_trades', getHistoricTrades);

export { router as toolsRouter };
```

## Acceptance Criteria
- [ ] POST /tools/get_last_quote returns NBBO data
- [ ] POST /tools/get_aggregates returns OHLCV bars
- [ ] POST /tools/get_historic_trades returns trade history
- [ ] All 6 tool endpoints operational
- [ ] Error handling consistent across all endpoints

## Deliverables
1. `src/mcp-server/routes/tools/getLastQuote.ts`
2. `src/mcp-server/routes/tools/getAggregates.ts`
3. `src/mcp-server/routes/tools/getHistoricTrades.ts`
4. Updated `src/mcp-server/routes/tools/index.ts`

## Testing Commands
```bash
# Test get_last_quote
curl -X POST http://localhost:8080/tools/get_last_quote \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AAPL"}'

# Test get_aggregates
curl -X POST http://localhost:8080/tools/get_aggregates \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AAPL", "multiplier": 1, "timespan": "day", "from_date": "2024-01-01", "to_date": "2024-01-31", "limit": 10}'

# Test get_historic_trades
curl -X POST http://localhost:8080/tools/get_historic_trades \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AAPL", "date": "2024-01-15", "limit": 10, "timestamp": 0}'
```

---

# SESSION 5: AI Agent - Core Infrastructure

## Goal
Set up the Anthropic client, MCP client, and core utilities for the AI agent.

## Prerequisites
- Sessions 1-4 completed
- MCP Server fully operational

## Requirements

### REQ-AGENT-TS-001: Agent Type Definitions
**Description:** Define TypeScript interfaces for the agent.

**File:** `src/agent/types/index.ts`
```typescript
export interface MCPToolDefinition {
  id: string;
  description: string;
  input_schema: {
    type: string;
    properties: Record<string, unknown>;
    required: string[];
  };
}

export interface AnthropicTool {
  name: string;
  description: string;
  input_schema: {
    type: string;
    properties: Record<string, unknown>;
    required: string[];
  };
}

export interface ToolUseBlock {
  type: 'tool_use';
  id: string;
  name: string;
  input: Record<string, unknown>;
}

export interface TextBlock {
  type: 'text';
  text: string;
}

export interface ToolResultBlock {
  type: 'tool_result';
  tool_use_id: string;
  content: string;
  is_error?: boolean;
}

export type ContentBlock = ToolUseBlock | TextBlock;

export interface Message {
  role: 'user' | 'assistant';
  content: string | ContentBlock[] | ToolResultBlock[];
}

export interface AgentConfig {
  model: string;
  maxTokens: number;
  mcpBaseUrl: string;
}
```

### REQ-AGENT-TS-002: Anthropic Client Service
**Description:** Initialize and configure the Anthropic SDK client.

**File:** `src/agent/services/anthropicClient.ts`
```typescript
import Anthropic from '@anthropic-ai/sdk';
import dotenv from 'dotenv';

dotenv.config();

const getApiKey = (): string => {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.error('[Agent] ANTHROPIC_API_KEY not configured');
    process.exit(1);
  }
  return apiKey;
};

export const anthropicClient = new Anthropic({
  apiKey: getApiKey(),
});

export const MODEL = 'claude-sonnet-4-20250514';
export const MAX_TOKENS = 1024;

export const SYSTEM_PROMPT = `You are a financial assistant with access to stock data tools.
When the user asks about stock prices or financial data, use the available tools to fetch real-time information.
Always provide clear, helpful responses based on the data you retrieve.`;
```

### REQ-AGENT-TS-003: MCP Client Service
**Description:** HTTP client for communicating with MCP server.

**File:** `src/agent/services/mcpClient.ts`
```typescript
import axios from 'axios';
import dotenv from 'dotenv';
import { MCPToolDefinition, AnthropicTool } from '../types';

dotenv.config();

const MCP_BASE_URL = process.env.MCP_BASE_URL || 'http://localhost:8080';

const isLoggingEnabled = process.env.AGENT_LOG_ENABLED !== 'false';

const log = (message: string): void => {
  if (isLoggingEnabled) {
    console.log(message);
  }
};

export const fetchToolDefinitions = async (): Promise<MCPToolDefinition[]> => {
  try {
    log('[Agent] Fetching tool definitions from MCP server...');
    const response = await axios.get(`${MCP_BASE_URL}/get_tool_defs`);
    const tools = response.data.tools as MCPToolDefinition[];
    log(`[Agent] Loaded ${tools.length} tools from MCP server`);
    return tools;
  } catch (error) {
    console.error('[Agent] Failed to fetch tool definitions:', error);
    process.exit(1);
  }
};

export const callMcpTool = async (
  toolId: string,
  args: Record<string, unknown>
): Promise<unknown> => {
  const url = `${MCP_BASE_URL}/tools/${toolId}`;
  log(`[Agent] Calling MCP tool: ${toolId}`);
  log(`[Agent] Parameters: ${JSON.stringify(args)}`);

  try {
    const response = await axios.post(url, args);
    log(`[Agent] Tool ${toolId} response received`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail || error.response?.data || error.message;
      console.error(`[Agent] Tool ${toolId} error: ${JSON.stringify(detail)}`);
      throw new Error(`Tool ${toolId} failed: ${JSON.stringify(detail)}`);
    }
    throw error;
  }
};

export const convertToAnthropicTools = (mcpTools: MCPToolDefinition[]): AnthropicTool[] => {
  return mcpTools.map((tool) => ({
    name: tool.id,
    description: tool.description,
    input_schema: tool.input_schema,
  }));
};
```

### REQ-AGENT-TS-004: Timestamp Utilities
**Description:** Utility functions for timestamp handling.

**File:** `src/agent/utils/timestamp.ts`
```typescript
import { formatInTimeZone, toZonedTime } from 'date-fns-tz';

const DEFAULT_TIMEZONE = 'America/Los_Angeles';

export const currentEpochMs = (timezone: string = 'UTC'): number => {
  const now = new Date();
  const zonedTime = toZonedTime(now, timezone);
  return zonedTime.getTime();
};

export const datetimeFromEpochMs = (
  epochMs: number,
  timezone: string = DEFAULT_TIMEZONE
): Date => {
  const utcDate = new Date(epochMs);
  return toZonedTime(utcDate, timezone);
};

export const formatTimestamp = (
  epochMs: number,
  timezone: string = DEFAULT_TIMEZONE
): string => {
  return formatInTimeZone(
    new Date(epochMs),
    timezone,
    'yyyy-MM-dd HH:mm:ss zzz'
  );
};
```

### REQ-AGENT-TS-005: Tool Converter Utility
**Description:** Convert MCP tool format to Anthropic format.

**File:** `src/agent/utils/toolConverter.ts`
```typescript
import { MCPToolDefinition, AnthropicTool } from '../types';

export const convertMcpToAnthropicTools = (
  mcpTools: MCPToolDefinition[]
): AnthropicTool[] => {
  return mcpTools.map((tool) => ({
    name: tool.id,
    description: tool.description,
    input_schema: {
      type: tool.input_schema.type,
      properties: tool.input_schema.properties,
      required: tool.input_schema.required,
    },
  }));
};
```

## Acceptance Criteria
- [ ] Anthropic client initializes successfully
- [ ] MCP tool definitions fetch from server
- [ ] Tool conversion produces valid Anthropic format
- [ ] Timestamp utilities work correctly
- [ ] Error handling for missing API keys

## Deliverables
1. `src/agent/types/index.ts` - Type definitions
2. `src/agent/services/anthropicClient.ts` - Anthropic SDK
3. `src/agent/services/mcpClient.ts` - MCP HTTP client
4. `src/agent/utils/timestamp.ts` - Timestamp utilities
5. `src/agent/utils/toolConverter.ts` - Tool conversion

---

# SESSION 6: AI Agent - Execution Loop

## Goal
Implement the main agent execution loop with tool use handling and CLI interface.

## Prerequisites
- Session 5 completed
- Agent infrastructure in place

## Requirements

### REQ-AGENT-TS-006: Response Formatter
**Description:** Format tool results for human readability.

**File:** `src/agent/utils/responseFormatter.ts`
```typescript
import { formatTimestamp } from './timestamp';

interface StockPriceResult {
  ticker: string;
  price: number;
  timestamp: number;
}

interface TickerDetailsResult {
  name: string;
  type: string;
  primary_exchange: string;
  market: string;
  locale: string;
}

interface TradeResult {
  price: number;
  size: number;
  timestamp: number;
}

interface QuoteResult {
  bidprice: number;
  bidsize: number;
  askprice: number;
  asksize: number;
  timestamp: number;
}

interface AggregatesResult {
  results: Array<{
    o: number;
    h: number;
    l: number;
    c: number;
    v: number;
  }>;
}

interface HistoricTradesResult {
  results: TradeResult[];
}

type ToolResult =
  | StockPriceResult
  | TickerDetailsResult
  | TradeResult
  | QuoteResult
  | AggregatesResult
  | HistoricTradesResult;

export const formatToolResponse = (
  toolName: string,
  result: ToolResult
): string => {
  try {
    switch (toolName) {
      case 'get_ticker_price': {
        const r = result as StockPriceResult;
        return `Ticker: ${r.ticker}, Price: $${r.price}, Time: ${formatTimestamp(r.timestamp)}`;
      }

      case 'get_ticker_details': {
        const r = result as TickerDetailsResult;
        return `${r.name} (${r.type} on ${r.primary_exchange}) - Market: ${r.market}, Locale: ${r.locale}`;
      }

      case 'get_last_trade': {
        const r = result as TradeResult;
        return `Last trade: $${r.price} (Size: ${r.size}) at ${formatTimestamp(r.timestamp)}`;
      }

      case 'get_last_quote': {
        const r = result as QuoteResult;
        return `Bid: $${r.bidprice} (${r.bidsize}), Ask: $${r.askprice} (${r.asksize}), Time: ${formatTimestamp(r.timestamp)}`;
      }

      case 'get_aggregates': {
        const r = result as AggregatesResult;
        if (r.results && r.results.length > 0) {
          const bar = r.results[0];
          return `OHLC: ${bar.o}, ${bar.h}, ${bar.l}, ${bar.c} - Volume: ${bar.v}`;
        }
        return 'No aggregate data available';
      }

      case 'get_historic_trades': {
        const r = result as HistoricTradesResult;
        if (r.results && r.results.length > 0) {
          const trade = r.results[0];
          return `Trade: Price $${trade.price}, Size ${trade.size} at ${formatTimestamp(trade.timestamp)}`;
        }
        return 'No historic trade data available';
      }

      default:
        return JSON.stringify(result);
    }
  } catch (error) {
    console.warn(`[Agent] Error formatting response for ${toolName}:`, error);
    return JSON.stringify(result);
  }
};
```

### REQ-AGENT-TS-007: Agent Execution Loop
**Description:** Main agent loop with tool use handling.

**File:** `src/agent/core/agentLoop.ts`
```typescript
import { anthropicClient, MODEL, MAX_TOKENS, SYSTEM_PROMPT } from '../services/anthropicClient';
import { fetchToolDefinitions, callMcpTool, convertToAnthropicTools } from '../services/mcpClient';
import { formatToolResponse } from '../utils/responseFormatter';
import { Message, ContentBlock, ToolUseBlock, ToolResultBlock, AnthropicTool } from '../types';

const isLoggingEnabled = process.env.AGENT_LOG_ENABLED !== 'false';

const log = (message: string): void => {
  if (isLoggingEnabled) {
    console.log(message);
  }
};

let cachedTools: AnthropicTool[] | null = null;

const getTools = async (): Promise<AnthropicTool[]> => {
  if (!cachedTools) {
    const mcpTools = await fetchToolDefinitions();
    cachedTools = convertToAnthropicTools(mcpTools);
  }
  return cachedTools;
};

export const runAgent = async (userQuestion: string): Promise<string> => {
  log('\n' + '='.repeat(60));
  log('[Agent] Starting agent run');
  log(`[Agent] User question: ${userQuestion}`);

  const tools = await getTools();
  const messages: Message[] = [{ role: 'user', content: userQuestion }];

  log(`[Agent] Sending to Claude (model: ${MODEL})`);

  let response = await anthropicClient.messages.create({
    model: MODEL,
    max_tokens: MAX_TOKENS,
    system: SYSTEM_PROMPT,
    tools: tools as Anthropic.Tool[],
    messages: messages as Anthropic.MessageParam[],
  });

  log(`[Agent] Response stop_reason: ${response.stop_reason}`);

  let iteration = 0;

  while (response.stop_reason === 'tool_use') {
    iteration++;

    const toolUseBlocks = response.content.filter(
      (block): block is ToolUseBlock => block.type === 'tool_use'
    );

    log(`[Agent] Iteration ${iteration}: ${toolUseBlocks.length} tool(s) to execute`);

    // Add assistant response to messages
    messages.push({
      role: 'assistant',
      content: response.content as ContentBlock[],
    });

    // Process each tool use
    const toolResults: ToolResultBlock[] = [];

    for (const toolUse of toolUseBlocks) {
      log(`[Agent] Executing tool: ${toolUse.name}`);
      log(`[Agent] Tool input: ${JSON.stringify(toolUse.input)}`);

      try {
        const result = await callMcpTool(toolUse.name, toolUse.input);
        const formattedResult = formatToolResponse(toolUse.name, result as never);
        log(`[Agent] Tool result: ${formattedResult}`);

        toolResults.push({
          type: 'tool_result',
          tool_use_id: toolUse.id,
          content: JSON.stringify(result),
        });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        console.error(`[Agent] Tool error: ${errorMessage}`);

        toolResults.push({
          type: 'tool_result',
          tool_use_id: toolUse.id,
          content: `Error: ${errorMessage}`,
          is_error: true,
        });
      }
    }

    // Add tool results to messages
    messages.push({
      role: 'user',
      content: toolResults,
    });

    log('[Agent] Sending tool results back to Claude');

    // Get next response
    response = await anthropicClient.messages.create({
      model: MODEL,
      max_tokens: MAX_TOKENS,
      system: SYSTEM_PROMPT,
      tools: tools as Anthropic.Tool[],
      messages: messages as Anthropic.MessageParam[],
    });

    log(`[Agent] Response stop_reason: ${response.stop_reason}`);
  }

  // Extract final text response
  const textBlocks = response.content.filter(
    (block): block is { type: 'text'; text: string } => block.type === 'text'
  );

  const finalResponse = textBlocks.map((block) => block.text).join('\n');

  log(`[Agent] Completed in ${iteration} iteration(s)`);
  log('='.repeat(60) + '\n');

  return finalResponse;
};

// Type import for Anthropic SDK
import Anthropic from '@anthropic-ai/sdk';
```

### REQ-AGENT-TS-008: CLI Interface
**Description:** Command-line interface for user interaction.

**File:** `src/agent/cli.ts`
```typescript
import * as readline from 'readline';
import { runAgent } from './core/agentLoop';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const askQuestion = (): void => {
  rl.question('Ask a stock-related question:\n> ', async (input) => {
    const question = input.trim();

    if (!question) {
      console.log('Please enter a question.');
      askQuestion();
      return;
    }

    if (question.toLowerCase() === 'exit' || question.toLowerCase() === 'quit') {
      console.log('Goodbye!');
      rl.close();
      process.exit(0);
    }

    try {
      const response = await runAgent(question);
      console.log('\n' + response + '\n');
    } catch (error) {
      console.error('Error:', error instanceof Error ? error.message : error);
    }

    askQuestion();
  });
};

console.log('GameStocks Agent - Node.js Edition');
console.log('Type "exit" or "quit" to stop.\n');
askQuestion();
```

### REQ-AGENT-TS-009: Agent Entry Point
**Description:** Main entry point for the agent.

**File:** `src/agent/index.ts`
```typescript
import dotenv from 'dotenv';

// Load environment variables first
dotenv.config();

// Import and run CLI
import './cli';
```

## Acceptance Criteria
- [ ] Agent starts and prompts for questions
- [ ] User question sent to Claude with tools
- [ ] Tool use detected and executed via MCP server
- [ ] Tool results formatted and returned to Claude
- [ ] Final response printed to console
- [ ] Multiple iterations supported

## Deliverables
1. `src/agent/utils/responseFormatter.ts` - Response formatting
2. `src/agent/core/agentLoop.ts` - Main execution loop
3. `src/agent/cli.ts` - CLI interface
4. `src/agent/index.ts` - Entry point

## Testing
```bash
# Start MCP server first
npm run dev:server

# In another terminal, run agent
npm run dev:agent

# Test with question
> What is the stock price of Elon Musk's company?
```

---

# SESSION 7: WebSocket Streaming

## Goal
Implement real-time market data streaming using Polygon.io WebSocket API.

## Prerequisites
- Session 1-2 completed (for environment setup)
- Polygon API key configured

## Requirements

### REQ-WS-TS-001: WebSocket Client Setup
**Description:** Configure Polygon WebSocket client.

**File:** `src/websocket/client.ts`
```typescript
import { WebSocketClient, Feed, Market } from '@polygon.io/client-js';
import dotenv from 'dotenv';

dotenv.config();

const getApiKey = (): string => {
  const apiKey = process.env.POLYGON_API_KEY;
  if (!apiKey) {
    console.error('[WebSocket] POLYGON_API_KEY not configured');
    process.exit(1);
  }
  return apiKey;
};

export const createWebSocketClient = (): WebSocketClient => {
  return new WebSocketClient({
    apiKey: getApiKey(),
    feed: Feed.Delayed,
    market: Market.Stocks,
  });
};
```

### REQ-WS-TS-002: Message Handler
**Description:** Generic message handler for WebSocket streams.

**File:** `src/websocket/handlers/messageHandler.ts`
```typescript
export interface StreamMessage {
  ev: string;      // Event type
  sym: string;     // Symbol
  [key: string]: unknown;
}

export const createMessageHandler = (streamName: string) => {
  return (messages: StreamMessage[]): void => {
    for (const msg of messages) {
      console.log(`[${streamName}] ${msg.sym}:`, JSON.stringify(msg, null, 2));
    }
  };
};

export const createAggregateHandler = (streamName: string) => {
  return (messages: StreamMessage[]): void => {
    for (const msg of messages) {
      const { sym, o, h, l, c, v, s, e } = msg as StreamMessage & {
        o: number; h: number; l: number; c: number; v: number; s: number; e: number;
      };
      console.log(`[${streamName}] ${sym}: O=${o} H=${h} L=${l} C=${c} V=${v} Start=${s} End=${e}`);
    }
  };
};

export const createTradeHandler = (streamName: string) => {
  return (messages: StreamMessage[]): void => {
    for (const msg of messages) {
      const { sym, p, s: size, t } = msg as StreamMessage & {
        p: number; s: number; t: number;
      };
      console.log(`[${streamName}] ${sym}: Price=$${p} Size=${size} Time=${t}`);
    }
  };
};

export const createQuoteHandler = (streamName: string) => {
  return (messages: StreamMessage[]): void => {
    for (const msg of messages) {
      const { sym, bp, bs, ap, as: askSize, t } = msg as StreamMessage & {
        bp: number; bs: number; ap: number; as: number; t: number;
      };
      console.log(`[${streamName}] ${sym}: Bid=$${bp}(${bs}) Ask=$${ap}(${askSize}) Time=${t}`);
    }
  };
};
```

### REQ-WS-TS-003: Trades Stream
**Description:** Real-time trade streaming.

**File:** `src/websocket/streams/trades.ts`
```typescript
import { createWebSocketClient } from '../client';
import { createTradeHandler, StreamMessage } from '../handlers/messageHandler';

const client = createWebSocketClient();

// Subscribe to all trades
client.stocks.subscribe('T.*');

// Alternative: specific tickers
// client.stocks.subscribe('T.AAPL', 'T.TSLA');

console.log('[Trades] Starting trade stream...');
console.log('[Trades] Press Ctrl+C to stop');

client.stocks.onmessage = createTradeHandler('Trades') as (messages: unknown[]) => void;

// Handle errors
client.stocks.onerror = (error: Error) => {
  console.error('[Trades] WebSocket error:', error);
};

// Handle close
client.stocks.onclose = () => {
  console.log('[Trades] WebSocket connection closed');
};
```

### REQ-WS-TS-004: Quotes Stream
**Description:** Real-time quote streaming.

**File:** `src/websocket/streams/quotes.ts`
```typescript
import { createWebSocketClient } from '../client';
import { createQuoteHandler, StreamMessage } from '../handlers/messageHandler';

const client = createWebSocketClient();

// Subscribe to all quotes
client.stocks.subscribe('Q.*');

// Alternative: specific tickers
// client.stocks.subscribe('Q.AAPL', 'Q.TSLA');

console.log('[Quotes] Starting quote stream...');
console.log('[Quotes] Press Ctrl+C to stop');

client.stocks.onmessage = createQuoteHandler('Quotes') as (messages: unknown[]) => void;

client.stocks.onerror = (error: Error) => {
  console.error('[Quotes] WebSocket error:', error);
};

client.stocks.onclose = () => {
  console.log('[Quotes] WebSocket connection closed');
};
```

### REQ-WS-TS-005: Minute Aggregates Stream
**Description:** Per-minute aggregate bar streaming.

**File:** `src/websocket/streams/aggregatesMin.ts`
```typescript
import { createWebSocketClient } from '../client';
import { createAggregateHandler, StreamMessage } from '../handlers/messageHandler';

const client = createWebSocketClient();

// Subscribe to minute aggregates
client.stocks.subscribe('AM.*');

// Alternative: specific tickers
// client.stocks.subscribe('AM.AAPL', 'AM.TSLA');

console.log('[Aggregates-Min] Starting minute aggregate stream...');
console.log('[Aggregates-Min] Press Ctrl+C to stop');

client.stocks.onmessage = createAggregateHandler('Aggregates-Min') as (messages: unknown[]) => void;

client.stocks.onerror = (error: Error) => {
  console.error('[Aggregates-Min] WebSocket error:', error);
};

client.stocks.onclose = () => {
  console.log('[Aggregates-Min] WebSocket connection closed');
};
```

### REQ-WS-TS-006: Second Aggregates Stream
**Description:** Per-second aggregate bar streaming.

**File:** `src/websocket/streams/aggregatesSec.ts`
```typescript
import { createWebSocketClient } from '../client';
import { createAggregateHandler, StreamMessage } from '../handlers/messageHandler';

const client = createWebSocketClient();

// Subscribe to second aggregates
client.stocks.subscribe('A.*');

// Alternative: specific tickers
// client.stocks.subscribe('A.AAPL', 'A.TSLA');

console.log('[Aggregates-Sec] Starting second aggregate stream...');
console.log('[Aggregates-Sec] Press Ctrl+C to stop');

client.stocks.onmessage = createAggregateHandler('Aggregates-Sec') as (messages: unknown[]) => void;

client.stocks.onerror = (error: Error) => {
  console.error('[Aggregates-Sec] WebSocket error:', error);
};

client.stocks.onclose = () => {
  console.log('[Aggregates-Sec] WebSocket connection closed');
};
```

## Acceptance Criteria
- [ ] WebSocket client connects to Polygon
- [ ] Trades stream receives and logs trades
- [ ] Quotes stream receives and logs quotes
- [ ] Minute aggregates stream works
- [ ] Second aggregates stream works
- [ ] Graceful handling of connection errors

## Deliverables
1. `src/websocket/client.ts` - WebSocket client factory
2. `src/websocket/handlers/messageHandler.ts` - Message handlers
3. `src/websocket/streams/trades.ts`
4. `src/websocket/streams/quotes.ts`
5. `src/websocket/streams/aggregatesMin.ts`
6. `src/websocket/streams/aggregatesSec.ts`

## Testing Commands
```bash
# Run trades stream
npm run dev:ws:trades

# Run quotes stream
npm run dev:ws:quotes
```

---

# SESSION 8: Testing & Quality

## Goal
Add comprehensive test coverage for all components.

## Prerequisites
- Sessions 1-7 completed
- Jest configuration in place

## Requirements

### REQ-TEST-TS-001: Jest Configuration
**Description:** Configure Jest for TypeScript testing.

**File:** `jest.config.js`
```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.test.ts'],
  moduleFileExtensions: ['ts', 'js', 'json'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/__tests__/**',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov'],
};
```

### REQ-TEST-TS-002: Mock Polygon Responses
**Description:** Create mock data for testing.

**File:** `src/__tests__/mocks/polygonResponses.ts`
```typescript
export const mockTickerPriceResponse = {
  data: {
    results: [
      {
        c: 150.25,
        t: 1703894400000,
      },
    ],
  },
};

export const mockTickerDetailsResponse = {
  data: {
    results: {
      name: 'Apple Inc.',
      primary_exchange: 'NASDAQ',
      locale: 'us',
      market: 'stocks',
      type: 'CS',
    },
  },
};

export const mockLastTradeResponse = {
  data: {
    results: {
      p: 150.50,
      s: 100,
      t: 1703894400000,
    },
  },
};

export const mockLastQuoteResponse = {
  data: {
    results: {
      ap: 150.55,
      as: 200,
      bp: 150.45,
      bs: 300,
      t: 1703894400000,
    },
  },
};
```

### REQ-TEST-TS-003: Timestamp Utility Tests
**Description:** Unit tests for timestamp utilities.

**File:** `src/__tests__/agent/timestamp.test.ts`
```typescript
import { currentEpochMs, datetimeFromEpochMs, formatTimestamp } from '../../agent/utils/timestamp';

describe('Timestamp Utilities', () => {
  describe('currentEpochMs', () => {
    it('should return current time in milliseconds', () => {
      const result = currentEpochMs();
      expect(typeof result).toBe('number');
      expect(result).toBeGreaterThan(0);
    });
  });

  describe('datetimeFromEpochMs', () => {
    it('should convert epoch ms to Date object', () => {
      const epochMs = 1703894400000; // 2023-12-30 00:00:00 UTC
      const result = datetimeFromEpochMs(epochMs);
      expect(result).toBeInstanceOf(Date);
    });
  });

  describe('formatTimestamp', () => {
    it('should format timestamp correctly', () => {
      const epochMs = 1703894400000;
      const result = formatTimestamp(epochMs);
      expect(typeof result).toBe('string');
      expect(result).toMatch(/\d{4}-\d{2}-\d{2}/);
    });
  });
});
```

### REQ-TEST-TS-004: Request Schema Tests
**Description:** Unit tests for Zod validation schemas.

**File:** `src/__tests__/mcp-server/schemas.test.ts`
```typescript
import {
  StockRequestSchema,
  AggregatesRequestSchema,
} from '../../mcp-server/schemas/requests';

describe('Request Schemas', () => {
  describe('StockRequestSchema', () => {
    it('should validate valid ticker', () => {
      const result = StockRequestSchema.parse({ ticker: 'aapl' });
      expect(result.ticker).toBe('AAPL'); // Should be uppercase
    });

    it('should reject empty ticker', () => {
      expect(() => StockRequestSchema.parse({ ticker: '' })).toThrow();
    });

    it('should reject missing ticker', () => {
      expect(() => StockRequestSchema.parse({})).toThrow();
    });
  });

  describe('AggregatesRequestSchema', () => {
    it('should validate complete request', () => {
      const input = {
        ticker: 'aapl',
        multiplier: 1,
        timespan: 'day',
        from_date: '2024-01-01',
        to_date: '2024-01-31',
        limit: 10,
      };
      const result = AggregatesRequestSchema.parse(input);
      expect(result.ticker).toBe('AAPL');
      expect(result.timespan).toBe('day');
    });

    it('should reject invalid date format', () => {
      const input = {
        ticker: 'aapl',
        multiplier: 1,
        timespan: 'day',
        from_date: '01-01-2024', // Wrong format
        to_date: '2024-01-31',
        limit: 10,
      };
      expect(() => AggregatesRequestSchema.parse(input)).toThrow();
    });

    it('should reject invalid timespan', () => {
      const input = {
        ticker: 'aapl',
        multiplier: 1,
        timespan: 'invalid',
        from_date: '2024-01-01',
        to_date: '2024-01-31',
        limit: 10,
      };
      expect(() => AggregatesRequestSchema.parse(input)).toThrow();
    });
  });
});
```

### REQ-TEST-TS-005: Response Formatter Tests
**Description:** Unit tests for response formatting.

**File:** `src/__tests__/agent/responseFormatter.test.ts`
```typescript
import { formatToolResponse } from '../../agent/utils/responseFormatter';

describe('Response Formatter', () => {
  describe('get_ticker_price', () => {
    it('should format stock price response', () => {
      const result = formatToolResponse('get_ticker_price', {
        ticker: 'AAPL',
        price: 150.25,
        timestamp: 1703894400000,
      });
      expect(result).toContain('AAPL');
      expect(result).toContain('$150.25');
    });
  });

  describe('get_ticker_details', () => {
    it('should format ticker details response', () => {
      const result = formatToolResponse('get_ticker_details', {
        name: 'Apple Inc.',
        type: 'CS',
        primary_exchange: 'NASDAQ',
        market: 'stocks',
        locale: 'us',
      });
      expect(result).toContain('Apple Inc.');
      expect(result).toContain('NASDAQ');
    });
  });

  describe('unknown tool', () => {
    it('should return JSON for unknown tools', () => {
      const data = { foo: 'bar' };
      const result = formatToolResponse('unknown_tool', data as never);
      expect(result).toBe(JSON.stringify(data));
    });
  });
});
```

## Acceptance Criteria
- [ ] Jest runs without configuration errors
- [ ] All utility functions have tests
- [ ] Schema validation tests pass
- [ ] Response formatter tests pass
- [ ] Test coverage report generated

## Deliverables
1. `jest.config.js` - Jest configuration
2. `src/__tests__/mocks/polygonResponses.ts` - Mock data
3. `src/__tests__/agent/timestamp.test.ts`
4. `src/__tests__/mcp-server/schemas.test.ts`
5. `src/__tests__/agent/responseFormatter.test.ts`

## Testing Commands
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- timestamp.test.ts
```

---

# SESSION 9: Enhancements & Documentation

## Goal
Add production-ready enhancements and documentation.

## Prerequisites
- Sessions 1-8 completed
- All components functional

## Requirements

### REQ-ENH-TS-001: Conversation Loop
**Description:** Enable multi-turn conversations with context.

**File:** `src/agent/cli.ts` (updated)
```typescript
import * as readline from 'readline';
import { runAgentWithHistory } from './core/agentLoop';
import { Message } from './types';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

let conversationHistory: Message[] = [];

const askQuestion = (): void => {
  rl.question('\n> ', async (input) => {
    const question = input.trim();

    if (!question) {
      askQuestion();
      return;
    }

    if (question.toLowerCase() === 'exit' || question.toLowerCase() === 'quit') {
      console.log('Goodbye!');
      rl.close();
      process.exit(0);
    }

    if (question.toLowerCase() === 'clear') {
      conversationHistory = [];
      console.log('Conversation history cleared.');
      askQuestion();
      return;
    }

    try {
      const { response, history } = await runAgentWithHistory(question, conversationHistory);
      conversationHistory = history;
      console.log('\n' + response);
    } catch (error) {
      console.error('Error:', error instanceof Error ? error.message : error);
    }

    askQuestion();
  });
};

console.log('GameStocks Agent - Node.js Edition');
console.log('Commands: "exit" to quit, "clear" to reset conversation\n');
askQuestion();
```

### REQ-ENH-TS-002: Graceful Shutdown
**Description:** Handle process termination gracefully.

**File:** `src/mcp-server/index.ts` (add shutdown handling)
```typescript
// Add at the end of the file
const shutdown = (): void => {
  console.log('\n[MCP Server] Shutting down gracefully...');
  process.exit(0);
};

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
```

### REQ-ENH-TS-003: Rate Limiting
**Description:** Add rate limiting middleware for API endpoints.

**File:** `src/mcp-server/middleware/rateLimiter.ts`
```typescript
import { Request, Response, NextFunction } from 'express';

interface RateLimitStore {
  [key: string]: {
    count: number;
    resetTime: number;
  };
}

const store: RateLimitStore = {};
const WINDOW_MS = 60000; // 1 minute
const MAX_REQUESTS = 30; // 30 requests per minute

export const rateLimiter = (req: Request, res: Response, next: NextFunction): void => {
  const ip = req.ip || 'unknown';
  const now = Date.now();

  if (!store[ip] || now > store[ip].resetTime) {
    store[ip] = {
      count: 1,
      resetTime: now + WINDOW_MS,
    };
    next();
    return;
  }

  store[ip].count++;

  if (store[ip].count > MAX_REQUESTS) {
    res.status(429).json({
      error: 'Too many requests',
      detail: 'Rate limit exceeded. Please try again later.',
    });
    return;
  }

  next();
};
```

### REQ-ENH-TS-004: Docker Configuration
**Description:** Containerize the application.

**File:** `Dockerfile`
```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY dist ./dist
COPY .env.template ./.env.template

EXPOSE 8080

CMD ["node", "dist/mcp-server/index.js"]
```

**File:** `docker-compose.yml`
```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8080:8080"
    environment:
      - POLYGON_API_KEY=${POLYGON_API_KEY}
      - MCP_SERVER_PORT=8080
      - MCP_SERVER_LOG_ENABLED=true
    restart: unless-stopped
```

### REQ-ENH-TS-005: Project README
**Description:** Comprehensive README for the Node.js version.

**File:** `README.md`
```markdown
# GameStocks - Node.js Edition

A conversational AI interface for querying real-time stock market data using natural language.

## Features

- Natural language stock queries via Claude AI
- Real-time stock data from Polygon.io
- WebSocket streaming for live market data
- TypeScript with full type safety
- Express.js REST API server

## Quick Start

### Prerequisites

- Node.js 18+
- Polygon.io API key
- Anthropic API key

### Installation

```bash
npm install
cp .env.template .env
# Edit .env with your API keys
```

### Running

```bash
# Start MCP Server
npm run dev:server

# Start Agent (in another terminal)
npm run dev:agent

# Run WebSocket streams
npm run dev:ws:trades
npm run dev:ws:quotes
```

### Testing

```bash
npm test
npm test -- --coverage
```

## Architecture

```
┌─────────────┐     HTTP      ┌─────────────┐     REST      ┌─────────────┐
│   Agent     │ ◄──────────►  │ MCP Server  │ ◄──────────►  │ Polygon.io  │
│  (Claude)   │               │  (Express)  │               │    API      │
└─────────────┘               └─────────────┘               └─────────────┘
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /get_tool_defs | GET | Get tool definitions |
| /tools/get_ticker_price | POST | Get stock price |
| /tools/get_ticker_details | POST | Get company info |
| /tools/get_last_trade | POST | Get last trade |
| /tools/get_last_quote | POST | Get NBBO quote |
| /tools/get_aggregates | POST | Get OHLCV bars |
| /tools/get_historic_trades | POST | Get trade history |

## License

MIT
```

## Acceptance Criteria
- [ ] Conversation history maintained between questions
- [ ] Server shuts down gracefully on SIGTERM/SIGINT
- [ ] Rate limiting prevents abuse
- [ ] Docker build succeeds
- [ ] README comprehensive and accurate

## Deliverables
1. Updated `src/agent/cli.ts` with conversation loop
2. `src/mcp-server/middleware/rateLimiter.ts`
3. `Dockerfile`
4. `docker-compose.yml`
5. `README.md`

---

# Summary

## Session Checklist

| Session | Component | Status |
|---------|-----------|--------|
| 1 | Project Foundation & Setup | ⬜ |
| 2 | MCP Server - Core Infrastructure | ⬜ |
| 3 | MCP Server - Stock Tools Part 1 | ⬜ |
| 4 | MCP Server - Stock Tools Part 2 | ⬜ |
| 5 | AI Agent - Core Infrastructure | ⬜ |
| 6 | AI Agent - Execution Loop | ⬜ |
| 7 | WebSocket Streaming | ⬜ |
| 8 | Testing & Quality | ⬜ |
| 9 | Enhancements & Documentation | ⬜ |

## Total Estimated Time
- **Minimum:** ~9 hours (1 hour per session)
- **Maximum:** ~18 hours (2 hours per session)

## Key Commands Reference

```bash
# Development
npm run dev:server          # Start MCP server with hot reload
npm run dev:agent           # Start agent CLI
npm run dev:ws:trades       # Start trades WebSocket stream
npm run dev:ws:quotes       # Start quotes WebSocket stream

# Production
npm run build               # Compile TypeScript
npm run start:server        # Run compiled server
npm run start:agent         # Run compiled agent

# Testing
npm test                    # Run all tests
npm test -- --coverage      # Run tests with coverage

# Docker
docker-compose up -d        # Start containerized server
docker-compose logs -f      # View logs
```

---

**Document End**
