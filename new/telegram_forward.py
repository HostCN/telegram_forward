import asyncio
import json
import logging
import os
import re
import time
from telethon import events
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("telegram_forward.log", mode='w')
    ]
)

# 配置文件路径
CONFIG_FILE = "config.json"
if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(f"配置文件 {CONFIG_FILE} 不存在")

# 加载配置文件
with open(CONFIG_FILE, "r") as config_file:
    config = json.load(config_file)

# 从配置文件读取参数
API_ID = config["api_id"]
API_HASH = config["api_hash"]
SESSION_STRING = config["session_string"]
SOURCE_CHANNEL_IDS = config["source_channel_ids"]
TARGET_CHANNEL_IDS = config["target_channel_ids"]
DELAY = config.get("delay", 3)
LINK_REPLACEMENTS = config.get("link_replacements", {})
CONDITIONAL_REPLACEMENTS = config.get("conditional_replacements", [])

# 已处理消息文件
PROCESSED_MESSAGES_FILE = "processed_messages.json"
SAVE_INTERVAL = 60
last_save_time = time.time()

# 加载已处理的消息
if os.path.exists(PROCESSED_MESSAGES_FILE):
    with open(PROCESSED_MESSAGES_FILE, "r") as file:
        processed_messages = set(json.load(file))
else:
    processed_messages = set()

# 条件替换逻辑
def apply_conditional_replacements(message_text):
    for condition in CONDITIONAL_REPLACEMENTS:
        # 检查消息是否包含任意关键词
        if any(keyword in message_text for keyword in condition["keywords"]):
            # 关键词匹配时，应用所有替换规则
            for rule in condition["rules"]:
                pattern = rule["pattern"]
                replacement = rule["replacement"]
                is_regex = rule["is_regex"]

                if is_regex:
                    message_text = re.sub(pattern, replacement, message_text)
                else:
                    message_text = message_text.replace(pattern, replacement)

    return message_text

# 异步主函数
async def main():
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:

        @client.on(events.NewMessage(chats=SOURCE_CHANNEL_IDS))
        async def handler(event):
            message = event.message

            # 检查是否已处理，避免重复转发
            if message.id not in processed_messages:
                original_message = message.text
                modified_message = original_message

                # 先应用 link_replacements 中的替换规则
                for pattern, replacement in LINK_REPLACEMENTS.items():
                    modified_message = re.sub(pattern, replacement, modified_message)

                # 然后应用 conditional_replacements 中的规则
                modified_message = apply_conditional_replacements(modified_message)

                # 检查是否发生了替换
                if modified_message != original_message:
                    logging.debug(f"替换后的消息: {modified_message}")

                    # 尝试转发到多个目标频道
                    for target_channel in TARGET_CHANNEL_IDS:
                        try:
                            await client.send_message(target_channel, modified_message, link_preview=False)
                            logging.info(f"成功转发消息到目标频道: {target_channel}")
                        except Exception as e:
                            logging.error(f"转发消息失败到频道 {target_channel}: {e}")
                            if "429" in str(e):  # 处理请求频率过高的错误
                                await asyncio.sleep(5)

                    # 标记已处理的消息
                    processed_messages.add(message.id)

                    # 定期保存已处理的消息
                    global last_save_time
                    if time.time() - last_save_time > SAVE_INTERVAL:
                        try:
                            with open(PROCESSED_MESSAGES_FILE, "w") as file:
                                json.dump(list(processed_messages), file)
                            last_save_time = time.time()
                        except Exception as e:
                            logging.error(f"保存已处理消息文件失败: {e}")

                    # 动态延迟
                    await asyncio.sleep(DELAY)

        logging.info("消息转发已启动，等待消息...")
        await client.run_until_disconnected()

# 运行主函数
try:
    asyncio.run(main())
except Exception as e:
    logging.error(f"运行主程序时出现错误: {e}")
