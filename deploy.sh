#!/bin/bash

# Telegram 自动签到脚本 - 一键部署脚本

set -e

echo "=================================="
echo "Telegram 自动签到 - 部署脚本"
echo "=================================="
echo ""

# 检查 Python 版本
echo "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，正在安装..."
    sudo apt update
    sudo apt install python3 python3-pip python3-venv -y
else
    echo "✅ Python3 已安装: $(python3 --version)"
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo ""
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ 依赖安装完成"

# 配置环境变量
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  未找到 .env 文件，开始配置向导..."
    
    # 创建基础配置文件
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        # 创建一个基础的 .env 模板
        cat > .env << 'EOF'
# Telegram API 配置
API_ID=
API_HASH=
PHONE_NUMBER=

# 签到时间配置
CHECKIN_HOUR=9
CHECKIN_MINUTE=0

# 时区配置
TIMEZONE=Asia/Shanghai

# 随机延迟配置（秒）
RANDOM_DELAY_MIN=0
RANDOM_DELAY_MAX=300
EOF
    fi
    
    echo "✅ 已创建 .env 文件"
    echo ""
    echo "=" * 60
    echo "📋 配置步骤 1/2：Telegram API 凭证"
    echo "=" * 60
    echo ""
    echo "1. 访问 https://my.telegram.org"
    echo "2. 使用手机号登录"
    echo "3. 点击 'API development tools'"
    echo "4. 创建应用获取 API_ID 和 API_HASH"
    echo ""
    
    # 输入 API 凭证
    read -p "请输入 API_ID (数字): " api_id
    read -p "请输入 API_HASH (32位字符串): " api_hash
    read -p "请输入手机号 (如 +8613800138000): " phone_number
    
    # 写入配置
    sed -i "s/API_ID=.*/API_ID=$api_id/" .env
    sed -i "s/API_HASH=.*/API_HASH=$api_hash/" .env
    sed -i "s/PHONE_NUMBER=.*/PHONE_NUMBER=$phone_number/" .env
    
    echo ""
    echo "✅ API 凭证配置完成"
    echo ""
    echo "=" * 60
    echo "📋 配置步骤 2/2：签到目标"
    echo "=" * 60
    echo ""
    echo "现在配置签到目标（机器人或群组）"
    echo "支持添加无限个目标，可自由选择按钮或命令方式"
    echo ""
    read -p "按回车键继续..." 
    
    # 运行交互式配置工具
    python3 setup_targets.py
    
else
    echo "✅ .env 配置文件已存在"
    echo ""
    read -p "是否重新配置签到目标? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 setup_targets.py
    fi
fi

# 测试配置
echo ""
echo "测试配置..."
python3 -c "import config; print('✅ 配置加载成功')" || {
    echo "❌ 配置加载失败，请检查 .env 文件"
    exit 1
}

echo ""
echo "=================================="
echo "✅ 部署完成！"
echo "=================================="
echo ""
echo "下一步操作："
echo ""
echo "1. 首次登录验证:"
echo "   source venv/bin/activate"
echo "   python test_login.py"
echo ""
echo "2. 测试签到:"
echo "   python manual_checkin.py"
echo ""
echo "3. 设置自动运行:"
echo "   chmod +x setup_service.sh"
echo "   sudo ./setup_service.sh"
echo ""
echo "或使用后台脚本:"
echo "   chmod +x run.sh"
echo "   ./run.sh"
echo ""
echo "=================================="
