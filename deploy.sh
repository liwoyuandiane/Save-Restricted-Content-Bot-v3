#!/bin/bash

# TG消息提取器机器人 v3 - 智能部署脚本
# 此脚本提供多种运行方式，详细步骤请参考 README.md

set -e

# 错误处理函数
handle_error() {
    local line_number=$1
    local error_code=$2
    local command=$3
    
    echo ""
    echo "❌ 脚本执行出错！"
    echo "================================================"
    echo "📍 错误位置: 第 $line_number 行"
    echo "🔢 错误代码: $error_code"
    echo "💻 执行命令: $command"
    echo ""
    
    # 根据错误代码提供具体的解决建议
    case $error_code in
        1)
            echo "🔍 可能原因："
            echo "   - 权限不足，请确保使用 root 用户运行"
            echo "   - 命令不存在，请检查系统环境"
            echo "   - 文件或目录不存在"
            ;;
        2)
            echo "🔍 可能原因："
            echo "   - 网络连接问题，无法下载包"
            echo "   - 软件源配置错误"
            echo "   - 包管理器锁定"
            ;;
        127)
            echo "🔍 可能原因："
            echo "   - 命令未找到，请检查 PATH 环境变量"
            echo "   - 软件未安装"
            ;;
        130)
            echo "🔍 可能原因："
            echo "   - 用户按 Ctrl+C 中断了脚本"
            echo "   - 这是正常的中断操作"
            ;;
        *)
            echo "🔍 可能原因："
            echo "   - 未知错误，请查看详细日志"
            ;;
    esac
    
    echo ""
    echo "🛠️  建议解决方案："
    echo "1. 检查网络连接"
    echo "2. 更新系统包列表: apt update"
    echo "3. 检查磁盘空间: df -h"
    echo "4. 查看系统日志: journalctl -xe"
    echo "5. 重新运行脚本"
    echo ""
    echo "📚 更多帮助请查看 README.md 中的常见问题解决方案"
    echo "🆘 如问题持续存在，请提供以上错误信息寻求帮助"
    
    exit $error_code
}

# 设置错误陷阱
trap 'handle_error $LINENO $? "$BASH_COMMAND"' ERR

# 命令执行函数（带错误处理）
run_command() {
    local description="$1"
    local command="$2"
    
    echo "🔄 $description..."
    if eval "$command"; then
        echo "✅ $description 完成"
    else
        local exit_code=$?
        echo "❌ $description 失败 (退出代码: $exit_code)"
        handle_error $LINENO $exit_code "$command"
    fi
}

# 网络连接检测函数
check_network() {
    echo "🌐 检测网络连接..."
    
    # 检测DNS解析
    if ! nslookup google.com &> /dev/null; then
        echo "❌ DNS 解析失败"
        echo "🔧 建议解决方案："
        echo "   - 检查网络连接"
        echo "   - 更换DNS服务器 (8.8.8.8, 1.1.1.1)"
        echo "   - 检查防火墙设置"
        return 1
    fi
    
    # 检测HTTP连接
    if ! curl -s --connect-timeout 10 http://httpbin.org/get &> /dev/null; then
        echo "❌ HTTP 连接失败"
        echo "🔧 建议解决方案："
        echo "   - 检查网络连接"
        echo "   - 检查代理设置"
        echo "   - 检查防火墙设置"
        return 1
    fi
    
    echo "✅ 网络连接正常"
    return 0
}

# 磁盘空间检测函数
check_disk_space() {
    echo "💾 检测磁盘空间..."
    
    local available_space=$(df / | awk 'NR==2 {print $4}')
    local required_space=1048576  # 1GB in KB
    
    if [ $available_space -lt $required_space ]; then
        echo "❌ 磁盘空间不足"
        echo "🔧 当前可用空间: $(($available_space / 1024))MB"
        echo "🔧 建议至少需要: $(($required_space / 1024))MB"
        echo "🛠️  建议解决方案："
        echo "   - 清理临时文件: apt clean"
        echo "   - 删除不需要的包: apt autoremove"
        echo "   - 清理日志文件: journalctl --vacuum-time=7d"
        return 1
    fi
    
    echo "✅ 磁盘空间充足: $(($available_space / 1024))MB 可用"
    return 0
}

