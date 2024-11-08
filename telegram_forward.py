import asyncio
import logging
import json
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon import events
import os
import sys
import atexit
from time import sleep

LOCK_FILE = "/tmp/telegram_forward.lock"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("telegram_forward.log", mode='w')
    ]
)

API_ID = API_ID # 环境变量名为 API_ID
API_HASH = 'API_HASH' # 环境变量名为 'API_HASH'
SESSION_STRING = 'SESSION_STRING' # 环境变量名为 'SESSION_STRING'

SOURCE_CHANNEL_IDS = ['@zxtspd', '@vpscang']
TARGET_CHANNEL_ID = '@hostzg'
KEYWORDS = ["2024", "DMIT"]
PROCESSED_MESSAGES_FILE = "processed_messages.json"

# 加载已处理消息的 ID
if os.path.exists(PROCESSED_MESSAGES_FILE):
    with open(PROCESSED_MESSAGES_FILE, "r") as file:
        processed_messages = set(json.load(file))
else:
    processed_messages = set()

async def main():
    # 使用 async with 启动 Telegram 客户端
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:

        @client.on(events.NewMessage(chats=SOURCE_CHANNEL_IDS))
        async def handler(event):
            message = event.message

            # 检查消息 ID 是否已处理，避免重复转发
            if message.id not in processed_messages and any(keyword in message.text for keyword in KEYWORDS):
                if "https://my.racknerd.com/cart.php?a=add" in message.text or "https://www.dmit.io/aff.php?aff=184" in message.text:
                    modified_message = message.text.replace(
                        "https://my.racknerd.com/cart.php?a=add", 
                        "https://my.racknerd.com/aff.php?aff=112"
                    ).replace(
                        "https://www.dmit.io/aff.php?aff=184", 
                        "https://www.dmit.io/aff.php?aff=785"
                    )

                    # 尝试转发消息并增加延迟
                    try:
                        await client.send_message(TARGET_CHANNEL_ID, modified_message)
                        logging.info(f"成功转发消息到目标频道: {TARGET_CHANNEL_ID}")
                        
                        # 记录已处理的消息 ID
                        processed_messages.add(message.id)
                        with open(PROCESSED_MESSAGES_FILE, "w") as file:
                            json.dump(list(processed_messages), file)
                        
                        await asyncio.sleep(3)  # 延迟3秒防止请求过多

                    except Exception as e:
                        logging.error(f"转发消息失败: {e}")
                        if "429" in str(e):  # 如果是请求过多错误，延迟重试
                            await asyncio.sleep(5)

        logging.info("消息转发已启动，等待消息...")
        await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
