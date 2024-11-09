# 安装telegram_forward

### 1. 确认 Python 已安装
首先，确保系统已经安装了 Python 3.x，通常在 Linux 服务器上会预装 Python。如果没有安装，使用以下命令进行安装：

```bash
# 在 Debian/Ubuntu 系统上
sudo apt update
sudo apt install python3 python3-venv python3-pip

# 在 CentOS/RHEL 系统上
sudo yum install python3
```

--------------------------------------------------------------------------------------------------------

运行这个 Telegram 消息转发脚本涉及以下步骤：

### 一、环境准备

2. **安装 Python 环境**  
   上步已经完成安装，确保系统已经安装了 Python （通常是 Python 3.x）。

3. **创建项目目录**  
   在宝塔面板的文件管理器或通过 SSH 登录服务器，创建一个目录来存放 Telegram 脚本文件。例如，可以创建目录 `/www/telegram_forward`：

   ```bash
   mkdir /www/telegram_forward
   cd /www/telegram_forward
   ```

### 二、安装 Telethon 库

1. **使用 SSH 登录服务器**  
   使用 SSH 客户端（如 PuTTY）或宝塔面板中的终端功能，进入服务器的命令行。

2. **进入项目目录**  
   切换到刚才创建的项目目录：

   ```bash
   cd /www/telegram_forward
   ```

3. **进入虚拟环境**  
   Python 虚拟环境：

   ```bash
   source venv/bin/activate
   ```

4. **安装 Telethon**  
   在虚拟环境中，使用 `pip` 安装 `Telethon`：

   ```bash
   pip install telethon
   ```

### 三、编写脚本文件

1. **创建 Python 脚本文件**  
   在项目目录 `/www/telegram_forward` 中创建一个 Python 文件，例如 `telegram_forward.py`。可以在宝塔面板的文件管理器中右键点击“新建文件”。

2. **粘贴脚本代码**  
   将之前的 Telegram 转发代码粘贴到 `telegram_forward.py` 文件中，并保存。

   在宝塔面板中编辑 `telegram_forward.py` 文件，确保填入 `API_ID`、`API_HASH`、`SOURCE_CHANNEL_ID`、`TARGET_CHANNEL_ID` 等信息。

### 四、运行脚本

1. **终端直接运行**
   
   ```bash
     cd /www/telegram_forward
     source venv/bin/activate
     nohup python3 telegram_forward.py > output.log
     ```

2. **宝塔的“计划任务”运行（推荐方便后期如更改代码后重启新脚本）**  
   在宝塔面板左侧找到“计划任务”，点击进入。
   点击“添加任务”，在任务类型中选择“Shell 脚本”，并设置以下内容：
   - **任务名称**：可以设置为 `Telegram消息转发脚本`
   - **执行周期**：添加后只需执行一次即可，方便后期如更改代码后重启新脚本
   - **脚本内容**：填写启动 Python 脚本的命令。注意，如果使用了虚拟环境，请确保激活虚拟环境后再运行脚本：

     ```bash
     cd /www/telegram_forward
     source venv/bin/activate
     nohup python3 telegram_forward.py > output.log
     ```

   上述命令会进入项目目录、激活虚拟环境，并以后台方式运行脚本，同时将输出记录到 `output.log` 文件中。
   保存并运行任务一次即可，查看是否成功启动脚本。

### 五、查看脚本是否正常运行

1. **检查日志**  
   可以通过查看 `output.log` 文件来检查脚本的输出是否有错误。也可以在宝塔面板的文件管理器中直接查看。

   ```bash
   tail -f /www/telegram_forward/output.log
   ```

2. **查看 Telegram 转发情况**  
   检查目标频道，确认脚本已经成功转发消息。

### 六、管理和停止脚本

1. **停止脚本**  
   若要停止脚本，可以通过 `ps` 命令找到 `telegram_forward.py` 进程并结束它：

   ```bash
   ps aux | grep telegram_forward.py
   ```

   找到脚本的进程 ID 后，使用以下命令终止：

   ```bash
   kill -9 <进程ID>
   ```

2. **调整脚本配置**  
   若需要调整关键词或替换规则，直接在宝塔面板的文件管理器中编辑 `telegram_forward.py` 文件，并重新启动脚本。

完成这些步骤后，你就能在宝塔面板中运行并管理 Telegram 转发脚本了。

--------------------------------------------------------------------------------------------------------

# 生成StringSession

为了确保你的脚本可以在无交互环境中自动登录使用 `StringSession`

这种方式适合需要在多台设备或服务器上运行同一会话的情况，可以避免每次登录都输入手机号或验证码。你可以在本地生成一个 `StringSession`，然后使用它在服务器上登录。

#### 进入文件所在文件夹，启动脚本

   ```bash
   cd /www/telegram_forward
   source venv/bin/activate
   python3 generate_string_session.py
   ```
根据提示输入telegram手机号，密码，获取的验证码

生成 `StringSession`脚本如下：

```python
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = '你的API_ID'
API_HASH = '你的API_HASH'

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("Session String:", client.session.save())  # 生成并打印会话字符串
```

执行该脚本后，会在控制台打印出一个 `Session String`。将该字符串保存下来，用于服务器上的脚本。