# 检测机器地理位置和推荐镜像源
detect_location_and_mirrors() {
    echo "🌍 检测机器地理位置和推荐镜像源..."
    
    # 尝试获取公网IP和地理位置
    local ip_info=""
    local country=""
    local region=""
    
    # 方法1: 使用 ipinfo.io
    if command -v curl &> /dev/null; then
        ip_info=$(curl -s --connect-timeout 10 "https://ipinfo.io/json" 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$ip_info" ]; then
            country=$(echo "$ip_info" | grep -o '"country":"[^"]*"' | cut -d'"' -f4)
            region=$(echo "$ip_info" | grep -o '"region":"[^"]*"' | cut -d'"' -f4)
        fi
    fi
    
    # 方法2: 使用 ip-api.com (备用)
    if [ -z "$country" ] && command -v curl &> /dev/null; then
        ip_info=$(curl -s --connect-timeout 10 "http://ip-api.com/json" 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$ip_info" ]; then
            country=$(echo "$ip_info" | grep -o '"country":"[^"]*"' | cut -d'"' -f4)
            region=$(echo "$ip_info" | grep -o '"region":"[^"]*"' | cut -d'"' -f4)
        fi
    fi
    
    # 根据地理位置推荐镜像源
    local recommended_mirrors=()
    
    if [ -n "$country" ]; then
        echo "📍 检测到机器位置: $country $region"
        
        case "$country" in
            "CN"|"China")
                recommended_mirrors=(
                    "https://mirrors.aliyun.com/pypi/simple"
                    "https://pypi.tuna.tsinghua.edu.cn/simple"
                    "https://mirrors.cloud.tencent.com/pypi/simple"
                    "https://pypi.org/simple"
                )
                echo "🇨🇳 推荐使用国内镜像源"
                ;;
            "US"|"United States")
                recommended_mirrors=(
                    "https://pypi.org/simple"
                    "https://pypi.python.org/simple"
                )
                echo "🇺🇸 推荐使用官方源"
                ;;
            "JP"|"Japan")
                recommended_mirrors=(
                    "https://pypi.org/simple"
                    "https://pypi.python.org/simple"
                )
                echo "🇯🇵 推荐使用官方源"
                ;;
            "SG"|"Singapore")
                recommended_mirrors=(
                    "https://pypi.org/simple"
                    "https://pypi.python.org/simple"
                )
                echo "🇸🇬 推荐使用官方源"
                ;;
            "HK"|"Hong Kong")
                recommended_mirrors=(
                    "https://pypi.org/simple"
                    "https://pypi.python.org/simple"
                )
                echo "🇭🇰 推荐使用官方源"
                ;;
            "DE"|"Germany")
                recommended_mirrors=(
                    "https://pypi.org/simple"
                    "https://pypi.python.org/simple"
                )
                echo "🇩🇪 推荐使用官方源"
                ;;
            *)
                recommended_mirrors=(
                    "https://pypi.org/simple"
                    "https://pypi.python.org/simple"
                )
                echo "🌍 推荐使用官方源"
                ;;
        esac
    else
        echo "⚠️  无法检测地理位置，使用默认镜像源"
        recommended_mirrors=(
            "https://pypi.org/simple"
            "https://pypi.python.org/simple"
        )
    fi
    
    # 返回推荐的镜像源数组
    echo "${recommended_mirrors[@]}"
}

