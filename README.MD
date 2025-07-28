## What is this?
The repo has two components 1) An MCP Server that can work with agent to fetch stock price and 2) an MCP Agent that can converts user question regarding stock price, works with MCP server to fetch stock price and gives response.

### Pre Requisites
1. Anthropic API Key
2. Polygon API Key

### Steps

1. Clone the repo. Go to the folder.
1. Copy the .env_template to new file and name it .env
3. Fill in your API keys in the .env file
4. While at the top level folder, create a python virtual environment with necessary libraries using following commands

```
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

5. To Run MCP Server, go to folder stocks-mcp-server and run following command
```
uvicorn main:app --reload --port 8080
```

6. Verify MCP Server end point is working as expected using following command
```
curl -X POST http://localhost:8080/tools/get_stock_price \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AMZN"}'
```

7. To use agent open another terminal, go to stocks-agent and run following command
```
python polygon_anthopic_agent.py
```
8. To check that everything is set up correctly end to end, give a question like the following one in the Terminal that is running agent
```
What is the stock price of Elon Musk's company?
```

This should return TSLA stock price


### Limitations 

1. Code in the following folders is work in progress and not functional.
```
stocks-polygon-ws-stream
```
2. Only one tool get stock price is FREE from Polygon, other tools like get historical prices don't work at the moment.


Timeline
7.28 - Understand the agent code fully, understand the MCP Server code fully. Enable follow up questions by adding a loop & context
