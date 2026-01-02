import logging
from anthropic import Anthropic
from dotenv import load_dotenv
import json
import os
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

load_dotenv()

# Configure logging
LOG_ENABLED = os.getenv("AGENT_LOG_ENABLED", "true").lower() == "true"
logging.basicConfig(
    level=logging.INFO if LOG_ENABLED else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MCP_BASE_URL = "http://localhost:8080"
MODEL = "claude-sonnet-4-20250514"

# Load tool definitions from MCP server
logger.info("Initializing agent...")
logger.info(f"Connecting to MCP server at {MCP_BASE_URL}")
try:
    response = requests.get(f"{MCP_BASE_URL}/get_tool_defs")
    response.raise_for_status()
    mcp_config = response.json()
    mcp_tools = {tool["id"]: tool for tool in mcp_config["tools"]}
    logger.info(f"Loaded {len(mcp_tools)} tools from MCP server: {list(mcp_tools.keys())}")
except Exception as e:
    logger.error(f"Failed to fetch tool definitions from MCP server: {e}")
    raise


def convert_to_anthropic_tools(mcp_tools_dict):
    """Convert MCP tool definitions to Anthropic tool format."""
    anthropic_tools = []
    for tool_id, tool in mcp_tools_dict.items():
        anthropic_tools.append({
            "name": tool_id,
            "description": tool["description"],
            "input_schema": tool["input_schema"]
        })
    return anthropic_tools


def current_epoch_ms(timezone_str: str = "UTC") -> int:
    now = datetime.now(ZoneInfo(timezone_str))
    return int(now.timestamp() * 1000)


def datetime_from_epochts(epoch_ts_ms, timezone_str):
    dt = datetime.fromtimestamp(epoch_ts_ms / 1000, tz=timezone.utc)
    return dt.astimezone(ZoneInfo(timezone_str))


def call_mcp_tool(tool_id: str, args: dict):
    url = f"{MCP_BASE_URL}/tools/{tool_id}"
    logger.info(f"Calling MCP tool: {tool_id}")
    logger.info(f"MCP request URL: {url}")
    logger.info(f"MCP request params: {json.dumps(args)}")
    try:
        response = requests.post(url, json=args)
        response.raise_for_status()
        result = response.json()
        logger.info(f"MCP response received for {tool_id}")
        return result
    except requests.HTTPError as e:
        try:
            error_detail = e.response.json()
        except Exception:
            error_detail = e.response.text
        logger.error(f"MCP Server Error {e.response.status_code}: {error_detail}")
        raise RuntimeError(f"{tool_id} failed - {error_detail}") from e


def formatted_tool_response(tool_id: str, result: dict):
    try:
        if tool_id == "get_stock_price":
            dt = datetime_from_epochts(result["timestamp"], "America/Los_Angeles")
            return f"Ticker: {result['ticker']}, Price: ${result['price']}, Time: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}"

        elif tool_id == "get_ticker_details":
            return f"{result['name']} ({result['type']} on {result['exchange']}) - Market: {result['market']}, Locale: {result['locale']}"

        elif tool_id == "get_last_trade":
            dt = datetime_from_epochts(result["timestamp"], "America/Los_Angeles")
            return f"Last trade: ${result['price']} (Size: {result['size']}) at {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}"

        elif tool_id == "get_last_quote":
            dt = datetime_from_epochts(result["timestamp"], "America/Los_Angeles")
            return (
                f"Bid: ${result['bidprice']} ({result['bidsize']}), "
                f"Ask: ${result['askprice']} ({result['asksize']}), "
                f"Time: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )

        elif tool_id == "get_aggregates":
            first = result["results"][0] if result["results"] else {}
            return f"OHLC: {first.get('o')}, {first.get('h')}, {first.get('l')}, {first.get('c')} - Volume: {first.get('v')}"

        elif tool_id == "get_historic_trades":
            trade = result["results"][0] if result["results"] else {}
            dt = datetime_from_epochts(trade.get("t", 0), "America/Los_Angeles")
            return f"Trade: Price ${trade.get('p')}, Size {trade.get('s')} at {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}"

        else:
            return json.dumps(result)

    except Exception as e:
        logger.warning(f"Error formatting result: {e}")
        return json.dumps(result)


def run_agent(user_question):
    logger.info("=" * 60)
    logger.info("Starting new agent run")
    logger.info(f"User question: {user_question}")

    tools = convert_to_anthropic_tools(mcp_tools)
    logger.info(f"Converted {len(tools)} tools for Anthropic API")

    messages = [
        {"role": "user", "content": user_question}
    ]

    system_prompt = """You are a financial assistant with access to stock data tools.
When the user asks about stock prices or financial data, use the available tools to fetch real-time information.
Always provide clear, helpful responses based on the data you retrieve."""

    # Initial request - Claude may request tool use
    logger.info(f"Sending initial request to Claude ({MODEL})")
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        tools=tools,
        messages=messages
    )
    logger.info(f"Received response - stop_reason: {response.stop_reason}")

    # Process response - handle tool use if requested
    iteration = 0
    while response.stop_reason == "tool_use":
        iteration += 1
        logger.info(f"Tool use iteration {iteration}")

        # Find tool use blocks in the response
        tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
        logger.info(f"Claude requested {len(tool_use_blocks)} tool(s)")

        # Add assistant's response to messages
        messages.append({"role": "assistant", "content": response.content})

        # Process each tool call and collect results
        tool_results = []
        for tool_use in tool_use_blocks:
            tool_name = tool_use.name
            tool_input = tool_use.input
            tool_use_id = tool_use.id

            logger.info(f"Processing tool: {tool_name} (id: {tool_use_id})")
            logger.info(f"Tool parameters: {json.dumps(tool_input, indent=2)}")

            try:
                # Call the MCP server
                mcp_result = call_mcp_tool(tool_name, tool_input)
                formatted = formatted_tool_response(tool_name, mcp_result)
                logger.info(f"Tool result: {formatted}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": json.dumps(mcp_result)
                })
                logger.info(f"Tool {tool_name} completed successfully")
            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {e}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": f"Error: {str(e)}",
                    "is_error": True
                })

        # Add tool results to messages
        messages.append({"role": "user", "content": tool_results})
        logger.info("Sending tool results back to Claude")

        # Continue the conversation with tool results
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system_prompt,
            tools=tools,
            messages=messages
        )
        logger.info(f"Received response - stop_reason: {response.stop_reason}")

    # Extract and print final text response
    logger.info("Extracting final response")
    final_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            final_text += block.text

    logger.info(f"Agent run completed after {iteration} tool iteration(s)")
    logger.info("=" * 60)

    print("\nResponse:")
    print(final_text)
    return final_text


if __name__ == "__main__":
    q = input("Ask a stock-related question:\n> ")
    run_agent(q)
