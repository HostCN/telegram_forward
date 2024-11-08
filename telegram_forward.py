import asyncio
import logging
import json
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon import events
import os
import sys
import psutil
import atexit
from time import sleep

# 锁文件路径
LOCK_FILE = "/tmp/telegram_forward.lock"
PROCESSED_MESSAGES_FILE = "processed_messages.json"
API_ID = api
API_HASH = 'api'
SESSION_STRING = 'api'
SOURCE_CHANNEL_IDS = ['@zxtspd', '@vpscang']
TARGET_CHANNEL_ID = '@hostzg'
KEYWORDS = ["2024", "DMIT"]

# 检查是否已经有实例运行
def check_process():
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'python3' and 'telegram_forward.py' in proc.info['cmdline']:
            # 如果进程不是当前进程，则结束它
            if proc.info['pid'] != current_pid:
                print(f"找到正在运行的进程: {proc.info['pid']}，准备终止它")
                proc.terminate()
                proc.wait()

# 检查并创建锁文件
if os.path.exists(LOCK_FILE):
    print("脚本已在运行，退出。")
    sys.exit(0)
else:
    open(LOCK_FILE, "w").close()

# 注册程序退出时删除锁文件
def cleanup():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

atexit.register(cleanup)

# 在开始时检查并终止多余的进程
check_process()

# 加载已处理消息的 ID
if os.path.exists(PROCESSED_MESSAGES_FILE):
    with open(PROCESSED_MESSAGES_FILE, "r") as file:
        processed_messages = set(json.load(file))
else:
    processed_messages = set()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("telegram_forward.log", mode='w')
    ]
)

async def main():
    # 初始化 Telegram 客户端
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
                        
                        await asyncio.sleep(1)  # 延迟1秒防止请求过多

                    except Exception as e:
                        logging.error(f"转发消息失败: {e}")
                        if "429" in str(e):  # 如果是请求过多错误，延迟重试
                            await asyncio.sleep(5)

        logging.info("消息转发已启动，等待消息...")
        await client.run_until_disconnected()

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
