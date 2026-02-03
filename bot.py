“””
Simple Python Code Executor Bot (No Docker Required)

This version uses subprocess with timeout and restricted execution.
Better compatibility with Railway and other platforms that don’t support Docker-in-Docker.
“””

import os
import sys
import asyncio
import logging
import tempfile
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging

logging.basicConfig(
format=’%(asctime)s - %(name)s - %(levelname)s - %(message)s’,
level=logging.INFO
)
logger = logging.getLogger(**name**)

# Configuration

BOT_TOKEN = os.environ.get(“TELEGRAM_BOT_TOKEN”)
ALLOWED_USERS = os.environ.get(“ALLOWED_USERS”, “”).split(”,”)
EXECUTION_TIMEOUT = int(os.environ.get(“EXECUTION_TIMEOUT”, “10”))
MAX_OUTPUT_LENGTH = 4000

def is_authorized(user_id: int) -> bool:
“”“Check if user is authorized to use the bot.”””
if not ALLOWED_USERS or ALLOWED_USERS == [””]:
return True
return str(user_id) in ALLOWED_USERS

# Wrapper code that provides some sandboxing

SANDBOX_WRAPPER = ‘’’
import sys
import signal

# Timeout handler

def timeout_handler(signum, frame):
raise TimeoutError(“Execution timed out”)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm({timeout})

# Restricted imports

ALLOWED_MODULES = {{
‘math’, ‘random’, ‘datetime’, ‘json’, ‘re’, ‘collections’,
‘itertools’, ‘functools’, ‘operator’, ‘string’, ‘textwrap’,
‘statistics’, ‘decimal’, ‘fractions’, ‘copy’, ‘pprint’,
‘numpy’, ‘pandas’, ‘sympy’, ‘scipy’
}}

original_import = **builtins**.**import**

def restricted_import(name, *args, **kwargs):
base_module = name.split(’.’)[0]
if base_module not in ALLOWED_MODULES:
raise ImportError(f”Import of ‘{{name}}’ is not allowed”)
return original_import(name, *args, **kwargs)

**builtins**.**import** = restricted_import

# Disable dangerous builtins

for name in [‘eval’, ‘exec’, ‘compile’, ‘open’, ‘input’, ‘**import**’]:
if hasattr(**builtins**, name):
delattr(**builtins**, name) if hasattr(**builtins**, ‘**delattr**’) else None

# User code starts here

{code}
‘’’

async def run_code_subprocess(code: str) -> str:
“”“Execute Python code in a subprocess with timeout.”””

```
# Wrap the code with sandboxing
wrapped_code = SANDBOX_WRAPPER.format(
    timeout=EXECUTION_TIMEOUT,
    code=code
)

# Write to temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(wrapped_code)
    temp_file = f.name

try:
    # Run in subprocess
    process = await asyncio.create_subprocess_exec(
        sys.executable, temp_file,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        limit=1024 * 1024  # 1MB output limit
    )
    
    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=EXECUTION_TIMEOUT + 2
        )
        
        output = ""
        if stdout:
            output += stdout.decode('utf-8', errors='replace')
        if stderr:
            stderr_text = stderr.decode('utf-8', errors='replace')
            # Filter out the wrapper noise from tracebacks
            if 'User code starts here' in stderr_text:
                lines = stderr_text.split('\n')
                filtered = []
                skip = True
                for line in lines:
                    if 'User code starts here' in line:
                        skip = False
                        continue
                    if not skip:
                        filtered.append(line)
                stderr_text = '\n'.join(filtered)
            output += f"\n[stderr]\n{stderr_text}" if output else stderr_text
        
        if not output.strip():
            output = "✓ Code executed successfully (no output)"
            
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        output = f"⏱️ Execution timed out after {EXECUTION_TIMEOUT} seconds"
        
except Exception as e:
    output = f"❌ Execution failed: {str(e)}"
finally:
    try:
        os.unlink(temp_file)
    except Exception:
        pass

return output[:MAX_OUTPUT_LENGTH]
```

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
“”“Handle /start command.”””
user_id = update.effective_user.id

```
if not is_authorized(user_id):
    await update.message.reply_text("⛔ You are not authorized to use this bot.")
    return

welcome_message = """🐍 *Python Code Executor Bot*
```

Send me Python code and I’ll execute it!

*Available Libraries:*
math, random, datetime, json, re, collections, itertools, functools, statistics, numpy, pandas, sympy, scipy

*Restrictions:*
• {timeout}s timeout
• No file/network access
• Limited imports

*Usage:*
Just send your Python code directly!

*Example:*

```python
import numpy as np
print(np.array([1,2,3]).mean())
```

Your user ID: `{user_id}`
“””.format(timeout=EXECUTION_TIMEOUT, user_id=user_id)

```
await update.message.reply_text(welcome_message, parse_mode='Markdown')
```

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
“”“Handle /run command.”””
user_id = update.effective_user.id

```
if not is_authorized(user_id):
    await update.message.reply_text("⛔ You are not authorized to use this bot.")
    return

code = ' '.join(context.args) if context.args else None

if not code:
    await update.message.reply_text(
        "Please provide code after /run\n\nExample:\n`/run print('Hello!')`",
        parse_mode='Markdown'
    )
    return

await execute_and_reply(update, code)
```

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
“”“Handle direct code messages.”””
user_id = update.effective_user.id

```
if not is_authorized(user_id):
    await update.message.reply_text("⛔ You are not authorized to use this bot.")
    return

code = update.message.text

# Skip casual messages
code_indicators = ['print', 'import', 'def ', 'class ', 'for ', 'while ', 'if ', '=', '(', '[', '{', '+', '-', '*', '/']
if len(code) < 3 or not any(indicator in code for indicator in code_indicators):
    await update.message.reply_text(
        "💡 Send Python code to execute it.\n\nUse /start for help.",
        parse_mode='Markdown'
    )
    return

await execute_and_reply(update, code)
```

async def execute_and_reply(update: Update, code: str) -> None:
“”“Execute code and send the result.”””
status_msg = await update.message.reply_text(“⚙️ Executing…”)

```
try:
    output = await run_code_subprocess(code)
    response = f"📤 *Output:*\n```\n{output}\n```"
    await status_msg.edit_text(response, parse_mode='Markdown')
except Exception as e:
    logger.error(f"Error executing code: {e}")
    await status_msg.edit_text(f"❌ Error: {str(e)}")
```

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
“”“Return the user’s Telegram ID.”””
user_id = update.effective_user.id
await update.message.reply_text(f”Your user ID is: `{user_id}`”, parse_mode=‘Markdown’)

def main():
“”“Start the bot.”””
if not BOT_TOKEN:
raise ValueError(“TELEGRAM_BOT_TOKEN environment variable is required”)

```
application = Application.builder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("run", run_command))
application.add_handler(CommandHandler("id", get_id))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

logger.info("Starting bot...")
application.run_polling(allowed_updates=Update.ALL_TYPES)
```

if **name** == “**main**”:
main()
