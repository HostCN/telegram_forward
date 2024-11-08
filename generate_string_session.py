from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# 你的 API ID 和 API HASH（从 Telegram 官网获取）
API_ID = ''  # 替换为你的 API ID
API_HASH = ''  # 替换为你的 API HASH

# 输入你的手机号，确保格式正确
phone = input('请输入你的手机号（带国际区号）：')  # 如 +1234567890


# 创建并启动 Telegram 客户端
with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    client.start(phone)  # 启动客户端并登录
    print("登录成功！")
    
    # 打印生成的 session 字符串
    print("你的 StringSession 为：")
    print(client.session.save())  # 打印 session 字符串
