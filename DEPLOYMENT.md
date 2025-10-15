# TG消息提取器部署指南

## 🚀 部署选项

### 1. 准备工作

#### 获取必要的 API 密钥：
- **API_ID** 和 **API_HASH**: 从 [my.telegram.org](https://my.telegram.org) 获取
- **BOT_TOKEN**: 从 [@BotFather](https://t.me/BotFather) 创建机器人获取
- **MongoDB**: 从 [MongoDB Atlas](https://www.mongodb.com/atlas) 获取连接字符串

#### 创建频道和群组：
- 创建一个公开频道作为强制订阅频道
- 创建一个群组作为日志群组
- 将机器人添加为管理员

### 2. 环境变量配置

在部署平台中设置以下环境变量：

```bash
# 必需配置
API_ID=你的API_ID
API_HASH=你的API_HASH
BOT_TOKEN=你的机器人TOKEN
OWNER_ID=你的用户ID
FORCE_SUB=-100你的频道ID
LOG_GROUP=-100你的群组ID
MONGO_DB=你的MongoDB连接字符串

# 可选配置
FREEMIUM_LIMIT=10
PREMIUM_LIMIT=500
STRING=你的会话字符串
```

### 3. 部署平台

#### VPS 部署
1. 克隆仓库到服务器
2. 安装依赖：`pip install -r requirements.txt`
3. 配置环境变量
4. 运行：`python3 main.py`

#### Heroku 部署
1. Fork 仓库
2. 在 Heroku 中创建新应用
3. 连接 GitHub 仓库
4. 设置环境变量
5. 部署

#### Render 部署
1. Fork 仓库
2. 在 Render 中创建 Web 服务
3. 连接 GitHub 仓库
4. 设置环境变量
5. 部署

#### Koyeb 部署
1. Fork 仓库
2. 在 Koyeb 中创建服务
3. 选择 Dockerfile 构建
4. 连接 GitHub 仓库
5. 设置环境变量
6. 部署

### 4. 验证部署

1. 检查机器人是否在线
2. 发送 `/start` 测试
3. 测试消息提取功能

## 🔧 常见问题

### Q: 机器人无法启动？
A: 检查环境变量是否正确设置，特别是 API_ID、API_HASH 和 BOT_TOKEN

### Q: 无法访问频道？
A: 确保机器人是频道管理员，并且 FORCE_SUB 设置正确

### Q: 数据库连接失败？
A: 检查 MONGO_DB 连接字符串是否正确，确保 IP 白名单设置

## 📞 支持

如有问题，请联系：
- GitHub Issues
- Telegram: @你的用户名

## 📄 许可证

本项目基于 GNU General Public License v3.0 许可证开源。
