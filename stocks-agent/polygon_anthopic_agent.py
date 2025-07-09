from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from dotenv import load_dotenv
import json
import re
import os
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MCP_BASE_URL = "http://localhost:8080"

# Load tool definitions from MCP server
try:
    response = requests.get(f"{MCP_BASE_URL}/get_tool_defs")
    response.raise_for_status()
    mcp_config = response.json()
    tools = {tool["id"]: tool for tool in mcp_config["tools"]}
except Exception as e:
    print(f"❌ Failed to fetch tool definitions from MCP server: {e}")
    raise


def current_epoch_ms(timezone_str: str = "UTC") -> int:
    now = datetime.now(ZoneInfo(timezone_str))
    return int(now.timestamp() * 1000)


def datetime_from_epochts(epoch_ts_ms, timezone_str):
    dt = datetime.fromtimestamp(epoch_ts_ms / 1000, tz=timezone.utc)
    return dt.astimezone(ZoneInfo(timezone_str))


def call_mcp_tool(tool_id: str, args: dict):
    url = f"{MCP_BASE_URL}/tools/{tool_id}"
    print(f"\n📡 Calling MCP: {url} with {args}")
    try:
        response = requests.post(url, json=args)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        try:
            error_detail = e.response.json()
        except Exception:
            error_detail = e.response.text
        print(f"❌ MCP Server Error {e.response.status_code}: {error_detail}")
        raise RuntimeError(f"{tool_id} failed — {error_detail}") from e


def build_prompt_all_tools(user_input, tools_dict):
    now_ts = current_epoch_ms("America/Los_Angeles")
    tools_list = list(tools_dict.values())

    tools_description = "\n".join([
        f"- {tool['id']}: {tool['description']}\n  Input Schema:\n{json.dumps(tool['input_schema'], indent=2)}"
        for tool in tools_list
    ])

    # Optional: Inject example input with timestamp
    examples = ""
    for tool in tools_list:
        example_params = {}
        for key in tool["input_schema"]["properties"]:
            if key == "ticker":
                example_params[key] = "AAPL"
            elif key == "timestamp":
                example_params[key] = now_ts
            elif key == "date":
                example_params[key] = "2024-06-01"
            elif key == "multiplier":
                example_params[key] = 1
            elif key == "timespan":
                example_params[key] = "day"
            elif key == "from_date":
                example_params[key] = "2024-06-01"
            elif key == "to_date":
                example_params[key] = "2024-06-18"
            elif key == "limit":
                example_params[key] = 1
            else:
                example_params[key] = "..."

        example_call = json.dumps({
            "tool_call": {
                "tool_id": tool["id"],
                "parameters": example_params
            }
        }, indent=2)

        examples += f"\nExample for {tool['id']}:\n{example_call}\n"

    # Key Prompt to focus on 
    return (
        HUMAN_PROMPT
        + "You are a financial assistant with access to stock data tools.\n"
        + "Available tools:\n"
        + tools_description
        + "\n\nWhen using a tool, respond ONLY with JSON like:\n"
        + '{"tool_call": {"tool_id": "<TOOL_ID>", "parameters": {...}}}\n'
        + "No explanations — just valid JSON.\n"
        + f"User question: {user_input}\n"
        + examples
        + AI_PROMPT
    )


def formatted_tool_response(tool_id: str, result: dict):
    try:
        if tool_id == "get_stock_price":
            dt = datetime_from_epochts(result["timestamp"], "America/Los_Angeles")
            return f"Ticker: {result['ticker']}, Price: {result['price']}, Time: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}"

        elif tool_id == "get_ticker_details":
            return f"{result['name']} ({result['type']} on {result['exchange']}) — Market: {result['market']}, Locale: {result['locale']}"

        elif tool_id == "get_last_trade":
            dt = datetime_from_epochts(result["timestamp"], "America/Los_Angeles")
            return f"Last trade: {result['price']} (Size: {result['size']}) at {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}"

        elif tool_id == "get_last_quote":
            dt = datetime_from_epochts(result["timestamp"], "America/Los_Angeles")
            return (
                f"Bid: {result['bidprice']} ({result['bidsize']}), "
                f"Ask: {result['askprice']} ({result['asksize']}), "
                f"Time: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )

        elif tool_id == "get_aggregates":
            first = result["results"][0] if result["results"] else {}
            return f"OHLC: {first.get('o')}, {first.get('h')}, {first.get('l')}, {first.get('c')} — Volume: {first.get('v')}"

        elif tool_id == "get_historic_trades":
            trade = result["results"][0] if result["results"] else {}
            dt = datetime_from_epochts(trade.get("t", 0), "America/Los_Angeles")
            return f"Trade: Price {trade.get('p')}, Size {trade.get('s')} at {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}"

        else:
            return json.dumps(result)

    except Exception as e:
        print("⚠️ Error formatting result:", e)
        return json.dumps(result)


def run_agent(user_question):
    prompt = build_prompt_all_tools(user_question, tools)

    response = client.completions.create(
        model="claude-2",
        prompt=prompt,
        max_tokens_to_sample=1000,
        stop_sequences=[HUMAN_PROMPT]
    )

    text = response.completion.strip()
    match = re.search(r'(\{.*"tool_call".*\})', text, re.DOTALL)
    if match:
        raw_json = match.group().strip()
        open_braces = raw_json.count("{")
        close_braces = raw_json.count("}")
        if open_braces > close_braces:
            raw_json += "}" * (open_braces - close_braces)

        try:
            call_data = json.loads(raw_json)
            tool_call = call_data.get("tool_call", {})
            tool_id = tool_call.get("tool_id")
            params = tool_call.get("parameters", {})

            if not tool_id:
                raise ValueError("Missing tool_id in tool_call")

            mcp_result = call_mcp_tool(tool_id, params)
            print(f"\n✅ Tool Response:\n{formatted_tool_response(tool_id, mcp_result)}")

            followup_prompt = (
                HUMAN_PROMPT
                + f"The user asked: {user_question}\n"
                + f"The tool returned this result: {json.dumps(mcp_result)}\n"
                + f"Please provide the final answer based on this.\n"
                + AI_PROMPT
            )

            final_response = client.completions.create(
                model="claude-2",
                prompt=followup_prompt,
                max_tokens_to_sample=1000,
                stop_sequences=[HUMAN_PROMPT]
            )

            print("\n💬 Final Response from LLM:")
            print(final_response.completion.strip())

        except Exception as e:
            print(f"❌ Error processing tool call:\n{e}")
            print(f"⚠️ Claude Response: {text}")

    else:
        print("❌ Claude did not return a valid tool_call block:")
        print(text)


if __name__ == "__main__":
    q = input("Ask a stock-related question:\n> ")
    run_agent(q)
