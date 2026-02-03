# Python Code Executor Telegram Bot

A powerful Telegram bot that executes Python code with full library support including crypto/blockchain, networking, and data processing. Perfect for running crypto scripts, checking wallet balances, API calls, and more.

## Features

- **Full Python Execution**: Run any Python code without restrictions
- **Crypto Libraries**: web3, solana, solders, bitcoinlib, eth-account, and more
- **Network Access**: Make HTTP requests to APIs (blockchain explorers, etc.)
- **Timeout Protection**: Configurable timeout (default 60s)
- **User Authorization**: Optional whitelist for allowed users
- **Pre-installed Libraries**: numpy, pandas, requests, aiohttp, and crypto packages

## Quick Deploy to Railway

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the prompts
3. Copy the API token you receive

### 2. Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

Or manually:
1. Push this code to a GitHub repository
2. Go to [railway.app](https://railway.app)
3. Create a new project and select "Deploy from GitHub repo"
4. Select your repository

### 3. Configure Environment Variables

In Railway dashboard, add these environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Your bot token from BotFather |
| `ALLOWED_USERS` | No | Comma-separated Telegram user IDs (empty = public access) |
| `EXECUTION_TIMEOUT` | No | Max execution time in seconds (default: 60) |

## Usage

### Commands

- `/start` - Welcome message and instructions
- `/run <code>` - Execute Python code
- `/libs` - List available libraries
- `/id` - Get your Telegram user ID

### Direct Messages

Just send Python code directly to the bot - it will detect and execute it automatically.

### Examples

**Check Solana Balance:**

```python
import requests

address = "YOUR_SOLANA_ADDRESS"
url = "https://api.mainnet-beta.solana.com"
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getBalance",
    "params": [address]
}
response = requests.post(url, json=payload)
balance = response.json()["result"]["value"] / 1e9
print(f"Balance: {balance} SOL")
```

**Check Ethereum Balance:**

```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
address = "YOUR_ETH_ADDRESS"
balance = w3.eth.get_balance(address)
print(f"Balance: {w3.from_wei(balance, 'ether')} ETH")
```

**Check Bitcoin Balance:**

```python
import requests

address = "YOUR_BTC_ADDRESS"
url = f"https://blockchain.info/q/addressbalance/{address}"
satoshis = int(requests.get(url).text)
btc = satoshis / 100000000
print(f"Balance: {btc} BTC")
```

**Data Processing:**

```python
import numpy as np
import pandas as pd

data = {'prices': [100, 150, 120, 180, 200]}
df = pd.DataFrame(data)
print(f"Mean: {df['prices'].mean()}")
print(f"Max: {df['prices'].max()}")
```

## Installed Libraries

### Crypto & Blockchain
- `web3` - Ethereum interaction
- `solana`, `solders` - Solana blockchain
- `base58` - Base58 encoding
- `eth-account` - Ethereum accounts
- `bitcoinlib` - Bitcoin utilities
- `blockcypher` - Blockchain API client
- `pycryptodome` - Cryptographic functions

### HTTP & Networking
- `requests` - HTTP requests
- `aiohttp` - Async HTTP
- `httpx` - Modern HTTP client

### Data Processing
- `numpy` - Numerical computing
- `pandas` - Data analysis

### Standard Library
All Python standard library modules are available.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your-token-here"

# Run the bot
python bot.py
```

## Security Notes

- Use `ALLOWED_USERS` in production to restrict who can run code
- The bot has full network access - be mindful of API rate limits
- Monitor your Railway usage for unexpected resource consumption

## License

MIT License - feel free to modify and deploy!
