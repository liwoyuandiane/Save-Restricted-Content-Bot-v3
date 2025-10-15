# 部署故障排除指南

## 🚨 常见问题及解决方案

### 1. RuntimeError: Event loop is closed

**问题描述：**
```
RuntimeError: Event loop is closed
Exception ignored in: <coroutine object MTProtoSender._recv_loop>
```

**原因：**
- Python asyncio 事件循环没有正确管理
- Telethon/Pyrogram 客户端没有优雅地关闭连接
- 容器停止时没有正确处理信号

**解决方案：**
✅ 已修复 - 代码已更新为使用正确的异步处理：
- 使用 `asyncio.run()` 替代已弃用的 `get_event_loop()`
- 添加了信号处理器来优雅地关闭连接
- 改进了错误处理和资源清理

### 2. 容器不断重启 (BackOff)

**问题描述：**
```
BackOff: Back-off restarting failed container
```

**原因：**
- 应用程序崩溃或异常退出
- 资源不足
- 配置错误

**解决方案：**
1. **检查环境变量**：确保所有必需的环境变量都已正确设置
2. **查看日志**：检查 Runtime Logs 中的具体错误信息
3. **资源限制**：确保没有超出平台限制

### 3. 机器人无响应

**问题描述：**
- 机器人启动成功但无法响应命令
- 发送消息没有回复

**解决方案：**
1. **检查 BOT_TOKEN**：确保机器人令牌正确
2. **检查权限**：确保机器人有必要的权限
3. **检查网络**：确保平台可以访问 Telegram API

## 🔧 部署检查清单

### 环境变量检查
确保以下环境变量已正确设置：

```bash
# 必需变量
API_ID=你的API_ID
API_HASH=你的API_HASH
BOT_TOKEN=你的机器人TOKEN
OWNER_ID=你的用户ID
FORCE_SUB=-100你的频道ID
LOG_GROUP=-100你的群组ID
MONGO_DB=你的MongoDB连接字符串

# 可选变量
FREEMIUM_LIMIT=10
PREMIUM_LIMIT=500
STRING=你的会话字符串（可选）
```

### 部署步骤
1. **Fork 仓库**到你的 GitHub 账户
2. **设置环境变量**在部署平台中
3. **连接 GitHub**仓库
4. **部署**并等待构建完成
5. **检查日志**确保没有错误

## 📊 监控和调试

### 查看日志
根据部署平台查看相应的日志：
- **Heroku**: 在 Dashboard 中查看 Logs
- **Render**: 在 Service 页面查看 Logs
- **Koyeb**: 在 Service 页面查看 Logs
- **VPS**: 使用 `journalctl` 或查看应用日志

### 健康检查
应用现在包含健康检查功能：
- 每30秒检查一次服务状态
- 自动重启不健康的容器
- 详细的连接状态报告

### 常见日志信息
```
正在启动客户端...
Telethon 客户端已启动
Pyrogram 应用已启动
用户机器人已启动... (如果配置了STRING)
运行 start 插件...
运行 login 插件...
运行 batch 插件...
...
```

## 🆘 获取帮助

如果问题仍然存在：

1. **检查完整日志**：复制完整的错误日志
2. **验证环境变量**：确保所有变量都正确设置
3. **重新部署**：尝试重新部署项目
4. **联系支持**：如果问题持续，请联系技术支持

## 📈 性能优化建议

1. **合理设置限制**：
   - `FREEMIUM_LIMIT=10` (免费用户)
   - `PREMIUM_LIMIT=500` (高级用户)

2. **监控资源使用**：
   - 定期检查平台仪表板
   - 避免超出平台限制

3. **定期更新**：
   - 保持代码最新
   - 定期检查依赖更新

---

**注意：** 如果遇到新的错误，请提供完整的错误日志以便更好地诊断问题。
