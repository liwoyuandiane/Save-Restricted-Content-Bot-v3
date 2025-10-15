#!/bin/bash

# 测试地理位置检测功能

echo "🌍 测试地理位置检测功能..."
echo "================================"

# 检测地理位置
detect_location() {
    echo "🔄 正在检测机器地理位置..."
    
    local ip_info=""
    local country=""
    local region=""
    local city=""
    
    # 方法1: 使用 ipinfo.io
    if command -v curl &> /dev/null; then
        echo "📡 使用 ipinfo.io 检测..."
        ip_info=$(curl -s --connect-timeout 10 "https://ipinfo.io/json" 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$ip_info" ]; then
            country=$(echo "$ip_info" | grep -o '"country":"[^"]*"' | cut -d'"' -f4)
            region=$(echo "$ip_info" | grep -o '"region":"[^"]*"' | cut -d'"' -f4)
            city=$(echo "$ip_info" | grep -o '"city":"[^"]*"' | cut -d'"' -f4)
            echo "✅ ipinfo.io 检测成功"
        else
            echo "❌ ipinfo.io 检测失败"
        fi
    else
        echo "❌ curl 命令不存在"
    fi
    
    # 方法2: 使用 ip-api.com (备用)
    if [ -z "$country" ] && command -v curl &> /dev/null; then
        echo "📡 使用 ip-api.com 检测..."
        ip_info=$(curl -s --connect-timeout 10 "http://ip-api.com/json" 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$ip_info" ]; then
            country=$(echo "$ip_info" | grep -o '"country":"[^"]*"' | cut -d'"' -f4)
            region=$(echo "$ip_info" | grep -o '"region":"[^"]*"' | cut -d'"' -f4)
            city=$(echo "$ip_info" | grep -o '"city":"[^"]*"' | cut -d'"' -f4)
            echo "✅ ip-api.com 检测成功"
        else
            echo "❌ ip-api.com 检测失败"
        fi
    fi
    
    # 显示检测结果
    if [ -n "$country" ]; then
        echo ""
        echo "📍 检测结果："
        echo "   国家: $country"
        echo "   地区: $region"
        echo "   城市: $city"
        
        # 推荐镜像源
        case "$country" in
            "CN"|"China")
                echo "🇨🇳 推荐镜像源："
                echo "   - https://mirrors.aliyun.com/pypi/simple"
                echo "   - https://pypi.tuna.tsinghua.edu.cn/simple"
                echo "   - https://mirrors.cloud.tencent.com/pypi/simple"
                ;;
            "US"|"United States")
                echo "🇺🇸 推荐镜像源："
                echo "   - https://pypi.org/simple"
                echo "   - https://pypi.python.org/simple"
                ;;
            "JP"|"Japan")
                echo "🇯🇵 推荐镜像源："
                echo "   - https://pypi.org/simple"
                echo "   - https://pypi.python.org/simple"
                ;;
            "SG"|"Singapore")
                echo "🇸🇬 推荐镜像源："
                echo "   - https://pypi.org/simple"
                echo "   - https://pypi.python.org/simple"
                ;;
            "HK"|"Hong Kong")
                echo "🇭🇰 推荐镜像源："
                echo "   - https://pypi.org/simple"
                echo "   - https://pypi.python.org/simple"
                ;;
            *)
                echo "🌍 推荐镜像源："
                echo "   - https://pypi.org/simple"
                echo "   - https://pypi.python.org/simple"
                ;;
        esac
    else
        echo "❌ 无法检测地理位置"
        echo "🌍 使用默认镜像源："
        echo "   - https://pypi.org/simple"
        echo "   - https://pypi.python.org/simple"
    fi
}

# 运行检测
detect_location

echo ""
echo "✅ 地理位置检测测试完成"