# 安装依赖重试函数
install_dependencies_with_retry() {
    local upgrade_flag="$1"
    local max_retries=3
    local retry_delay=10
    
    # 检测地理位置并获取推荐镜像源
    local mirrors=($(detect_location_and_mirrors))
    
    for ((attempt=1; attempt<=max_retries; attempt++)); do
        echo "🔄 尝试安装依赖 (第 $attempt/$max_retries 次)..."
        
        # 配置 pip 超时和重试
        local pip_cmd="pip install --timeout 300 --retries 3 --no-cache-dir"
        if [ -n "$upgrade_flag" ]; then
            pip_cmd="$pip_cmd $upgrade_flag"
        fi
        pip_cmd="$pip_cmd -r requirements.txt"
        
        if eval "$pip_cmd"; then
            echo "✅ Python 依赖安装成功"
            return 0
        else
            echo "❌ 第 $attempt 次安装失败"
            if [ $attempt -lt $max_retries ]; then
                echo "⏳ 等待 $retry_delay 秒后重试..."
                sleep $retry_delay
                retry_delay=$((retry_delay * 2))  # 指数退避
            fi
        fi
    done
    
    echo "❌ 默认安装失败，尝试使用推荐的镜像源..."
    
    # 尝试使用推荐的镜像源
    for mirror in "${mirrors[@]}"; do
        echo "🔄 尝试使用镜像源: $mirror"
        if pip install --timeout 300 --retries 3 --no-cache-dir -i "$mirror" $upgrade_flag -r requirements.txt; then
            echo "✅ 使用镜像源 $mirror 安装成功"
            return 0
        fi
    done
    
    echo "❌ 推荐镜像源也失败了，尝试其他备用镜像源..."
    
    # 备用镜像源（全球通用）
    local backup_mirrors=(
        "https://pypi.org/simple"
        "https://pypi.python.org/simple"
        "https://mirrors.aliyun.com/pypi/simple"
        "https://pypi.tuna.tsinghua.edu.cn/simple"
        "https://mirrors.cloud.tencent.com/pypi/simple"
    )
    
    for mirror in "${backup_mirrors[@]}"; do
        echo "🔄 尝试使用备用镜像源: $mirror"
        if pip install --timeout 300 --retries 3 --no-cache-dir -i "$mirror" $upgrade_flag -r requirements.txt; then
            echo "✅ 使用备用镜像源 $mirror 安装成功"
            return 0
        fi
    done
    
    echo "❌ 所有安装方法都失败了"
    return 1
}

echo "🚀 TG消息提取器机器人 v3 - 智能部署脚本"
echo "================================================"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用 root 用户运行此脚本"
    exit 1
fi

echo "🔍 正在检测当前环境..."

