# Python Code Executor Telegram Bot

A powerful Telegram bot that executes Python code with full library support including crypto/blockchain, networking, and data processing. Perfect for running crypto scripts, checking wallet balances, API calls, and more.

## Features

- **Full Python Execution**: Run any Python code without restrictions
- **Crypto Libraries**: web3, solana, bitcoinlib, ccxt, and 30+ more
- **Network Access**: Make HTTP requests to APIs (blockchain explorers, exchanges, etc.)
- **Timeout Protection**: Configurable timeout (default 60s)
- **User Authorization**: Optional whitelist for allowed users

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

**Get Crypto Prices (CoinGecko):**

```python
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()
prices = cg.get_price(ids='bitcoin,ethereum,solana', vs_currencies='usd')
for coin, data in prices.items():
    print(f"{coin.upper()}: ${data['usd']:,.2f}")
```

**Check Exchange Balance (CCXT):**

```python
import ccxt

exchange = ccxt.binance({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET'
})
balance = exchange.fetch_balance()
print(balance['total'])
```

**Generate HD Wallet:**

```python
from hdwallet import HDWallet
from hdwallet.symbols import ETH

hdwallet = HDWallet(symbol=ETH)
hdwallet.from_mnemonic("your twelve word mnemonic phrase here")
hdwallet.from_path("m/44'/60'/0'/0/0")
print(f"Address: {hdwallet.p2pkh_address()}")
print(f"Private Key: {hdwallet.private_key()}")
```

## Installed Libraries

### Ethereum
- `web3` - Ethereum interaction
- `eth-account` - Account management
- `eth-abi` - ABI encoding/decoding
- `eth-utils` - Utility functions

### Solana
- `solana` - Solana client
- `solders` - Low-level Solana primitives

### Bitcoin
- `bitcoinlib` - Bitcoin utilities
- `blockcypher` - Blockchain API

### Other Chains
- `tronpy` - Tron blockchain
- `xrpl-py` - XRP Ledger
- `stellar-sdk` - Stellar network

### Wallets & Keys
- `hdwallet` - HD wallet (BIP32/39/44)
- `mnemonic` - Seed phrase generation
- `base58` - Base58 encoding
- `bip32utils` - BIP32 utilities

### Cryptography
- `pycryptodome` - Crypto primitives
- `coincurve` - secp256k1 operations
- `pynacl` - Ed25519/NaCl
- `ecdsa` - ECDSA signing
- `cryptography` - General crypto

### Exchange APIs
- `ccxt` - 100+ exchanges unified API
- `python-binance` - Binance API
- `pycoingecko` - Price data

### HTTP & Networking
- `requests` - HTTP client
- `aiohttp` - Async HTTP
- `httpx` - Modern HTTP
- `websockets` - WebSocket client

### Data Processing
- `numpy` - Numerical computing
- `pandas` - Data analysis

### Standard Library
All Python standard library modules are available.

## AI System Prompt

Use this system prompt with ChatGPT, Claude, or other AI assistants to generate Python scripts compatible with this bot:

```
You are a Python script generator for a Telegram bot that executes Python code. Generate scripts that are self-contained, print their output, and work within a 60-second timeout.

INSTALLED LIBRARIES:

Ethereum/EVM:
- web3 (Web3, Account, Contract interaction)
- eth-account (Account, signing)
- eth-abi (encode_abi, decode_abi)
- eth-utils (to_checksum_address, from_wei, to_wei)

Solana:
- solana (Client, Keypair, PublicKey, Transaction)
- solders (low-level primitives)

Bitcoin:
- bitcoinlib (keys, transactions, wallets)
- blockcypher (API client)

Other Blockchains:
- tronpy (Tron)
- xrpl-py (XRP Ledger)
- stellar-sdk (Stellar)

Wallet Generation:
- hdwallet (HDWallet - BIP32/BIP39/BIP44 HD wallets)
- mnemonic (Mnemonic - seed phrase generation)
- bip32utils (BIP32 key derivation)
- base58 (encoding/decoding)

Cryptography:
- pycryptodome (AES, RSA, SHA256, etc. - import from Crypto)
- coincurve (fast secp256k1 - PrivateKey, PublicKey)
- pynacl (Ed25519, Box, SecretBox - import from nacl)
- ecdsa (ECDSA signing - SigningKey, VerifyingKey)
- cryptography (general purpose crypto)

Exchange APIs:
- ccxt (100+ exchanges: ccxt.binance(), ccxt.coinbase(), etc.)
- python-binance (Binance - Client)
- pycoingecko (CoinGeckoAPI - price data)

HTTP/Networking:
- requests (requests.get, requests.post)
- aiohttp (async HTTP)
- httpx (modern HTTP client)
- websockets (WebSocket connections)

Data Processing:
- numpy (np.array, numerical operations)
- pandas (pd.DataFrame, data analysis)
- json (built-in)
- re (regex, built-in)

RULES:
1. Always use print() to output results - the bot captures stdout
2. Handle exceptions gracefully with try/except
3. For API calls, handle potential network errors
4. Keep execution under 60 seconds
5. Do not use input() - there is no interactive input
6. Do not write to files unless necessary
7. For async code, use asyncio.run() or asyncio.get_event_loop().run_until_complete()
8. Include brief comments explaining what the code does
9. Format output clearly for Telegram (it will be in a code block)
10. When working with private keys or mnemonics, remind users to never share them

COMMON PATTERNS:

Check wallet balance:
- Use requests to call RPC endpoints or blockchain APIs
- Or use the appropriate library (web3 for ETH, solana for SOL, etc.)

Generate wallets:
- Use hdwallet for HD wallets with mnemonic phrases
- Use eth-account for simple Ethereum accounts
- Use coincurve or ecdsa for raw key generation

Get crypto prices:
- Use pycoingecko for free price data
- Use ccxt for exchange-specific prices

Interact with exchanges:
- Use ccxt for unified API across exchanges
- Use python-binance for Binance-specific features

Sign transactions:
- Use eth-account for Ethereum
- Use solders for Solana
- Use the appropriate chain library for others

When the user asks for a script, generate clean, working Python code that follows these guidelines.
```

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
- Never share private keys or mnemonics in code you send to the bot

## License

MIT License - feel free to modify and deploy!
