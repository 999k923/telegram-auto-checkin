#!/bin/bash

###############################################################################
# Telegram 自动签到机器人 - 一键安装脚本
# 适用于全新的 Ubuntu/Debian 系统
###############################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

###############################################################################
# 主函数
###############################################################################

clear
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        Telegram 自动签到机器人 - 一键部署脚本               ║"
echo "║                                                              ║"
echo "║        支持：Ubuntu 18.04+ / Debian 10+                     ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 确认开始安装
read -p "是否开始安装? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "安装已取消"
    exit 0
fi

###############################################################################
# 步骤 1: 检查系统环境
###############################################################################

print_header "步骤 1/6: 检查系统环境"

# 检查是否为 root 用户
if [ "$EUID" -eq 0 ]; then 
    print_warning "检测到使用 root 用户运行"
    print_info "建议使用普通用户运行，但会继续安装"
fi

# 检测系统类型
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
    print_info "系统: $OS $VER"
else
    print_error "无法检测系统类型"
    exit 1
fi

# 检查网络连接
print_info "检查网络连接..."
if ping -c 1 google.com &> /dev/null || ping -c 1 baidu.com &> /dev/null; then
    print_success "网络连接正常"
else
    print_warning "网络连接可能有问题，但继续安装"
fi

###############################################################################
# 步骤 2: 安装系统依赖
###############################################################################

print_header "步骤 2/6: 安装系统依赖"

print_info "更新软件包列表..."
sudo apt update

print_info "检查并安装必要软件..."

# Python3
if ! command -v python3 &> /dev/null; then
    print_info "安装 Python3..."
    sudo apt install python3 -y
else
    print_success "Python3 已安装: $(python3 --version)"
fi

# pip3
if ! command -v pip3 &> /dev/null; then
    print_info "安装 pip3..."
    sudo apt install python3-pip -y
else
    print_success "pip3 已安装: $(pip3 --version)"
fi

# python3-venv
if ! dpkg -l | grep -q python3-venv; then
    print_info "安装 python3-venv..."
    sudo apt install python3-venv -y
else
    print_success "python3-venv 已安装"
fi

# git (可选)
if ! command -v git &> /dev/null; then
    print_info "安装 git..."
    sudo apt install git -y
else
    print_success "git 已安装: $(git --version)"
fi

###############################################################################
# 步骤 3: 创建工作目录
###############################################################################

print_header "步骤 3/6: 创建工作目录"

INSTALL_DIR="$HOME/telegram-auto-checkin"

if [ -d "$INSTALL_DIR" ]; then
    print_warning "目录已存在: $INSTALL_DIR"
    read -p "是否删除并重新安装? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        print_info "已删除旧目录"
    else
        print_error "安装已取消"
        exit 1
    fi
fi

# 注意：这里假设脚本是从项目目录运行的
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$SCRIPT_DIR" = "$INSTALL_DIR" ]; then
    print_info "已在目标目录中，跳过复制"
else
    print_info "创建目录: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    
    print_info "复制项目文件..."
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/" 2>/dev/null || true
    print_success "文件复制完成"
fi

cd "$INSTALL_DIR"

###############################################################################
# 步骤 4: 创建 Python 虚拟环境
###############################################################################

print_header "步骤 4/6: 创建 Python 虚拟环境"

if [ -d "venv" ]; then
    print_info "虚拟环境已存在，重新创建"
    rm -rf venv
fi

print_info "创建虚拟环境..."
python3 -m venv venv

print_info "激活虚拟环境..."
source venv/bin/activate

print_success "虚拟环境创建成功"

###############################################################################
# 步骤 5: 安装 Python 依赖
###############################################################################

print_header "步骤 5/6: 安装 Python 依赖"

print_info "升级 pip..."
pip install --upgrade pip -q

print_info "安装项目依赖 (这可能需要几分钟)..."
pip install -r requirements.txt -q

print_success "依赖安装完成"

###############################################################################
# 步骤 6: 配置应用
###############################################################################

print_header "步骤 6/6: 配置应用"

if [ -f ".env" ]; then
    print_warning ".env 文件已存在"
    read -p "是否保留现有配置? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "保留现有配置"
    else
        rm .env
        print_info "删除旧配置，将创建新配置"
    fi
