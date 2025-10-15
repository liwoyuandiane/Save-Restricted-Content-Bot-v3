# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import os
import logging
from flask import Flask, render_template, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

@app.route("/")
def welcome():
    """渲染欢迎页面"""
    try:
        return render_template("welcome.html")
    except Exception as e:
        logger.error(f"渲染欢迎页面时出错: {e}")
        return "欢迎使用 TG消息提取器机器人 v3", 200

@app.route("/health")
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "service": "TG消息提取器机器人 v3",
        "version": "3.0.0"
    }), 200

@app.route("/status")
def status():
    """状态检查端点"""
    return jsonify({
        "status": "running",
        "message": "机器人正在运行"
    }), 200

if __name__ == "__main__":
    # 从环境变量获取端口，默认为5000
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    logger.info(f"启动Flask应用，端口: {port}, 调试模式: {debug}")
    app.run(host="0.0.0.0", port=port, debug=debug)
