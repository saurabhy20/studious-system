import os
import sys
import logging
import asyncio
import psutil
import requests
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.network import ConnectionTcpFull, ConnectionTcpAbridged
from dotenv import load_dotenv

# Load environment variables first!
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Prince-X")

# Validate environment variables
def validate_env():
    required_vars = ["API_ID", "API_HASH", "SESSION_STRING"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

validate_env()

# Load environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))
OWNER_ID = int(os.getenv("OWNER_ID", 0))
OPENAI_KEY = os.getenv("OPENAI_KEY", "")
TG_PORT = int(os.getenv("TG_PORT", 443))  # Default to 443
CONNECTION_MODE = os.getenv("CONNECTION_MODE", "TcpFull")  # Connection mode

# Connection mode mapping
CONNECTION_TYPES = {
    "TcpFull": ConnectionTcpFull,
    "TcpAbridged": ConnectionTcpAbridged
}

# Get connection class with validation
if CONNECTION_MODE in CONNECTION_TYPES:
    connection_class = CONNECTION_TYPES[CONNECTION_MODE]
    logger.info(f"Using connection mode: {CONNECTION_MODE}")
else:
    logger.warning(f"Invalid connection mode: {CONNECTION_MODE}. Using default TcpFull")
    connection_class = ConnectionTcpFull
    CONNECTION_MODE = "TcpFull"

# Initialize clients with connection optimization
try:
    # Create connection instance with port configuration
    connection = connection_class(
        ip=None,          # Will be resolved automatically
        port=TG_PORT,
        dc_id=0,          # Default DC
        loggers=logger
    )
    
    client = TelegramClient(
        StringSession(SESSION_STRING),
        API_ID,
        API_HASH,
        connection=connection,  # Pass the configured connection
        use_ipv6=False,         # Disable IPv6 for faster resolution
        connection_retries=10,
        auto_reconnect=True,
        timeout=30,
        request_retries=5,
        device_model="Prince-X Server",
        system_version="Ultra-Low-Latency",
        lang_code="en",
        system_lang_code="en"
    )
    
    bot = None
    if BOT_TOKEN:
        bot_connection = connection_class(
            ip=None,
            port=TG_PORT,
            dc_id=0,
            loggers=logger
        )
        bot = TelegramClient(
            'bot',
            API_ID,
            API_HASH,
            connection=bot_connection  # Pass the configured connection
        )
        
    logger.info("Telegram clients initialized successfully")
        
except Exception as e:
    logger.error(f"Client initialization failed: {str(e)}")
    logger.exception(e)  # Log full exception trace
    sys.exit(1)

# Global variables
start_time = datetime.now()

# Core commands
@client.on(events.NewMessage(pattern=r'\.ping'))
async def ping_handler(event):
    start = datetime.now()
    message = await event.edit("🏓 `Pong!`")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await message.edit(f"🏓 **Pong!**\n`{ms:.2f}ms`")

@client.on(events.NewMessage(pattern=r'\.sys'))
async def sysinfo_handler(event):
    start = datetime.now()
    message = await event.reply("📊 **Collecting system data...**")
    end = datetime.now()
    resp_time = (end - start).microseconds / 1000
    
    cpu_usage = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    await message.edit(
        f"🖥️ **Prince-X System Report**\n\n"
        f"⏱️ **Response Time:** `{resp_time:.2f}ms`\n"
        f"🧠 **CPU Usage:** `{cpu_usage}%`\n"
        f"💾 **Memory:** `{mem.used/1024/1024:.1f}MB/{mem.total/1024/1024:.1f}MB`\n"
        f"💽 **Swap:** `{swap.used/1024/1024:.1f}MB/{swap.total/1024/1024:.1f}MB`\n"
        f"🐍 **Python:** `{sys.version.split()[0]}`\n"
        f"⚡ **Uptime:** `{datetime.now() - start_time}`"
    )

@client.on(events.NewMessage(pattern=r'\.restart'))
async def restart_handler(event):
    await event.reply("🔄 **Restarting Prince-X Userbot...**")
    os.execl(sys.executable, sys.executable, *sys.argv)

@client.on(events.NewMessage(pattern=r'\.hello'))
async def hello_handler(event):
    user = await event.get_sender()
    await event.reply(f"👋 Hello [{user.first_name}](tg://user?id={user.id})! How can I assist you today?")

@client.on(events.NewMessage(pattern=r'\.ask (.*)'))
async def ai_handler(event):
    query = event.pattern_match.group(1)
    await event.reply("💭 Thinking...")
    
    try:
        headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": query}],
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            await event.reply(f"🤖 **Prince-X AI**\n\n{answer}")
        else:
            await event.reply(f"❌ API Error: {response.status_code}")
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

@client.on(events.NewMessage(pattern=r'\.gencard'))
async def fake_card_handler(event):
    await event.reply("💳 **Fake Card Generated!**\n\n"
                     "Card: `4111 1111 1111 1111`\n"
                     "Exp: `12/25`\nCVV: `123`\n\n"
                     "📧 Temp Email: `temp@princex.cc`")

# Connection test command
@client.on(events.NewMessage(pattern=r'\.conn'))
async def conn_test_handler(event):
    try:
        start = datetime.now()
        me = await client.get_me()
        connect_time = (datetime.now() - start).microseconds / 1000
        await event.reply(
            f"🌐 **Connection Test**\n\n"
            f"✅ **Success!**\n"
            f"👤 **User:** {me.first_name}\n"
            f"🆔 **ID:** {me.id}\n"
            f"🔌 **Mode:** {CONNECTION_MODE}\n"
            f"🔢 **Port:** {TG_PORT}\n"
            f"⚡ **Ping:** {connect_time:.2f}ms"
        )
    except Exception as e:
        await event.reply(f"❌ **Connection Failed**\n\n{str(e)}")

# Startup notification
async def send_startup_message():
    try:
        me = await client.get_me()
        message = (
            "🚀 **Prince-X Userbot Activated!**\n\n"
            f"👑 **User:** [{me.first_name}](tg://user?id={me.id})\n"
            f"🔌 **Connection:** {CONNECTION_MODE} on port {TG_PORT}\n"
            "📅 **System Status:** Operational\n\n"
            "_Report issues @PrinceXSupport_"
        )
        
        if LOG_CHANNEL:
            await client.send_message(LOG_CHANNEL, message)
        else:
            logger.info("Skipping startup message - LOG_CHANNEL not set")
    except Exception as e:
        logger.error(f"Startup message error: {str(e)}")

# Main function
async def main():
    try:
        logger.info("Starting Prince-X Client...")
        await client.start()
        logger.info("Prince-X Client Started")
        
        # Verify connection
        me = await client.get_me()
        logger.info(f"Authenticated as: {me.first_name} (ID: {me.id})")
        
        if bot:
            logger.info("Starting Assistant Bot...")
            await bot.start(bot_token=BOT_TOKEN)
            logger.info("Assistant Bot Started")
        
        await send_startup_message()
        logger.info("Startup process completed")
        
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
