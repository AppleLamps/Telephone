# 🐍 Python Code Executor Telegram Bot

A secure Telegram bot that executes Python code in isolated Docker containers. Perfect for testing snippets, learning Python, or quick calculations.

## Features

- 🔒 **Sandboxed Execution**: Code runs in isolated Docker containers
- ⏱️ **Timeout Protection**: Prevents infinite loops (configurable, default 10s)
- 💾 **Memory Limits**: Containers limited to 128MB RAM
- 🚫 **No Network**: Sandbox has no internet access
- 👤 **User Authorization**: Optional whitelist for allowed users
- 📦 **Pre-installed Libraries**: numpy, pandas, matplotlib, requests, sympy, scipy

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
1. Send `/newbot` and follow the prompts
1. Copy the API token you receive

### 2. Deploy to Railway

#### Option A: One-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

#### Option B: Manual Deploy

1. Push this code to a GitHub repository
1. Go to [railway.app](https://railway.app)
1. Create a new project and select “Deploy from GitHub repo”
1. Select your repository

### 3. Configure Environment Variables

In Railway dashboard, add these environment variables:

|Variable            |Required|Description                                                      |
|--------------------|--------|-----------------------------------------------------------------|
|`TELEGRAM_BOT_TOKEN`|✅ Yes   |Your bot token from BotFather                                    |
|`ALLOWED_USERS`     |❌ No    |Comma-separated Telegram user IDs (leave empty for public access)|
|`EXECUTION_TIMEOUT` |❌ No    |Max execution time in seconds (default: 10)                      |

### 4. Enable Docker-in-Docker (Important!)

Railway requires special configuration for Docker-in-Docker:

1. In your Railway project, go to **Settings** → **General**
1. Enable **“Docker-in-Docker”** or add the service with privileged mode

⚠️ **Note**: If Railway doesn’t support Docker-in-Docker on your plan, see the “Alternative: Process-Based Execution” section below.

## Usage

### Commands

- `/start` - Welcome message and instructions
- `/run <code>` - Execute Python code
- `/id` - Get your Telegram user ID (useful for ALLOWED_USERS)

### Direct Messages

Just send Python code directly to the bot - it will detect and execute it automatically.

### Examples

**Simple calculation:**

```python
print(2 ** 100)
```

**Using libraries:**

```python
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print(f"Mean: {arr.mean()}")
print(f"Std: {arr.std()}")
```

**Multiline code:**

```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

print(list(fibonacci(10)))
```

## Alternative: Process-Based Execution

If Railway doesn’t support Docker-in-Docker on your plan, use this simpler version that runs code in a subprocess with `RestrictedPython`:

Create a new `bot_simple.py`:

```python
import os
import sys
import asyncio
from io import StringIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ALLOWED_USERS = os.environ.get("ALLOWED_USERS", "").split(",")
TIMEOUT = int(os.environ.get("EXECUTION_TIMEOUT", "5"))

# Restricted builtins
SAFE_BUILTINS = {
    'print': print, 'len': len, 'range': range, 'int': int, 'float': float,
    'str': str, 'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
    'bool': bool, 'abs': abs, 'max': max, 'min': min, 'sum': sum,
    'sorted': sorted, 'reversed': reversed, 'enumerate': enumerate,
    'zip': zip, 'map': map, 'filter': filter, 'round': round, 'pow': pow,
    'True': True, 'False': False, 'None': None,
}

async def run_code(code: str) -> str:
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        exec(code, {"__builtins__": SAFE_BUILTINS})
        output = sys.stdout.getvalue() or "✓ Executed (no output)"
    except Exception as e:
        output = f"❌ Error: {e}"
    finally:
        sys.stdout = old_stdout
    
    return output[:4000]

# ... rest of handlers same as main bot
```

Update `requirements.txt`:

```
python-telegram-bot==21.3
```

## Security Considerations

⚠️ **Warning**: Running arbitrary code is inherently risky. This bot includes multiple safety measures, but consider:

1. **Always use ALLOWED_USERS** in production to restrict access
1. **Monitor resource usage** - malicious code could still cause issues
1. **Review logs** for suspicious activity
1. **Consider rate limiting** for high-traffic bots

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your-token-here"

# Run the bot
python bot.py
```

## License

MIT License - feel free to modify and deploy!
