"""
Python Code Executor Bot for Telegram

Full-featured Python executor supporting crypto scripts, network requests,
and all standard libraries. Designed for deployment on Railway.
"""

import os
import sys
import asyncio
import logging
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ALLOWED_USERS = os.environ.get("ALLOWED_USERS", "").split(",")
EXECUTION_TIMEOUT = int(os.environ.get("EXECUTION_TIMEOUT", "60"))  # 60 seconds for crypto API calls
MAX_OUTPUT_LENGTH = 4000


def is_authorized(user_id: int) -> bool:
    """Check if user is authorized to use the bot."""
    if not ALLOWED_USERS or ALLOWED_USERS == [""]:
        return True
    return str(user_id) in ALLOWED_USERS


async def run_code_subprocess(code: str) -> str:
    """Execute Python code in a subprocess with timeout."""

    # Write code to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        # Run in subprocess with full Python capabilities
        process = await asyncio.create_subprocess_exec(
            sys.executable, '-u', temp_file,  # -u for unbuffered output
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=1024 * 1024 * 5  # 5MB output limit
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=EXECUTION_TIMEOUT
            )

            # Decode outputs
            output = ""
            if stdout:
                output += stdout.decode('utf-8', errors='replace')
            if stderr:
                stderr_text = stderr.decode('utf-8', errors='replace')
                if output:
                    output += f"\n[stderr]\n{stderr_text}"
                else:
                    output = stderr_text

            # Check if process failed (non-zero exit code)
            if process.returncode != 0:
                if not output.strip():
                    output = f"Process exited with code {process.returncode} (no output)"
                else:
                    # Ensure we indicate this was an error
                    output = f"[Exit code: {process.returncode}]\n{output}"
            elif not output.strip():
                # Process succeeded but produced no output
                output = "Code executed successfully (no output)"

        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            output = f"Execution timed out after {EXECUTION_TIMEOUT} seconds"

    except Exception as e:
        # Log the full exception for debugging
        logger.error(f"Execution error: {e}", exc_info=True)
        output = f"Execution failed: {str(e)}"
    finally:
        try:
            os.unlink(temp_file)
        except Exception:
            pass

    return output[:MAX_OUTPUT_LENGTH]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    welcome_message = """*Python Code Executor Bot*

Send me any Python code and I'll execute it!

*Available Libraries:*
- Crypto: web3, solana, solders, base58, eth-account, bitcoinlib, blockcypher, requests
- Data: numpy, pandas, aiohttp, httpx
- Utils: json, re, datetime, asyncio, and all standard library

*Features:*
- Full network access for API calls
- {timeout}s timeout
- Supports async code

*Usage:*
Just send your Python code directly or use /run

*Example - Check SOL Balance:*
```python
import requests
addr = "your_solana_address"
url = f"https://api.mainnet-beta.solana.com"
payload = {{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getBalance",
    "params": [addr]
}}
r = requests.post(url, json=payload)
balance = r.json()["result"]["value"] / 1e9
print(f"Balance: {{balance}} SOL")
```

Your user ID: `{user_id}`
""".format(timeout=EXECUTION_TIMEOUT, user_id=user_id)

    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /run command."""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    code = ' '.join(context.args) if context.args else None

    if not code:
        await update.message.reply_text(
            "Please provide code after /run\n\nExample:\n`/run print('Hello!')`",
            parse_mode='Markdown'
        )
        return

    await execute_and_reply(update, code)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle direct code messages."""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    code = update.message.text

    # Strip markdown code blocks if present
    if code.startswith('```python'):
        code = code[9:]
    elif code.startswith('```'):
        code = code[3:]
    if code.endswith('```'):
        code = code[:-3]
    code = code.strip()

    # Skip casual messages - check for code indicators
    code_indicators = [
        'print', 'import', 'from ', 'def ', 'class ', 'for ', 'while ',
        'if ', 'try:', 'async ', 'await ', 'with ', 'return',
        '=', '(', '[', '{', '#'
    ]

    if len(code) < 3 or not any(indicator in code for indicator in code_indicators):
        await update.message.reply_text(
            "Send Python code to execute it.\n\nUse /start for help.",
            parse_mode='Markdown'
        )
        return

    await execute_and_reply(update, code)


async def execute_and_reply(update: Update, code: str) -> None:
    """Execute code and send the result."""
    status_msg = await update.message.reply_text("Executing...")

    try:
        output = await run_code_subprocess(code)

        # Handle long outputs
        if len(output) > MAX_OUTPUT_LENGTH:
            output = output[:MAX_OUTPUT_LENGTH] + "\n... (output truncated)"

        response = f"*Output:*\n```\n{output}\n```"
        await status_msg.edit_text(response, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error executing code: {e}")
        await status_msg.edit_text(f"Error: {str(e)}")


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return the user's Telegram ID."""
    user_id = update.effective_user.id
    await update.message.reply_text(f"Your user ID is: `{user_id}`", parse_mode='Markdown')


async def libs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List available libraries."""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    libs_message = """*Installed Libraries:*

*Ethereum:*
`web3`, `eth-account`, `eth-abi`, `eth-utils`

*Solana:*
`solana`, `solders`

*Bitcoin:*
`bitcoinlib`, `blockcypher`

*Other Chains:*
`tronpy`, `xrpl-py`, `stellar-sdk`

*Wallets & Keys:*
`hdwallet`, `mnemonic`, `base58`, `bip32utils`

*Cryptography:*
`pycryptodome`, `coincurve`, `pynacl`, `ecdsa`, `cryptography`

*Exchange APIs:*
`ccxt`, `python-binance`, `pycoingecko`

*Networking:*
`requests`, `aiohttp`, `httpx`, `websockets`

*Data:*
`numpy`, `pandas`

*Standard Library:*
All Python standard library modules
"""
    await update.message.reply_text(libs_message, parse_mode='Markdown')


def main():
    """Start the bot."""
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("run", run_command))
    application.add_handler(CommandHandler("id", get_id))
    application.add_handler(CommandHandler("libs", libs))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
