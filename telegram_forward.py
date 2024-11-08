import os
import sys
import signal
import psutil
import logging
import json
import atexit
import asyncio
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon import events
from telethon.errors import FloodWaitError
from time import sleep
import traceback

# 锁文件路径
LOCK_FILE = "/tmp/telegram_forward.lock"
PROCESSED_MESSAGES_FILE = "processed_messages.json"

# 删除锁文件
def remove_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

# 创建锁文件，防止脚本重复运行
def create_lock():
    if os.path.exists(LOCK_FILE):
        print("脚本已在运行，退出。")
        sys.exit(0)
    else:
        open(LOCK_FILE, "w").close()

# 检查是否有其他相同名称的进程在运行，并保留最新的进程
def terminate_existing_processes():
    current_pid = os.getpid()  # 获取当前进程 ID
    current_process_name = os.path.basename(sys.argv[0])  # 获取当前脚本文件名

    # 存储所有匹配的进程，并按启动时间排序
    matching_processes = []

    # 遍历所有进程，查找与当前脚本相同名称的进程
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
        if proc.info['pid'] != current_pid and current_process_name in proc.info['exe']:
            matching_processes.append(proc)

    # 按启动时间升序排序，保留最晚启动的进程
    matching_processes.sort(key=lambda proc: proc.info['create_time'], reverse=True)

    # 如果存在多个进程，终止其余的进程
    for proc in matching_processes[1:]:  # 保留最新的进程
        logging.info(f"发现多余的进程 {proc.info['pid']} ({proc.info['exe']})，正在终止...")
        try:
            proc.terminate()  # 终止该进程
            proc.wait()  # 等待进程退出
            logging.info(f"进程 {proc.info['pid']} 已成功终止")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            logging.error(f"无法终止进程 {proc.info['pid']}, 权限不足或进程已退出")

atexit.register(remove_lock)  # 程序结束时删除锁文件
create_lock()  # 程序开始时检查并创建锁文件

terminate_existing_processes()  # 检查并终止多余的进程

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("telegram_forward.log", mode='w')
    ]
)

# API 配置
API_ID = your_api_id
API_HASH = 'your_api_hash'
SESSION_STRING = 'your_string_session'

SOURCE_CHANNEL_IDS = ['@zxtspd', '@vpscang']
TARGET_CHANNEL_ID = '@hostzg'
KEYWORDS = ["2024", "DMIT"]

# 加载已处理的消息ID
if os.path.exists(PROCESSED_MESSAGES_FILE):
    with open(PROCESSED_MESSAGES_FILE, "r") as file:
        processed_messages = set(json.load(file))
else:
    processed_messages = set()

processed_message_counter = 0
MAX_WRITE_INTERVAL = 100  # 每处理100条消息写一次文件

async def process_message(message, client):
    global processed_message_counter
    if message.id not in processed_messages and any(keyword in message.text for keyword in KEYWORDS):
        if "https://my.racknerd.com/cart.php?a=add" in message.text or "https://www.dmit.io/aff.php?aff=184" in message.text:
            modified_message = message.text.replace(
                "https://my.racknerd.com/cart.php?a=add", 
                "https://my.racknerd.com/aff.php?aff=112"
            ).replace(
                "https://www.dmit.io/aff.php?aff=184", 
                "https://www.dmit.io/aff.php?aff=785"
            )

            try:
                # 发送修改后的消息
                await client.send_message(TARGET_CHANNEL_ID, modified_message)
                logging.info(f"成功转发消息到目标频道: {TARGET_CHANNEL_ID}")
                
                # 更新处理计数
                processed_message_counter += 1

                # 每处理100条消息才写入一次文件
                if processed_message_counter >= MAX_WRITE_INTERVAL:
                    with open(PROCESSED_MESSAGES_FILE, "w") as file:
                        json.dump(list(processed_messages), file)
                    processed_message_counter = 0

                # 记录已处理的消息ID
                processed_messages.add(message.id)

                await asyncio.sleep(1)  # 延迟1秒防止请求过多

            except Exception as e:
                logging.error(f"转发消息失败: {e}")
                logging.error(traceback.format_exc())  # 打印堆栈信息
                if isinstance(e, FloodWaitError):
                    logging.warning(f"遇到 FloodWaitError，等待 {e.seconds} 秒后重试")
                    await asyncio.sleep(e.seconds)  # FloodWaitError时等待

        else:
            logging.info(f"消息未包含关键字，跳过处理: {message.id}")

async def main():
    # 使用 async with 来异步地创建 Telegram 客户端
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:

        @client.on(events.NewMessage(chats=SOURCE_CHANNEL_IDS))
        async def handler(event):
            message = event.message

            # 处理消息
            await process_message(message, client)

        logging.info("消息转发已启动，等待消息...")
        await client.run_until_disconnected()

# 启动主程序
asyncio.run(main())
