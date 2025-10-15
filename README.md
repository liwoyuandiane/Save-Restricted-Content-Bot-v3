<h1 align="center">
  TG消息提取器机器人 v3
</h1>

TG消息提取器机器人是由 devgagan 和 TEAM SPY 开发的稳定 Telegram 机器人。它使用户能够从 Telegram 频道和群组中检索受限消息，提供自定义缩略图支持和上传最大 4GB 文件的功能。此外，机器人还支持从 YouTube、Instagram、Facebook 等 100 多个网站下载视频。

[Telegram](https://t.me/save_restricted_content_bots) | [查看最新更新](https://github.com/devgaganin/Save-Restricted-Content-Bot-V2/tree/v3#updates)

### 给仓库点星鼓励我们更新新功能
请给仓库点星并多多 Fork，谢谢！

## 📚 关于此分支
- 此分支基于 `Pyrogram V2`，提供增强的稳定性和强制登录功能。对于公共频道，用户不需要强制登录，但对于公共群组和私有频道，用户必须进行登录。
- 详细功能请向下滚动查看功能部分

---

## 🔧 功能特性
- 从公共和私有频道/群组中提取内容
- 添加自定义机器人功能，使用 `/setbot`
- 128位加密数据保存，使用 @v3saverbot 生成 `MASTER_KEY`、`IV_KEY`
- 重命名并转发内容到其他频道或用户
- 从其他机器人提取受限内容，使用格式如 `https://botusername(不带@)/message_id(从plus messenger获取)`
- `/login` 方法以及基于 `session` 的登录
- 自定义标题和缩略图
- 自动移除默认视频缩略图
- 删除或替换文件名和标题中的单词
- 如果启用，自动置顶消息
- 下载 YouTube/Instagram/Twitter/Facebook 等 ytdlp 支持的网站，支持最佳格式
- 通过手机号登录
- **支持 4GB 文件上传**：机器人可以处理最大 4GB 的大文件上传
- 如果不是高级字符串，则文件分割器
- **增强计时器**：为免费和付费用户提供不同的计时器，限制使用并改善服务
- **改进循环**：优化处理多个文件或链接的循环，减少延迟并提升性能
- **高级访问**：高级用户享受更快的处理速度和优先队列管理
- ~~广告设置短链接广告令牌系统~~
- ~~通过 `SpyLib` 使用 Telethon 模块和 `mautrix bridge repo` 快速上传~~
- 直接上传到任何启用主题的群组中的 `topic`
- 实时下载和上传进度，支持聊天、文本、音频、视频、视频笔记、贴纸等所有内容

  
## ⚡ 命令列表

- **`start`**: 🚀 启动机器人
- **`batch`**: 🫠 批量提取
- **`login`**: 🔑 登录机器人
- **`single`**: 处理单个链接
- **`setbot`**: 添加你的自定义机器人
- **`logout`**: 🚪 退出机器人
- **`adl`**: 👻 从30+个网站下载音频
- **`dl`**: 💀 从30+个网站下载视频
- **`transfer`**: 💘 赠送高级会员给他人
- **`status`**: ⌛ 获取你的计划详情
- **`add`**: ➕ 添加用户到高级会员
- **`rem`**: ➖ 移除用户的高级会员
- **`rembot`**: 移除你的自定义机器人
- **`session`**: 🧵 生成 Pyrogramv2 会话
- **`settings`**: ⚙️ 个性化设置
- **`stats`**: 📊 获取机器人统计信息
- **`plan`**: 🗓️ 查看我们的高级计划
- **`terms`**: 🥺 条款和条件
- **`help`**: ❓ 如果你是新手，获取帮助
- **`cancel`**: 🚫 取消批量处理


## ⚙️ 必需的环境变量

<details>
<summary><b>点击查看必需的环境变量</b></summary>

要运行机器人，你需要配置一些敏感变量。以下是安全设置它们的方法：

- **`API_ID`**: 从 [telegram.org](https://my.telegram.org/auth) 获取你的 API ID
- **`API_HASH`**: 从 [telegram.org](https://my.telegram.org/auth) 获取你的 API Hash
- **`BOT_TOKEN`**: 从 [@BotFather](https://t.me/botfather) 获取你的机器人令牌
- **`OWNER_ID`**: 使用 [@missrose_bot](https://t.me/missrose_bot) 发送 `/info` 获取你的用户 ID
- **`FORCE_SUB`**: 强制订阅的频道 ID
- **`LOG_GROUP`**: 机器人记录消息的群组或频道。转发消息到 [@userinfobot](https://t.me/userinfobot) 获取你的频道/群组 ID
- **`MONGO_DB`**: 用于存储会话数据的 MongoDB URL（推荐用于安全）
  
### 其他配置选项：
- **`STRING`**: （可选）在此处添加你的**高级账户会话字符串**以允许 4GB 文件上传。这是**可选的**，如果不使用可以留空
- **`FREEMIUM_LIMIT`**: 默认为 `0`。设置此值以允许免费用户提取内容。如果设置为 `0`，免费用户将无法访问任何提取功能
- **`PREMIUM_LIMIT`**: 默认为 `500`。这是高级用户的批量限制。你可以自定义此值以允许高级用户在一次批量中处理更多链接/文件
- **`YT_COOKIES`**: 用于下载 YouTube 视频的 Cookies
- **`INSTA_COOKIES`**: 如果你想启用 Instagram 下载，请填写 Cookies

**如何获取 Cookies？**：在 Android 上使用 Mozilla Firefox 或在桌面使用 Chrome 并下载扩展程序获取此 Cookie 或任何 Netscape Cookies (HTTP Cookies) 提取器并使用它

### 货币化（可选）：
- **`WEBSITE_URL`**: （可选）这是你的货币化短链接服务的域名。提供短链接器的域名，例如：`upshrink.com`。**不要**包含 `www` 或 `https://`。默认链接缩短器已设置
- **`AD_API`**: （可选）来自你的链接缩短服务的 API 密钥（例如，**Upshrink**、**AdFly** 等）以货币化链接。输入你的缩短器提供的 API

> **重要提示：** 始终保持你的凭据安全！永远不要在仓库中硬编码它们。使用环境变量或 `.env` 文件。

</details>

---

## 🚀 部署指南

<details>
<summary><b>在 VPS 上部署</b></summary>

## 📋 部署前准备

### 1. 系统要求
- Ubuntu 18.04+ 或 Debian 10+
- Python 3.8+
- 至少 1GB RAM
- 至少 2GB 存储空间

### 2. 获取必要信息
在开始部署前，请确保您已准备好以下信息：
- **API_ID** 和 **API_HASH**：从 [my.telegram.org](https://my.telegram.org) 获取
- **BOT_TOKEN**：从 [@BotFather](https://t.me/BotFather) 获取
- **OWNER_ID**：您的 Telegram 用户 ID
- **MongoDB 连接字符串**：MongoDB Atlas 或自建 MongoDB

## 🚀 部署步骤

### 方法一：使用智能部署脚本（推荐）

如果您希望快速部署，可以使用提供的智能部署脚本：

```bash
# 下载并运行部署脚本
chmod +x deploy.sh
sudo ./deploy.sh
```

#### 🧠 智能检测功能：
- **环境检测**：自动检测已安装的组件，避免重复安装
- **依赖检测**：智能检测Python包，只安装缺失的依赖
- **配置检测**：检测环境变量文件，提示未配置的项目
- **状态总结**：部署完成后提供详细的状态报告

#### 🚀 脚本选项：
1. **快速测试运行**：前台运行，用于测试配置
2. **Screen 后台运行**：简单易用的后台运行方式
3. **Systemd 服务运行**：开机自启，适合生产环境
4. **仅完成环境配置**：只配置环境，稍后手动运行

#### ✨ 智能特性：
- **避免重复安装**：检测现有环境，只安装缺失组件
- **虚拟环境管理**：检测现有虚拟环境，询问是否重新创建
- **依赖优化**：检测关键Python包，智能安装和更新
- **配置验证**：检测环境变量配置完整性
- **错误处理**：详细的错误诊断和解决建议
- **预检测**：网络连接和磁盘空间检测
- **日志记录**：完整的部署日志和错误追踪

### 方法二：手动部署

如果您希望完全手动控制部署过程，请按照以下步骤：

### 步骤 1：更新系统并安装依赖

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装必要的系统包
sudo apt install -y python3-full python3-venv python3-pip ffmpeg git curl wget nano htop screen
```

### 步骤 2：克隆项目

```bash
# 克隆项目到服务器
git clone https://github.com/your-username/Save-Restricted-Content-Bot-v3-main.git
cd Save-Restricted-Content-Bot-v3-main
```

### 步骤 3：创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 验证虚拟环境（应该显示虚拟环境路径）
which python
which pip
```

### 步骤 4：安装 Python 依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证关键依赖安装
pip list | grep -E "(telethon|pyrogram)"
```

### 步骤 5：配置环境变量

```bash
# 复制环境变量模板
cp env.example .env

# 编辑配置文件
nano .env
```

在 `.env` 文件中填入您的配置：

```bash
# Telegram API 配置
API_ID=你的API_ID
API_HASH=你的API_HASH
BOT_TOKEN=你的机器人TOKEN

# 用户配置
OWNER_ID=你的用户ID

# 频道和群组配置
FORCE_SUB=-100你的频道ID
LOG_GROUP=-100你的群组ID

# 数据库配置
MONGO_DB=你的MongoDB连接字符串

# 其他配置（可选）
WEBHOOK_URL=
PORT=5000
```

### 步骤 6：测试运行

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 运行机器人进行测试
python main.py
```

如果看到类似以下输出，说明配置成功：
```
[INFO] 机器人启动成功
[INFO] 所有客户端已连接
```

按 `Ctrl+C` 停止测试。

## 🔄 运行方式选择

根据您的需求，可以选择不同的运行方式：

### 方式一：快速测试运行

**适用场景**：测试配置、调试问题

```bash
# 激活虚拟环境
source venv/bin/activate

# 前台运行
python main.py

# 按 Ctrl+C 停止
```

**优点**：
- 可以直接看到运行日志
- 便于调试和测试
- 配置简单

**缺点**：
- 终端关闭后机器人停止
- 不适合长期运行

### 方式二：Screen 后台运行（推荐）

**适用场景**：个人使用、简单部署

```bash
# 创建新的 screen 会话
screen -S telegram-bot

# 激活虚拟环境
source venv/bin/activate

# 运行机器人
python main.py

# 分离会话：按 Ctrl+A，然后按 D
# 重新连接：screen -r telegram-bot
# 停止会话：screen -S telegram-bot -X quit
```

**优点**：
- 简单易用
- 可以随时连接查看状态
- 适合个人使用

**缺点**：
- 服务器重启后需要手动启动
- 需要记住 screen 命令

### 方式三：Systemd 服务运行

**适用场景**：生产环境、服务器长期运行

```bash
# 创建服务文件
sudo nano /etc/systemd/system/telegram-bot.service
```

服务文件内容：
```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/your/project
Environment=PATH=/path/to/your/project/venv/bin
ExecStart=/path/to/your/project/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable telegram-bot

# 启动服务
sudo systemctl start telegram-bot

# 检查服务状态
sudo systemctl status telegram-bot
```

**优点**：
- 开机自启动
- 自动重启
- 系统级管理
- 适合生产环境

**缺点**：
- 配置相对复杂
- 需要 root 权限

## 🔄 后台运行

### 方法一：使用 Screen（推荐）

```bash
# 创建新的 screen 会话
screen -S telegram-bot

# 激活虚拟环境
source venv/bin/activate

# 运行机器人
python main.py

# 分离会话：按 Ctrl+A，然后按 D
# 重新连接：screen -r telegram-bot
# 停止会话：screen -S telegram-bot -X quit
```

### 方法二：使用 Systemd 服务

```bash
# 创建服务文件
sudo nano /etc/systemd/system/telegram-bot.service
```

服务文件内容：
```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/111/Save-Restricted-Content-Bot-v3-main
Environment=PATH=/root/111/Save-Restricted-Content-Bot-v3-main/venv/bin
ExecStart=/root/111/Save-Restricted-Content-Bot-v3-main/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable telegram-bot

# 启动服务
sudo systemctl start telegram-bot

# 检查服务状态
sudo systemctl status telegram-bot
```

## 🔍 监控和调试

### 查看日志

```bash
# 查看应用日志
tail -f bot.log

# 查看 systemd 服务日志
sudo journalctl -u telegram-bot -f

# 查看最近的错误日志
sudo journalctl -u telegram-bot --since "1 hour ago" | grep ERROR
```

### 检查服务状态

```bash
# 检查进程是否运行
ps aux | grep python

# 检查端口占用
netstat -tulpn | grep :5000

# 检查服务状态
sudo systemctl status telegram-bot
```

## 🚨 常见问题解决

### 脚本错误处理

如果部署脚本运行出错，脚本会自动提供详细的错误信息：

#### 🔍 错误诊断信息：
- **错误位置**：显示出错的具体行号
- **错误代码**：显示系统返回的错误代码
- **执行命令**：显示导致错误的命令
- **可能原因**：根据错误代码提供可能的原因分析
- **解决建议**：提供具体的解决步骤

#### 📝 日志文件：
- **deployment_errors.log**：记录所有错误信息
- **deployment_success.log**：记录成功操作
- **bot.log**：记录机器人运行日志

#### 🛠️ 常见错误代码：
- **错误代码 1**：权限不足、命令不存在、文件不存在
- **错误代码 2**：网络连接问题、软件源配置错误
- **错误代码 127**：命令未找到、软件未安装
- **错误代码 130**：用户中断操作

### 问题 1：ModuleNotFoundError

**原因**：没有在虚拟环境中运行

**解决方案**：
```bash
# 确保激活虚拟环境
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

### 问题 2：externally-managed-environment 错误

**原因**：尝试在系统级 Python 环境中安装包

**解决方案**：
```bash
# 使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 问题 3：aiohttp 安装失败

**原因**：网络超时或镜像源问题

**解决方案**：
```bash
# 方法1: 使用智能修复脚本（推荐）
bash fix_aiohttp.sh

# 方法2: 使用主部署脚本（自动检测地理位置）
bash deploy.sh

# 方法3: 手动安装
pip install --timeout 300 --retries 3 --no-cache-dir aiohttp>=3.8.0

# 方法4: 测试地理位置检测
bash test_location.sh
```

**智能镜像源选择**：
- 🇨🇳 **中国用户**：自动使用阿里云、清华、腾讯云镜像源
- 🌍 **海外用户**：自动使用官方 PyPI 源
- 🔄 **自动重试**：失败时自动切换镜像源

### 问题 4：网络连接错误

**原因**：requirements.txt 中包含无法访问的链接

**解决方案**：
```bash
# 检查 requirements.txt 内容
cat requirements.txt

# 如果包含 Dropbox 链接，请使用官方包
# 确保 requirements.txt 中包含：
# telethon
# pyrogram
# 而不是外部链接
```

### 问题 5：MongoDB 连接失败

**解决方案**：
- 检查 MongoDB 连接字符串格式
- 确保 MongoDB 服务器可访问
- 检查防火墙设置
- 验证数据库用户权限

### 问题 6：权限错误

**解决方案**：
```bash
# 给脚本执行权限
chmod +x main.py

# 检查文件所有者
ls -la main.py
```

## 🔧 维护操作

### 更新机器人

```bash
# 停止服务
sudo systemctl stop telegram-bot

# 进入项目目录
cd /path/to/Save-Restricted-Content-Bot-v3-main

# 拉取最新代码
git pull

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 重启服务
sudo systemctl start telegram-bot
```

### 备份配置

```bash
# 备份环境变量
cp .env .env.backup

# 备份整个项目
tar -czf telegram-bot-backup-$(date +%Y%m%d).tar.gz .
```

</details>

<details>
<summary><b>在 Heroku 上部署</b></summary>

1. Fork 并给仓库点星
2. 点击 [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy)
3. 输入必需变量并点击部署 ✅

</details>

<details>
<summary><b>在 Render 上部署</b></summary>

1. Fork 并给仓库点星
2. 编辑 `config.py` 或在 Render 上设置环境变量
3. 访问 [render.com](https://render.com)，注册/登录
4. 创建新的 Web 服务，选择免费计划
5. 连接你的 GitHub 仓库并部署 ✅

</details>

<details>
<summary><b>在 Koyeb 上部署</b></summary>

1. Fork 并给仓库点星
2. 编辑 `config.py` 或在 Koyeb 上设置环境变量
3. 创建新服务，选择 `Dockerfile` 作为构建类型
4. 连接你的 GitHub 仓库并部署 ✅

</details>


---
### ⚠️ 必须做：保护你的敏感变量

**不要在 GitHub 上暴露敏感变量（例如 `API_ID`、`API_HASH`、`BOT_TOKEN`）。使用环境变量来保持它们的安全。**

### 安全配置变量：

- **在 VPS 或本地机器上：**
  - 使用文本编辑器编辑 `config.py`：
    ```bash
    nano config.py
    ```
  - 或者，导出为环境变量：
    ```bash
    export API_ID=your_api_id
    export API_HASH=your_api_hash
    export BOT_TOKEN=your_bot_token
    ```

- **对于云平台（Heroku、Railway 等）：**
  - 在你的平台仪表板中直接设置环境变量

- **使用 `.env` 文件：**
  - 创建 `.env` 文件并添加你的凭据：
    ```
    API_ID=your_api_id
    API_HASH=your_api_hash
    BOT_TOKEN=your_bot_token
    ```
  - 确保将 `.env` 添加到 `.gitignore` 以防止它被推送到 GitHub

**为什么这很重要？**
如果你的凭据被推送到公共仓库，它们可能会被窃取。始终通过使用环境变量或本地配置文件来保持它们的安全。

---

## 🛠️ 使用条款

访问[使用条款](https://github.com/devgaganin/Save-Restricted-Content-Bot-Repo/blob/master/TERMS_OF_USE.md)页面查看并接受指导原则。

## 重要说明

**注意**：更改条款和命令并不会神奇地让你成为开发者。真正的开发涉及理解代码、编写新功能和调试问题，而不仅仅是重命名东西。如果真有这么简单就好了！


<h3 align="center">
  由 <a href="https://t.me/team_spy_pro"> Gagan </a> 用 ❤️ 开发
</h3>