# 环境检测函数
check_environment() {
    local missing_deps=()
    local existing_deps=()
    
    # 检测系统依赖
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    else
        existing_deps+=("python3")
    fi
    
    if ! command -v pip3 &> /dev/null; then
        missing_deps+=("pip3")
    else
        existing_deps+=("pip3")
    fi
    
    if ! command -v ffmpeg &> /dev/null; then
        missing_deps+=("ffmpeg")
    else
        existing_deps+=("ffmpeg")
    fi
    
    # 检测项目文件
    if [ -d "venv" ]; then
        existing_deps+=("虚拟环境")
    fi
    
    if [ -f ".env" ]; then
        existing_deps+=("环境变量文件")
    fi
    
    if [ -f "requirements.txt" ]; then
        existing_deps+=("依赖文件")
    fi
    
    # 显示检测结果
    if [ ${#existing_deps[@]} -gt 0 ]; then
        echo "✅ 已存在的组件："
        for dep in "${existing_deps[@]}"; do
            echo "   - $dep"
        done
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo "❌ 需要安装的组件："
        for dep in "${missing_deps[@]}"; do
            echo "   - $dep"
        done
    else
        echo "✅ 所有基础组件已存在"
    fi
    
    echo ""
}

# 执行环境检测
check_environment

# 预检测网络和磁盘空间
echo "🔍 执行预检测..."
if ! check_network; then
    echo "⚠️  网络连接有问题，但脚本将继续运行"
    echo "   如果后续安装失败，请检查网络连接"
    echo ""
fi

if ! check_disk_space; then
    echo "⚠️  磁盘空间不足，但脚本将继续运行"
    echo "   如果后续安装失败，请清理磁盘空间"
    echo ""
fi

echo "📋 此脚本将执行以下操作："
echo "1. 检测并安装缺失的系统依赖"
echo "2. 检测并创建/更新虚拟环境"
echo "3. 检测并安装Python依赖"
echo "4. 检测并配置环境变量"
echo "5. 选择运行方式"
echo ""

read -p "是否继续？(Y/n): " -n 1 -r
echo
# 如果用户直接按回车，默认为 y
if [[ -z $REPLY || $REPLY =~ ^[Yy]$ ]]; then
    echo "✅ 继续执行部署..."
else
    echo "❌ 部署已取消"
    exit 1
fi

echo "🔧 步骤 1: 检测并安装系统依赖..."
echo "正在检测系统环境..."

# 检测并更新包列表
echo "📦 检查包列表状态..."
if ! apt list --installed | grep -q "python3-full\|python3-venv\|python3-pip"; then
    echo "📦 更新包列表..."
    run_command "更新包列表" "apt update -y"
else
    echo "✅ 包列表已是最新"
    # 即使包已安装，也检查是否需要更新
    echo "🔄 检查包更新..."
    run_command "检查包更新" "apt update -y" || echo "⚠️  包更新检查失败，继续安装"
fi

# 检测 Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，正在安装..."
    run_command "安装 Python3" "apt install -y python3-full"
else
    echo "✅ Python3 已安装: $(python3 --version)"
fi

# 检测 python3-venv
if ! python3 -m venv --help &> /dev/null; then
    echo "❌ python3-venv 未安装，正在安装..."
    run_command "安装 python3-venv" "apt install -y python3-venv"
else
    echo "✅ python3-venv 已安装"
fi

# 检测 pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未安装，正在安装..."
    run_command "安装 pip3" "apt install -y python3-pip"
else
    echo "✅ pip3 已安装: $(pip3 --version)"
fi

# 检测 ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg 未安装，正在安装..."
    run_command "安装 ffmpeg" "apt install -y ffmpeg"
else
    echo "✅ ffmpeg 已安装: $(ffmpeg -version | head -n1)"
fi

# 检测其他工具
TOOLS=("git" "curl" "wget" "nano" "htop" "screen")
for tool in "${TOOLS[@]}"; do
    if ! command -v $tool &> /dev/null; then
        echo "❌ $tool 未安装，正在安装..."
        run_command "安装 $tool" "apt install -y $tool"
    else
        echo "✅ $tool 已安装"
    fi
done

echo "✅ 系统依赖检测完成"

echo "🐍 步骤 2: 检测并创建虚拟环境..."
if [ -d "venv" ]; then
    echo "✅ 虚拟环境已存在"
    echo "⚠️  是否重新创建虚拟环境？"
    read -p "重新创建将删除现有环境 (y/N): " -n 1 -r
    echo
    # 如果用户直接按回车，默认为 N（不重新创建）
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  删除现有虚拟环境..."
        run_command "删除现有虚拟环境" "rm -rf venv"
        echo "🐍 创建新的虚拟环境..."
        run_command "创建虚拟环境" "python3 -m venv venv"
    else
        echo "✅ 使用现有虚拟环境"
    fi
else
    echo "🐍 创建虚拟环境..."
    run_command "创建虚拟环境" "python3 -m venv venv"
fi

echo "🔌 激活虚拟环境..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 虚拟环境激活失败，activate 文件不存在"
    handle_error $LINENO 1 "source venv/bin/activate"
fi

echo "📦 步骤 3: 检测并安装Python依赖..."
echo "正在检测Python包..."

# 检测pip版本并升级
CURRENT_PIP_VERSION=$(pip --version | cut -d' ' -f2)
echo "📦 当前pip版本: $CURRENT_PIP_VERSION"
echo "⬆️  升级pip..."
run_command "升级 pip" "pip install --upgrade pip"

# 检测关键依赖
KEY_PACKAGES=("telethon" "pyrogram" "python-dotenv" "motor" "flask" "psutil" "aiohttp" "aiofiles")
MISSING_PACKAGES=()
OUTDATED_PACKAGES=()

for package in "${KEY_PACKAGES[@]}"; do
    if ! pip show $package &> /dev/null; then
        echo "❌ $package 未安装"
        MISSING_PACKAGES+=($package)
    else
        echo "✅ $package 已安装"
        # 检查是否需要更新
        if pip list --outdated | grep -q "^$package "; then
            echo "🔄 $package 有可用更新"
            OUTDATED_PACKAGES+=($package)
        fi
    fi
done

# 检查requirements.txt是否存在
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt 文件不存在"
    echo "🔧 创建默认的 requirements.txt..."
    run_command "创建 requirements.txt" "cat > requirements.txt << 'EOF'
telethon
pyrogram
python-dotenv
psutil
opencv-python-headless
devgagantools
aiofiles
aiohttp
telethon-tgcrypto
motor
pymongo
pytz
Pillow
tgcrypto
flask
werkzeug==2.2.2
mutagen
yt-dlp
requests
cryptography
EOF"
    echo "✅ 已创建 requirements.txt"
fi

# 安装依赖
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo "📦 安装缺失的Python依赖..."
    install_dependencies_with_retry
elif [ ${#OUTDATED_PACKAGES[@]} -gt 0 ]; then
    echo "🔄 更新过时的Python依赖..."
    install_dependencies_with_retry "--upgrade"
else
    echo "✅ 所有关键依赖已安装且为最新版本"
    echo "🔄 检查是否需要更新其他依赖..."
    install_dependencies_with_retry "--upgrade" || echo "⚠️  依赖更新检查失败，继续"
fi

echo "✅ Python依赖检测完成"

echo "⚙️ 步骤 4: 检测并配置环境变量..."
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo "📋 复制环境变量模板..."
        cp env.example .env
        echo "✅ 已创建 .env 文件"
    else
        echo "🔧 创建默认环境变量文件..."
        cat > .env << 'EOF'
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
EOF
        echo "✅ 已创建默认 .env 文件"
    fi
    
    echo ""
    echo "⚠️  请编辑配置文件："
    echo "   nano .env"
    echo ""
    echo "📝 需要填入的配置："
    echo "   API_ID=你的API_ID"
    echo "   API_HASH=你的API_HASH"
    echo "   BOT_TOKEN=你的机器人TOKEN"
    echo "   OWNER_ID=你的用户ID"
    echo "   FORCE_SUB=-100你的频道ID"
    echo "   LOG_GROUP=-100你的群组ID"
    echo "   MONGO_DB=你的MongoDB连接字符串"
    echo ""
    read -p "配置完成后按 Enter 继续..."
else
    echo "✅ 环境变量文件已存在"
    
    # 检测关键配置是否已填写
    if grep -q "你的API_ID\|你的API_HASH\|你的机器人TOKEN" .env; then
        echo "⚠️  检测到未配置的变量，请编辑 .env 文件"
        echo "   nano .env"
        echo ""
        read -p "配置完成后按 Enter 继续..."
    else
        echo "✅ 环境变量配置完整"
    fi
fi

echo ""
echo "🚀 步骤 5: 选择运行方式"
echo "================================"
echo "请选择您希望的运行方式："
echo ""
echo "1) 快速测试运行（前台运行，用于测试）"
echo "2) Screen 后台运行（推荐，简单易用）"
echo "3) Systemd 服务运行（开机自启，生产环境推荐）"
echo "4) 仅完成环境配置，稍后手动运行"
echo ""

read -p "请选择 (1-4) [默认: 2]: " -n 1 -r
echo
echo ""

# 如果用户直接按回车，默认为 2 (Screen 后台运行)
if [[ -z $REPLY ]]; then
    REPLY=2
fi

case $REPLY in
    1)
        echo "🚀 选择：快速测试运行"
        echo "================================"
        echo "⚠️  机器人将在前台运行，按 Ctrl+C 停止"
        echo ""
        read -p "按 Enter 开始运行机器人..."
        echo "启动机器人..."
        source venv/bin/activate
        if [ -f "venv/bin/python" ]; then
            venv/bin/python main.py
        else
            python3 main.py
        fi
        ;;
    2)
        echo "🚀 选择：Screen 后台运行"
        echo "================================"
        echo "正在创建 Screen 会话..."
        screen -dmS telegram-bot bash -c "cd $(pwd) && source venv/bin/activate && python3 main.py || venv/bin/python main.py"
        echo "✅ Screen 会话已创建"
        echo ""
        echo "🔧 Screen 管理命令："
        echo "  查看会话: screen -ls"
        echo "  连接会话: screen -r telegram-bot"
        echo "  分离会话: Ctrl+A 然后按 D"
        echo "  停止会话: screen -S telegram-bot -X quit"
        echo ""
        echo "📊 当前会话状态："
        screen -ls
        ;;
    3)
        echo "🚀 选择：Systemd 服务运行"
        echo "================================"
        echo "正在创建 systemd 服务..."
        
        cat > /etc/systemd/system/telegram-bot.service << EOF
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        echo "🚀 启动服务..."
        systemctl daemon-reload
        systemctl enable telegram-bot
        systemctl start telegram-bot
        
        echo "✅ Systemd 服务已创建并启动"
        echo ""
        echo "📊 服务状态："
        systemctl status telegram-bot --no-pager -l
        echo ""
        echo "🔧 管理命令："
        echo "  查看状态: systemctl status telegram-bot"
        echo "  查看日志: journalctl -u telegram-bot -f"
        echo "  重启服务: systemctl restart telegram-bot"
        echo "  停止服务: systemctl stop telegram-bot"
        ;;
    4)
        echo "🚀 选择：仅完成环境配置"
        echo "================================"
        echo "✅ 环境配置完成！"
        echo ""
        echo "📝 手动运行命令："
        echo "  cd $(pwd)"
        echo "  source venv/bin/activate"
        echo "  venv/bin/python main.py"
        echo ""
        echo "💡 后台运行建议："
        echo "  screen -S bot"
        echo "  source venv/bin/activate"
        echo "  venv/bin/python main.py"
        echo "  # 按 Ctrl+A 然后按 D 分离"
        ;;
    *)
        echo "❌ 无效选择，默认完成环境配置"
        echo "✅ 环境配置完成！请手动运行机器人"
        ;;