fi

if [ ! -f ".env" ]; then
    # 创建基础配置文件
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

# 签到目标配置（多目标，JSON 格式）
CHECKIN_TARGETS=[]
EOF

    print_success "已创建 .env 文件"
    
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  📋 配置步骤 1/2：获取 Telegram API 凭证"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "请按以下步骤操作："
    echo ""
    echo "  1. 在浏览器中打开: https://my.telegram.org"
    echo "  2. 使用你的手机号登录 Telegram"
    echo "  3. 点击 'API development tools' (API 开发工具)"
    echo "  4. 填写应用信息（随意填写即可）"
    echo "  5. 获取 API_ID 和 API_HASH"
    echo ""
    read -p "按回车键继续..." 
    echo ""
    
    # 输入 API 凭证
    while true; do
        read -p "请输入 API_ID (纯数字，如 12345678): " api_id
        if [[ "$api_id" =~ ^[0-9]+$ ]]; then
            break
        else
            print_error "API_ID 必须是纯数字，请重新输入"
        fi
    done
    
    while true; do
        read -p "请输入 API_HASH (32位字符串): " api_hash
        if [ ${#api_hash} -eq 32 ]; then
            break
        else
            print_error "API_HASH 必须是32位字符串，请重新输入"
        fi
    done
    
    while true; do
        read -p "请输入手机号 (格式: +8613800138000): " phone_number
        if [[ "$phone_number" =~ ^\+[0-9]+$ ]]; then
            break
        else
            print_error "手机号格式错误，必须以 + 开头，如 +8613800138000"
        fi
    done
    
    # 写入配置
    sed -i "s/API_ID=.*/API_ID=$api_id/" .env
    sed -i "s/API_HASH=.*/API_HASH=$api_hash/" .env
    sed -i "s|PHONE_NUMBER=.*|PHONE_NUMBER=$phone_number|" .env
    
    print_success "API 凭证配置完成"
    
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  📋 配置步骤 2/2：配置签到目标"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "即将启动交互式配置向导"
    echo "你可以添加多个签到目标（群组或机器人）"
    echo "每个目标可以选择按钮点击或发送命令方式"
    echo ""
    read -p "按回车键继续..." 
    echo ""
    
    # 运行配置向导
    python setup_targets.py
    
    print_success "签到目标配置完成"
fi

# 测试配置
print_info "验证配置..."
python -c "import config; print('配置验证成功')" 2>/dev/null || {
    print_error "配置验证失败，请检查 .env 文件"
    exit 1
}
print_success "配置验证通过"

# 设置脚本执行权限
chmod +x run.sh stop.sh setup_service.sh 2>/dev/null || true

###############################################################################
# 安装完成
###############################################################################

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                  ✅ 安装完成！                              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
print_success "项目安装目录: $INSTALL_DIR"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  📚 下一步操作"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "1️⃣  首次登录验证 (必须)"
echo "   cd $INSTALL_DIR"
echo "   source venv/bin/activate"
echo "   python test_login.py"
echo ""
echo "2️⃣  测试手动签到"
echo "   python manual_checkin.py"
echo ""
echo "3️⃣  启动自动签到 (三选一)"
echo ""
echo "   方式 A: 使用 systemd 服务 (推荐，开机自启)"
echo "   sudo ./setup_service.sh"
echo "   sudo systemctl start telegram-auto-checkin"
echo "   sudo systemctl status telegram-auto-checkin"
echo ""
echo "   方式 B: 使用后台脚本"
echo "   ./run.sh"
echo ""
echo "   方式 C: 前台运行 (用于调试)"
echo "   python main.py"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  🔧 其他工具"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "• 添加新签到目标:    python add_target.py"
echo "• 查看所有群组:      python list_groups.py"
echo "• 测试群组消息:      python test_group.py"
echo "• 停止后台运行:      ./stop.sh"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  📖 查看文档"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "• 快速开始:    cat QUICKSTART.md"
echo "• 完整文档:    cat README.md"
echo "• 部署检查:    cat CHECKLIST.md"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
print_warning "重要提示："
echo "  请确保先运行 python test_login.py 完成首次登录验证！"
echo "  登录成功后才能正常使用自动签到功能。"
echo ""
