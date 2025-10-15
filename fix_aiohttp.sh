#!/bin/bash

# 修复 aiohttp 安装问题的快速脚本

echo "🔧 修复 aiohttp 安装问题..."
echo "================================"

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 虚拟环境不存在，请先运行 deploy.sh"
    exit 1
fi

# 检测地理位置
detect_location() {
    echo "🌍 检测机器地理位置..."
    
    local country=""
    local region=""
    
    # 使用 ipinfo.io 检测
    if command -v curl &> /dev/null; then
        local ip_info=$(curl -s --connect-timeout 10 "https://ipinfo.io/json" 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$ip_info" ]; then
            country=$(echo "$ip_info" | grep -o '"country":"[^"]*"' | cut -d'"' -f4)
            region=$(echo "$ip_info" | grep -o '"region":"[^"]*"' | cut -d'"' -f4)
        fi
    fi
    
    if [ -n "$country" ]; then
        echo "📍 检测到机器位置: $country $region"
        case "$country" in
            "CN"|"China")
                echo "🇨🇳 推荐使用国内镜像源"
                return 0
                ;;
            *)
                echo "🌍 推荐使用官方源"
                return 1
                ;;
        esac
    else
        echo "⚠️  无法检测地理位置，使用默认策略"
        return 1
    fi
}

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 检测地理位置并选择策略
if detect_location; then
    # 中国用户：优先使用国内镜像源
    echo "🔄 使用国内镜像源策略..."
    
    local mirrors=(
        "https://mirrors.aliyun.com/pypi/simple"
        "https://pypi.tuna.tsinghua.edu.cn/simple"
        "https://mirrors.cloud.tencent.com/pypi/simple"
        "https://pypi.org/simple"
    )
    
    for mirror in "${mirrors[@]}"; do
        echo "🔄 尝试使用镜像源: $mirror"
        if pip install --timeout 300 --retries 3 --no-cache-dir -i "$mirror" aiohttp>=3.8.0; then
            echo "✅ aiohttp 安装成功"
            exit 0
        fi
    done
else
    # 海外用户：优先使用官方源
    echo "🔄 使用官方源策略..."
    
    # 方法1: 使用官方源
    echo "方法1: 使用官方源..."
    if pip install --timeout 300 --retries 3 --no-cache-dir aiohttp>=3.8.0; then
        echo "✅ aiohttp 安装成功"
        exit 0
    fi
    
    # 方法2: 使用官方备用源
    echo "方法2: 使用官方备用源..."
    if pip install --timeout 300 --retries 3 --no-cache-dir -i https://pypi.python.org/simple aiohttp>=3.8.0; then
        echo "✅ aiohttp 安装成功"
        exit 0
    fi
    
    # 方法3: 安装特定版本
    echo "方法3: 安装特定版本..."
    if pip install --timeout 300 --retries 3 --no-cache-dir aiohttp==3.8.6; then
        echo "✅ aiohttp 安装成功"
        exit 0
    fi
    
    # 方法4: 尝试国内镜像源作为备用
    echo "方法4: 尝试国内镜像源作为备用..."
    local backup_mirrors=(
        "https://mirrors.aliyun.com/pypi/simple"
        "https://pypi.tuna.tsinghua.edu.cn/simple"
    )
    
    for mirror in "${backup_mirrors[@]}"; do
        echo "🔄 尝试使用备用镜像源: $mirror"
        if pip install --timeout 300 --retries 3 --no-cache-dir -i "$mirror" aiohttp>=3.8.0; then
            echo "✅ aiohttp 安装成功"
            exit 0
        fi
    done
fi

echo "❌ 所有方法都失败了"
echo "🛠️  建议解决方案："
echo "1. 检查网络连接: ping pypi.org"
echo "2. 尝试更换 DNS 服务器: echo 'nameserver 8.8.8.8' >> /etc/resolv.conf"
echo "3. 使用代理服务器: pip install --proxy http://proxy:port aiohttp>=3.8.0"
echo "4. 手动下载安装包"
echo "5. 检查防火墙设置"

exit 1