esac

echo ""
echo "🎉 部署完成！"
echo "================================================"

# 部署总结
echo "📊 部署总结："
echo "📁 项目目录: $(pwd)"
echo "🔧 虚拟环境: $(pwd)/venv"
echo "📝 日志文件: $(pwd)/bot.log"
echo "⚙️  配置文件: $(pwd)/.env"

# 检查最终状态
echo ""
echo "🔍 最终状态检查："

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "✅ 虚拟环境: 已创建"
else
    echo "❌ 虚拟环境: 未创建"
fi

# 检查环境变量文件
if [ -f ".env" ]; then
    echo "✅ 环境变量: 已配置"
else
    echo "❌ 环境变量: 未配置"
fi

# 检查关键Python包
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    if pip show telethon &> /dev/null && pip show pyrogram &> /dev/null; then
        echo "✅ Python依赖: 已安装"
    else
        echo "❌ Python依赖: 安装不完整"
    fi
fi

# 创建错误日志记录
log_error() {
    local error_msg="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] ERROR: $error_msg" >> deployment_errors.log
}

# 创建成功日志记录
log_success() {
    local success_msg="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] SUCCESS: $success_msg" >> deployment_success.log
}

echo ""
echo "📚 更多信息请查看 README.md"
echo "🆘 如遇问题，请检查日志文件或查看常见问题解决方案"
echo ""
echo "📝 日志文件："
echo "   - 错误日志: deployment_errors.log"
echo "   - 成功日志: deployment_success.log"
echo "   - 应用日志: bot.log"
