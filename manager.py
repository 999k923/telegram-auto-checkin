#!/usr/bin/env python3
"""
Telegram 自动签到 - 统一管理控制台
=====================================
整合所有功能于一体的交互式管理工具。

功能覆盖：
  1. 一键安装/部署（创建 venv、安装依赖、配置 API 凭证）
  2. 配置签到目标（添加 / 编辑 / 删除 / 查看）
  3. 登录验证测试
  4. 列出所有群组和机器人
  5. 查看机器人按钮（测试按钮点击）
  6. 测试群组签到
  7. 手动执行签到
  8. 启动 / 停止 / 重启 / 查看状态
  9. 查看日志
  10. 查看签到历史
  11. 编辑时间配置
  12. 备份 / 恢复配置
  13. 一键卸载
  14. 服务管理（systemd 安装 / 启动 / 停止）
"""

import os
import sys
import json
import shutil
import subprocess
import platform
import re
import time
import logging
import signal
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
VERSION = "2.0.0"
PROJECT_NAME = "Telegram 自动签到"

# 必需依赖
REQUIRED_PACKAGES = [
    "telethon>=1.34.0",
    "APScheduler>=3.10.4",
    "python-dotenv>=1.0.0",
    "pytz>=2023.3",
]

# 环境变量键
ENV_KEYS = {
    "api_id": "API_ID",
    "api_hash": "API_HASH",
    "phone": "PHONE_NUMBER",
    "hour": "CHECKIN_HOUR",
    "minute": "CHECKIN_MINUTE",
    "timezone": "TIMEZONE",
    "delay_min": "RANDOM_DELAY_MIN",
    "delay_max": "RANDOM_DELAY_MAX",
    "targets": "CHECKIN_TARGETS",
}

# 默认配置
DEFAULT_CONFIG = {
    "hour": "9",
    "minute": "0",
    "timezone": "Asia/Shanghai",
    "delay_min": "0",
    "delay_max": "300",
    "targets": [],
}

# 文件路径（相对于项目根目录）
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR / ".env"
SESSION_FILE = SCRIPT_DIR / "telegram_session.session"
VENV_DIR = SCRIPT_DIR / "venv"
LOG_FILE = SCRIPT_DIR / "auto_checkin.log"
HISTORY_FILE = SCRIPT_DIR / "checkin_history.log"
PID_FILE = SCRIPT_DIR / "bot.pid"

# systemctl 服务名
SERVICE_NAME = "telegram-auto-checkin"
SYSTEMD_PATH = Path("/etc/systemd/system/telegram-auto-checkin.service")

# ---------------------------------------------------------------------------
# 日志配置
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("manager")

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def venv_python():
    """返回虚拟环境 python 路径，若不存在则返回空字符串。"""
    if platform.system() == "Windows":
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python")


def run_cmd(cmd, check=False, shell=True, timeout=300):
    """运行子进程命令，返回 (success, output)。"""
    try:
        if isinstance(cmd, list):
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=SCRIPT_DIR, timeout=timeout)
        else:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=SCRIPT_DIR, timeout=timeout)
        output = (proc.stdout or "") + (proc.stderr or "")
        ok = proc.returncode == 0
        if check and not ok:
            logger.error(f"命令失败 (rc={proc.returncode}): {cmd}")
            if output:
                logger.error(output[-2000:])
        return ok, output.strip()
    except subprocess.TimeoutExpired:
        return False, "[TIMEOUT]"
    except FileNotFoundError:
        return False, "[Command not found]"


def wait(key="回车"):
    """等待用户按键。"""
    try:
        input(f"\n按 {key} 继续...")
    except (EOFError, KeyboardInterrupt):
        pass


def confirm(prompt="确认？", default=True):
    """确认对话框。default=True 时 y 是默认值。"""
    suffix = "[Y/n]" if default else "[y/N]"
    ans = input(f"{prompt} {suffix} ").strip().lower()
    if not ans:
        return default
    return ans in ("y", "yes")


def get_input(prompt, default="", validator=None, err_msg=None):
    """带默认值和验证器的输入。"""
    while True:
        val = input(prompt).strip()
        if not val and default:
            return default
        if validator and val:
            if validator(val):
                return val
            if err_msg:
                print(f"⚠️  {err_msg}")
            continue
        if val:
            return val
        if default == "":
            print("⚠️  此项不能为空")


# ---------------------------------------------------------------------------
# .env 文件管理
# ---------------------------------------------------------------------------

def load_env_to_lines():
    """读取 .env 返回 (lines_list, env_dict)。"""
    lines = []
    env = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            k, v = stripped.split("=", 1)
            # 去引号
            v = v.strip().strip("\"'")
            env[k.strip()] = v
    return lines, env


def save_env_from_lines(lines):
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)


def update_env_kv(lines, key, value):
    """在 lines 中更新/插入 key=value，返回更新后的 lines。"""
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            found = True
            break
    if not found:
        # 在 PHONE_NUMBER 后面插入
        insert_at = len(lines)
        for i, line in enumerate(lines):
            if line.strip().startswith("PHONE_NUMBER="):
                insert_at = i + 1
                break
        lines.insert(insert_at, f"{key}={value}\n")
    return lines


def get_targets():
    """从 .env 读取签到目标列表（新版 JSON 或旧版 BOT_USERNAME）。"""
    _, env = load_env_to_lines()
    targets = env.get("CHECKIN_TARGETS", "")
    if targets:
        try:
            return json.loads(targets)
        except json.JSONDecodeError:
            pass
    # 旧版兼容
    bot = env.get("BOT_USERNAME", "")
    if bot:
        return [{
            "name": bot,
            "target": bot,
            "command": env.get("CHECKIN_COMMAND", "/start"),
            "button_text": env.get("CHECKIN_BUTTON_TEXT", ""),
        }]
    return []


def set_targets(targets):
    """将目标列表写回 .env。"""
    lines, _ = load_env_to_lines()
    json_str = json.dumps(targets, ensure_ascii=False)
    lines = update_env_kv(lines, "CHECKIN_TARGETS", json_str)
    # 注释掉旧版单目标键
    for i, line in enumerate(lines):
        if line.startswith("BOT_USERNAME=") or line.startswith("CHECKIN_COMMAND=") or line.startswith("CHECKIN_BUTTON_TEXT="):
            if not line.startswith("#"):
                lines[i] = "# (已迁移到 CHECKIN_TARGETS) " + line
    save_env_from_lines(lines)
    return True


def get_env(key, default=""):
    """获取环境变量值。"""
    _, env = load_env_to_lines()
    return env.get(key, default)


def set_env(key, value):
    """设置环境变量值到 .env。"""
    lines, _ = load_env_to_lines()
    lines = update_env_kv(lines, key, value)
    save_env_from_lines(lines)
    return True


def ensure_env_exists():
    """确保 .env 文件存在（从 .env.example 复制）。"""
    if ENV_FILE.exists():
        return True
    example = SCRIPT_DIR / ".env.example"
    if example.exists():
        shutil.copy2(example, ENV_FILE)
        return True
    # 直接创建
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("# Telegram API 配置\n")
        f.write("API_ID=\n")
        f.write("API_HASH=\n")
        f.write("PHONE_NUMBER=\n\n")
        f.write("# 签到时间配置\n")
        f.write(f"CHECKIN_HOUR={DEFAULT_CONFIG['hour']}\n")
        f.write(f"CHECKIN_MINUTE={DEFAULT_CONFIG['minute']}\n\n")
        f.write(f"TIMEZONE={DEFAULT_CONFIG['timezone']}\n\n")
        f.write("RANDOM_DELAY_MIN=0\n")
        f.write("RANDOM_DELAY_MAX=300\n\n")
        f.write("CHECKIN_TARGETS=[]\n")
    return True


# ---------------------------------------------------------------------------
# 菜单系统
# ---------------------------------------------------------------------------

def banner():
    """打印欢迎横幅。"""
    print("")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       Telegram 自动签到 - 统一管理控制台                    ║")
    print(f"║       版本: {VERSION:<40}║")
    print("║       项目目录: " + str(SCRIPT_DIR)[-40:] + "   ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("")


def main_menu():
    """主菜单。"""
    print("┌──────────────────────────────────────────────────────────┐")
    print("│  主菜单                                                   │")
    print("├──────────────────────────────────────────────────────────┤")
    print("│  [1] 一键安装 / 部署                                       │")
    print("│  [2] 配置签到目标                                          │")
    print("│  [3] 登录验证测试                                          │")
    print("│  [4] 列出所有群组和机器人                                  │")
    print("│  [5] 查看机器人按钮（测试按钮点击）                         │")
    print("│  [6] 测试群组签到                                          │")
    print("│  [7] 手动执行签到                                          │")
    print("│  [8] 服务管理（启动 / 停止 / 重启 / 状态）                  │")
    print("│  [9] 查看日志                                              │")
    print("│  [10] 查看签到历史                                         │")
    print("│  [11] 编辑签到时间配置                                      │")
    print("│  [12] 备份配置                                             │")
    print("│  [13] 恢复配置                                             │")
    print("│  [14] 一键卸载                                             │")
    print("│  [15] 自动获取验证码（get_code）                            │")
    print("│  [0] 退出                                                  │")
    print("└──────────────────────────────────────────────────────────┘")
    choice = input("请选择功能 [0-15]: ").strip()
    return choice


# ---------------------------------------------------------------------------
# 功能实现
# ---------------------------------------------------------------------------

# ---------- 1. 一键安装 / 部署 ----------

def cmd_install():
    """一键安装/部署：系统依赖 -> venv -> python 依赖 -> API 凭证 -> 配置目标。"""
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║  1. 一键安装 / 部署                                      ║")
    print("╚════════════════════════════════════════════════════════╝")
    print("\n此操作将完成：")
    print("  ① 检查并安装 Python 及系统依赖")
    print("  ② 创建 Python 虚拟环境")
    print("  ③ 安装 Python 项目依赖")
    print("  ④ 配置 Telegram API 凭证")
    print("  ⑤ 配置签到目标")
    print("")
    if not confirm("确认开始安装"):
        return

    # ① 检查 Python
    print("\n--- 步骤 1: 检查 Python 环境 ---")
    ok, out = run_cmd("python3 --version")
    if not ok:
        print("⚠️  未找到 python3，正在安装...")
        ok, _ = run_cmd("sudo apt update", check=False)
        ok, _ = run_cmd("sudo apt install -y python3 python3-pip python3-venv", check=False)
        if not ok:
            print("❌ Python 安装失败，请手动安装后重试")
            return
    else:
        print(f"✅ Python: {out}")

    # ② 创建 venv
    print("\n--- 步骤 2: 创建虚拟环境 ---")
    if VENV_DIR.exists():
        print("⚠️  虚拟环境已存在，删除后重建...")
        shutil.rmtree(VENV_DIR)
    ok, _ = run_cmd("python3 -m venv venv")
    if not ok:
        print("❌ 虚拟环境创建失败")
        return
    print("✅ 虚拟环境创建成功")

    # ③ 安装依赖
    print("\n--- 步骤 3: 安装 Python 依赖 ---")
    if not (SCRIPT_DIR / "requirements.txt").exists():
        with open(SCRIPT_DIR / "requirements.txt", "w", encoding="utf-8") as f:
            f.write("telethon>=1.34.0\n")
            f.write("APScheduler>=3.10.4\n")
            f.write("python-dotenv>=1.0.0\n")
            f.write("pytz>=2023.3\n")
    ok, _ = run_cmd(f"{venv_python()} -m pip install --upgrade pip")
    if not ok:
        print("⚠️  pip 升级失败，继续...")
    ok, _ = run_cmd(f"{venv_python()} -m pip install -r requirements.txt")
    if not ok:
        print("❌ 依赖安装失败")
        return
    print("✅ Python 依赖安装完成")

    # ④ 配置 API 凭证
    print("\n--- 步骤 4: 配置 Telegram API 凭证 ---")
    ensure_env_exists()
    session_file = SCRIPT_DIR / "telegram_session.session"
    current_api_id = get_env("API_ID")
    current_hash = get_env("API_HASH")
    current_phone = get_env("PHONE_NUMBER")

    # 检测已有 Session 文件
    if session_file.exists():
        print(f"  检测到已有登录会话文件: {session_file}")
        print("  💡 如果 .env 中没有 API 凭证，请先运行 [3] 登录验证测试获取验证码")
        print("     或直接编辑 .env 文件填入 API_ID / API_HASH / PHONE_NUMBER")
        wait()

    if current_api_id and current_hash and current_phone:
        print(f"  API_ID: {current_api_id}")
        print(f"  API_HASH: {current_hash[:4]}...{current_hash[-4:]}")
        print(f"  PHONE_NUMBER: {current_phone}")
        if not confirm("已有配置，是否重新配置？", default=False):
            print("保留现有配置。")
        else:
            _config_api_credentials()
    elif session_file.exists():
        print("  ⚠️  .env 中没有 API 凭证，但检测到 Session 文件")
        print("  请手动编辑 .env 文件，填入以下字段：")
        print("    API_ID=<你的 API_ID>")
        print("    API_HASH=<你的 API_HASH>")
        print("    PHONE_NUMBER=+86138xxxx138000")
        print("  编辑完成后按回车继续，或选择 [2] 重新配置")
        if confirm("是否现在手动编辑 .env？", default=False):
            return
    else:
        _config_api_credentials()

    # ⑤ 配置签到目标
    print("\n--- 步骤 5: 配置签到目标 ---")
    existing_targets = get_targets()
    if existing_targets:
        print(f"  检测到已有 {len(existing_targets)} 个签到目标：")
        for i, t in enumerate(existing_targets):
            method = f"按钮点击 [{t.get('button_text','')}]" if t.get("button_text") else "文本命令"
            print(f"    [{i+1}] {t['name']}  |  {t['command']}  |  {method}")
        print("\n  [1] 跳过（保留现有配置，直接进入下一步）")
        print("  [2] 添加更多目标")
        print("  [3] 重新配置所有目标（清空后从头添加）")
        choice = input("  请选择 [1/2/3] (默认 1): ").strip()
        if choice == "2":
            print("即将启动交互式配置向导，可添加更多签到目标。")
            wait()
            _interactive_add_targets(reset=False)
        elif choice == "3":
            if confirm("确认清空所有目标并从头配置？"):
                set_targets([])
                print("即将启动交互式配置向导。")
                wait()
                _interactive_add_targets(reset=True)
            else:
                print("已取消，保留现有配置。")
        else:
            print("保留现有配置，跳过此步骤。")
    else:
        print("  当前没有配置签到目标。")
        print("\n  [1] 先列出所有群组和机器人，再配置目标")
        print("  [2] 直接跳过，稍后通过 [2] 菜单配置")
        choice = input("  请选择 [1/2] (默认 1): ").strip()
        if choice == "2":
            print("跳过签到目标配置，后续可在主菜单 [2] 中手动添加。")
            # 验证环节需要目标，跳过验证
            pass
        else:
            # 列出群组和机器人（需要 venv 已就绪）
            py = venv_python()
            if py and Path(py).exists():
                print("\n正在列出所有群组和机器人，请稍候...")
                ok, out = run_cmd(f"{py} list_groups.py", check=False, timeout=120)
                if ok and out:
                    print(out)
                    print("\n根据上面列出的信息，现在配置签到目标。")
                else:
                    print("⚠️  列出群组失败，请检查网络连接或 Telegram 登录状态。")
                    print("  可先运行 [3] 登录验证测试，再继续。")
            else:
                print("⚠️  虚拟环境未创建，无法列出群组。")
                print("  请确保步骤 1-3 已完成。")
            wait()
            _interactive_add_targets(reset=False)

    # 验证
    print("\n--- 验证配置 ---")
    ok, out = run_cmd(f'{venv_python()} -c "import config; print(\'✅ 配置加载成功\')"')
    if ok:
        print(out)
    else:
        print("⚠️  配置验证失败，请检查 .env 文件")

    print("\n╔════════════════════════════════════════════════════════╗")
    print("║  ✅ 安装完成！                                          ║")
    print("╚════════════════════════════════════════════════════════╝")
    # ⑥ 自动安装 systemd 服务并启动
    print("\n--- 步骤 6: 安装 systemd 系统服务 ---")
    _install_systemd_service()
    ok, _ = run_cmd(f"sudo systemctl start {SERVICE_NAME} 2>/dev/null")
    ok, status_out = run_cmd(f"sudo systemctl is-active {SERVICE_NAME} 2>/dev/null")
    if status_out.strip() == "active":
        print("✅ systemd 服务已启动")
    else:
        print("⚠️  systemd 服务启动失败，可手动运行 sudo systemctl start telegram-auto-checkin")

    print("\n╔════════════════════════════════════════════════════════╗")
    print("║  ✅ 安装完成！                                          ║")
    print("╚════════════════════════════════════════════════════════╝")
    print("\n下一步建议：")
    print("  [3] 登录验证测试  (首次必须完成)")
    print("  [8] 服务管理      (查看/重启/停止)")
    wait()


def _config_api_credentials():
    """交互式配置 API 凭证。"""
    print("\n  请按以下步骤获取 API 凭证：")
    print("  1. 打开 https://my.telegram.org")
    print("  2. 使用手机号登录")
    print("  3. 点击 'API development tools'")
    print("  4. 创建应用并获取 API_ID 和 API_HASH")
    print("")
    wait()

    def valid_api_id(v):
        return v.isdigit()

    def valid_api_hash(v):
        return len(v) == 32

    def valid_phone(v):
        return v.startswith("+") and v[1:].isdigit()

    api_id = get_input("  请输入 API_ID (纯数字): ", validator=valid_api_id, err_msg="API_ID 必须是纯数字")
    api_hash = get_input("  请输入 API_HASH (32位字符串): ", validator=valid_api_hash, err_msg="API_HASH 必须是32位字符串")
    phone = get_input("  请输入手机号 (格式 +8613800138000): ", validator=valid_phone, err_msg="必须以+开头，后面纯数字")

    set_env("API_ID", api_id)
    set_env("API_HASH", api_hash)
    set_env("PHONE_NUMBER", phone)
    print("✅ API 凭证配置完成")


# ---------- 2. 配置签到目标 ----------

def cmd_configure_targets():
    """签到目标配置菜单。"""
    while True:
        targets = get_targets()
        print("\n╔════════════════════════════════════════════════════════╗")
        print("║  2. 配置签到目标                                        ║")
        print("╚════════════════════════════════════════════════════════╝")
        print("┌──────────────────────────────────────────────────────┐")
        print("│  [1] 查看当前目标列表                                  │")
        print("│  [2] 添加新签到目标                                    │")
        print("│  [3] 编辑指定目标                                      │")
        print("│  [4] 删除指定目标                                      │")
        print("│  [5] 重新配置所有目标（清空后从头添加）                 │")
        print("│  [6] 使用 list_groups 查找群组名称                     │")
        print("│  [0] 返回主菜单                                        │")
        print("└──────────────────────────────────────────────────────┘")

        if targets:
            print(f"\n  当前共 {len(targets)} 个目标：")
            for i, t in enumerate(targets):
                method = f"按钮点击 [{t.get('button_text','')}]" if t.get("button_text") else "文本命令"
                print(f"    [{i+1}] {t['name']}  |  目标: {t['target']}  |  命令: {t['command']}  |  {method}")
            print()

        choice = input("请选择: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            if targets:
                for i, t in enumerate(targets):
                    print(f"  [{i+1}] {json.dumps(t, ensure_ascii=False)}")
            else:
                print("  当前没有配置任何签到目标。")
        elif choice == "2":
            new_t = _add_single_target()
            if new_t:
                targets.append(new_t)
                set_targets(targets)
                print(f"✅ 已添加目标: {new_t['name']}")
        elif choice == "3":
            if not targets:
                print("⚠️  没有可编辑的目标")
                continue
            idx = get_target_index(targets, "编辑")
            if idx is not None:
                old = targets[idx]
                print(f"  编辑目标: {old['name']}")
                targets[idx] = _build_target_interactive(default=old) or old
                set_targets(targets)
                print(f"✅ 目标 [{idx+1}] 已更新")
        elif choice == "4":
            if not targets:
                print("⚠️  没有可删除的目标")
                continue
            idx = get_target_index(targets, "删除")
            if idx is not None:
                removed = targets.pop(idx)
                if targets:
                    set_targets(targets)
                    print(f"✅ 已删除目标: {removed['name']}")
                else:
                    set_targets([])
                    print("✅ 所有目标已清空")
        elif choice == "5":
            if confirm("确认清空所有目标并从头配置？"):
                set_targets([])
                _interactive_add_targets(reset=True)
            else:
                print("已取消")
        elif choice == "6":
            print("\n正在列出所有群组和机器人...")
            py = venv_python()
            if not py or not Path(py).exists():
                print("❌ 虚拟环境未创建，请先运行 [1] 一键安装")
            else:
                ok, out = run_cmd(f"{py} list_groups.py", check=False, timeout=120)
                if out:
                    print(out[-3000:])
        else:
            print("⚠️  无效选择")


def get_target_index(targets, action="操作"):
    """交互式选择目标索引，返回索引或 None（取消）。"""
    print(f"\n  选择要{action}的目标编号：")
    for i, t in enumerate(targets):
        print(f"    [{i+1}] {t['name']}  ({t['target']})")
    while True:
        try:
            idx = int(input(f"  输入编号 (0 取消): ").strip()) - 1
            if idx == -1:
                return None
            if 0 <= idx < len(targets):
                return idx
            print("⚠️  编号超出范围")
        except ValueError:
            print("⚠️  请输入有效数字")


def _add_single_target():
    """添加单个签到目标的交互式引导。"""
    print("\n" + "=" * 60)
    print("添加新的签到目标")
    print("=" * 60)

    name = get_input("\n1️⃣  显示名称 (如: @okemby_bot 或 Cloud Cat Group): ", err_msg="名称不能为空")
    if not name:
        return None

    print("\n2️⃣  目标标识:")
    print("   • 机器人: 使用 @username 格式 (如: @okemby_bot)")
    print("   • 群组:   使用完整群组名称 (如: Cloud Cat Group)")
    print("   • 或使用 ID (如: -1001234567890)")
    print("   💡 提示: 在主菜单选择 [4] 可列出所有群组/机器人")
    target = get_input("   输入目标标识: ", err_msg="目标不能为空")
    if not target:
        return None

    print("\n3️⃣  签到命令:")
    print("   常用命令: /start, /checkin, /signin, /daily")
    command = get_input("   输入命令 (默认: /start): ", default="/start")

    print("\n4️⃣  签到方式:")
    print("   [1] 按钮点击 - 发送命令后自动点击按钮")
    print("   [2] 文本命令 - 直接发送命令即可")
    method = get_input("   选择方式 (1/2, 默认: 1): ", default="1")

    button_text = ""
    if method != "2":
        print("\n5️⃣  按钮文字:")
        print("   常见按钮: 签到, 打卡, Check in, 每日签到")
        print("   💡 提示: 在主菜单选择 [5] 可查看机器人的所有按钮")
        button_text = input("   输入按钮文字 (留空则使用文本命令): ").strip()

    cfg = {"name": name, "target": target, "command": command, "button_text": button_text}

    print("\n" + "-" * 60)
    print("配置预览:")
    print(f"  名称:   {cfg['name']}")
    print(f"  目标:   {cfg['target']}")
    print(f"  命令:   {cfg['command']}")
    print(f"  方式:   {'按钮点击 - ' + cfg['button_text'] if cfg['button_text'] else '文本命令'}")
    print("-" * 60)

    if not confirm("确认添加此目标？"):
        return None
    return cfg


def _build_target_interactive(default=None):
    """使用已有默认值重建目标配置。"""
    d = default or {}
    print("\n编辑签到目标 (直接回车保持原值):")
    name = get_input("  名称: ", default=d.get("name", ""))
    if not name:
        return None
    target = get_input("  目标标识: ", default=d.get("target", ""))
    if not target:
        return None
    command = get_input("  签到命令: ", default=d.get("command", "/start") or "/start")
    print("  签到方式: [1] 按钮点击  [2] 文本命令")
    method = get_input("  选择方式 (1/2): ", default="1" if d.get("button_text") else "2")
    button_text = ""
    if method != "2":
        button_text = get_input("  按钮文字: ", default=d.get("button_text", ""))
    return {"name": name, "target": target, "command": command, "button_text": button_text}


def _interactive_add_targets(reset=False):
    """连续添加多个目标的交互式循环。"""
    if reset:
        targets = []
    else:
        targets = get_targets()

    print(f"\n当前已有 {len(targets)} 个目标。开始添加新目标...")

    while True:
        new_t = _add_single_target()
        if new_t:
            targets.append(new_t)
            print(f"✅ 第 {len(targets)} 个目标已添加: {new_t['name']}")
        else:
            print("⚠️  未添加目标")

        if not confirm("是否继续添加下一个目标？", default=len(targets) < 3):
            break

    if targets:
        print("\n" + "=" * 60)
        print("📋 配置汇总")
        print("=" * 60)
        for i, t in enumerate(targets):
            print(f"  [{i+1}] {t['name']}  |  {t['command']}  |  {'按钮' if t.get('button_text') else '命令'}")
        if confirm("确认保存配置？"):
            set_targets(targets)
            print("✅ 配置已保存")
        else:
            print("已取消，未保存")
    else:
        print("❌ 未配置任何签到目标")


# ---------- 3. 登录验证测试 ----------

def cmd_test_login():
    """调用 telegram_client.py 进行登录测试。"""
    print("\n正在执行 Telegram 登录验证测试...")
    print("首次登录需要输入 Telegram 发送的验证码，可能有两步验证密码。\n")
    py = venv_python()
    if not py or not Path(py).exists():
        print("❌ 虚拟环境未创建，请先运行 [1] 一键安装")
        return
    ok, out = run_cmd(f"{py} test_login.py", check=False, timeout=600)
    if out:
        print(out[-3000:])
    print("\n完成。")


# ---------- 4. 列出所有群组和机器人 ----------

def cmd_list_groups():
    """列出所有群组和机器人。"""
    print("\n正在列出所有群组和机器人...")
    py = venv_python()
    if not py or not Path(py).exists():
        print("❌ 虚拟环境未创建，请先运行 [1] 一键安装")
        return
    ok, out = run_cmd(f"{py} list_groups.py", check=False, timeout=120)
    if out:
        print(out)


# ---------- 5. 查看机器人按钮 ----------

def cmd_test_buttons():
    """查看机器人按钮并测试点击。"""
    print("\n正在查看机器人按钮...")
    py = venv_python()
    if not py or not Path(py).exists():
        print("❌ 虚拟环境未创建，请先运行 [1] 一键安装")
        return
    ok, out = run_cmd(f"{py} test_buttons.py", check=False, timeout=180)
    if out:
        print(out[-3000:])


# ---------- 6. 测试群组签到 ----------

def cmd_test_group():
    """测试群组签到。"""
    print("\n正在测试群组签到...")
    py = venv_python()
    if not py or not Path(py).exists():
        print("❌ 虚拟环境未创建，请先运行 [1] 一键安装")
        return
    ok, out = run_cmd(f"{py} test_group.py", check=False, timeout=180)
    if out:
        print(out[-3000:])


# ---------- 7. 手动执行签到 ----------

def cmd_manual_checkin():
    """手动触发一次签到。"""
    print("\n正在手动执行签到...")
    py = venv_python()
    if not py or not Path(py).exists():
        print("❌ 虚拟环境未创建，请先运行 [1] 一键安装")
        return
    targets = get_targets()
    if not targets:
        print("⚠️  当前没有配置签到目标，请先配置目标后再测试。")
        return
    ok, out = run_cmd(f"{py} manual_checkin.py", check=False, timeout=120)
    if out:
        print(out[-3000:])


# ---------- 8. 服务管理 ----------

def cmd_service_manage():
    """服务管理：启动 / 停止 / 重启 / 查看状态 / 前台运行。"""
    while True:
        py = venv_python()
        targets = get_targets()
        print("\n╔════════════════════════════════════════════════════════╗")
        print("║  8. 服务管理                                            ║")
        print("╚════════════════════════════════════════════════════════╝")
        print("┌──────────────────────────────────────────────────────┐")
        print("│  [1] 启动签到程序（前台运行，Ctrl+C 停止）             │")
        print("│  [2] 启动签到程序（后台运行，PID 文件管理）            │")
        print("│  [3] 停止后台运行的签到程序                            │")
        print("│  [4] 查看签到程序运行状态                              │")
        print("│  [5] 重启后台签到程序                                  │")
        print("│  [0] 返回主菜单                                        │")
        print("└──────────────────────────────────────────────────────┘")

        choice = input("请选择: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            if not targets:
                print("⚠️  没有配置签到目标，无法启动")
                continue
            if not py or not Path(py).exists():
                print("❌ 虚拟环境不存在，请先运行 [1] 一键安装")
                continue
            print("\n前台启动签到程序 (Ctrl+C 停止):")
            print("=" * 60)
            run_cmd(f"{py} main.py", check=False, timeout=None)
            print("程序已退出。")
        elif choice == "2":
            _start_background()
        elif choice == "3":
            _stop_background()
        elif choice == "4":
            _check_status()
        elif choice == "5":
            _stop_background()
            _start_background()
        else:
            print("⚠️  无效选择")


def _start_background():
    """后台启动签到程序（PID 文件管理）。"""
    py = venv_python()
    if not py or not Path(py).exists():
        print("❌ 虚拟环境不存在")
        return
    targets = get_targets()
    if not targets:
        print("⚠️  没有配置签到目标")
        return

    if PID_FILE.exists():
        try:
            old_pid = int(PID_FILE.read_text().strip())
            if _is_process_alive(old_pid):
                print(f"⚠️  程序已在运行 (PID: {old_pid})")
                if not confirm("是否先停止再启动？"):
                    return
                os.kill(old_pid, signal.SIGTERM)
                time.sleep(2)
        except (ValueError, OSError):
            pass
        PID_FILE.unlink(missing_ok=True)

    # 创建日志文件
    log_path = str(LOG_FILE)
    # 后台启动
    print(f"后台启动签到程序...")
    if platform.system() == "Windows":
        # Windows 用 subprocess.Popen
        import subprocess as sp
        proc = sp.Popen(
            [py, "main.py"],
            stdout=open(log_path, "a"),
            stderr=subprocess.STDOUT,
            cwd=SCRIPT_DIR,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0,
        )
        PID_FILE.write_text(str(proc.pid))
        print(f"✅ 已启动 (PID: {proc.pid})")
    else:
        # Linux/macOS 用 nohup
        ok, _ = run_cmd(f"nohup {py} main.py >> {log_path} 2>&1 & echo $!")
        if ok:
            try:
                pid = int(_.strip())
                PID_FILE.write_text(str(pid))
                print(f"✅ 已后台启动 (PID: {pid})")
            except ValueError:
                print("⚠️  无法获取 PID，请手动检查")
        else:
            print("❌ 启动失败")


def _stop_background():
    """停止后台运行的签到程序。"""
    if not PID_FILE.exists():
        print("⚠️  PID 文件不存在，程序可能未在运行")
        # 尝试通过进程名查找
        try:
            import subprocess as sp
            result = sp.run(["pgrep", "-f", "main.py"], capture_output=True, text=True, cwd=SCRIPT_DIR)
            if result.stdout.strip():
                pids = result.stdout.strip().split("\n")
                print(f"  发现相关进程: {pids}")
                if confirm("是否终止这些进程？"):
                    for p in pids:
                        os.kill(int(p.strip()), signal.SIGTERM)
                    print("✅ 已终止")
            else:
                print("  未发现相关进程")
        except Exception:
            pass
        return

    try:
        pid = int(PID_FILE.read_text().strip())
        if _is_process_alive(pid):
            os.kill(pid, signal.SIGTERM)
            PID_FILE.unlink()
            print(f"✅ 已停止 (PID: {pid})")
        else:
            PID_FILE.unlink()
            print("✅ PID 文件已清理（进程已不存在）")
    except (ValueError, OSError) as e:
        print(f"⚠️  清理失败: {e}")


def _check_status():
    """检查签到程序状态。"""
    py = venv_python()
    print("\n检查签到程序运行状态...")
    if not py or not Path(py).exists():
        print("  ❌ 虚拟环境不存在")
        return

    # PID 文件 / systemd / pgrep 三处互查，综合给出状态
    running = False
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if _is_process_alive(pid):
                print(f"  ✅ 后台程序正在运行 (PID: {pid})")
                running = True
            else:
                print(f"  ⚠️  PID 文件已失效 (PID: {pid} 已停止)")
        except (ValueError, OSError):
            print("  ⚠️  PID 文件内容异常")

    # systemd 状态
    ok, out = run_cmd(f"systemctl is-active {SERVICE_NAME} 2>/dev/null || echo not-installed")
    if ok and out.strip() == "active":
        print(f"  ✅ systemd 服务正在运行")
        running = True
    elif ok:
        print(f"  ℹ️  systemd 服务状态: {out.strip()}")

    # 通过 pgrep 补充发现（适用于 systemd 或前台启动但无 PID 文件的场景）
    try:
        import subprocess as sp
        result = sp.run(["pgrep", "-f", "main.py"], capture_output=True, text=True, cwd=SCRIPT_DIR)
        if result.stdout.strip() and not running:
            pids = result.stdout.strip().split()
            running = True
            print(f"  ℹ️  PID 文件不存在，但通过进程列表发现 main.py 正在运行: {pids}")
        elif result.stdout.strip():
            pids = result.stdout.strip().split()
            print(f"  ℹ️  发现相关 main.py 进程: {pids}")
    except Exception:
        pass

    if not running and not PID_FILE.exists():
        print("  ℹ️  程序未在后台运行（可通过 [8]->[2] 启动）")

    # 配置文件状态
    _, env = load_env_to_lines()
    api_ok = bool(env.get("API_ID") and env.get("API_HASH") and env.get("PHONE_NUMBER"))
    targets = get_targets()
    print(f"\n  配置状态:")
    print(f"    API 凭证: {'✅' if api_ok else '❌ 未配置'}")
    print(f"    签到目标: {'✅' if targets else '❌ 未配置'} ({len(targets)} 个)")
    print(f"    Session 文件: {'✅' if SESSION_FILE.exists() else '⚠️  未登录'}")
    hour = env.get("CHECKIN_HOUR", "?")
    minute = env.get("CHECKIN_MINUTE", "?")
    tz = env.get("TIMEZONE", "?")
    print(f"    签到时间: {hour}:{minute} ({tz})")
    print(f"    日志文件: {'✅' if LOG_FILE.exists() else '❌ 无'}")
    print(f"    历史记录: {'✅' if HISTORY_FILE.exists() else '❌ 无'}")


def _is_process_alive(pid):
    """检查进程是否存活。"""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


# ---------- 9. 安装 systemd 服务 ----------

def _install_systemd_service():
    """安装 systemd 系统服务（开机自启，无交互式提示）。"""

    py_path = venv_python()
    if not py_path or not Path(py_path).exists():
        print("⚠️  虚拟环境不存在，跳过 systemd 服务安装")
        return
    # 如果项目目录在 /root 下，强制使用 root 用户（避免权限问题）
    if str(SCRIPT_DIR).startswith("/root/"):
        current_user = "root"
    else:
        current_user = os.environ.get("SUDO_USER", os.environ.get("USER", "root"))

    service_content = f"""[Unit]
Description={PROJECT_NAME} - Telegram Auto Check-in
After=network.target

[Service]
Type=simple
User={current_user}
WorkingDirectory={SCRIPT_DIR}
Environment="PATH={VENV_DIR}/bin:{os.environ.get('PATH','')}"
Environment="PYTHONUNBUFFERED=1"
ExecStart={py_path} {SCRIPT_DIR}/main.py
Restart=always
RestartSec=10
StandardOutput=append:{LOG_FILE}
StandardError=append:{LOG_FILE}

[Install]
WantedBy=multi-user.target
"""
    print("\n正在创建服务文件...")
    try:
        # 需要 sudo
        ok, out = run_cmd(
            f'sudo bash -c \'echo "{service_content}" > {SYSTEMD_PATH}\''
        )
        if not ok:
            print("⚠️  自动写入失败，尝试手动模式...")
            print(f"\n请将以下内容写入: {SYSTEMD_PATH}")
            print("-" * 60)
            print(service_content)
            print("-" * 60)
            wait()
            ok, out = run_cmd("sudo systemctl daemon-reload")
            if not ok:
                print("❌ 无法执行 systemctl daemon-reload")
                return
        else:
            print("✅ 服务文件创建成功")

        ok, out = run_cmd("sudo systemctl daemon-reload")
        if ok:
            print("✅ systemd 配置已重载")
        else:
            print("⚠️  daemon-reload 失败")
        ok, out = run_cmd("sudo systemctl enable " + SERVICE_NAME)
        if ok:
            print("✅ systemd 服务已启用（开机自启）")
        else:
            print("⚠️  systemd 服务启用失败")
        return
    except Exception as e:
        print(f"⚠️  systemd 服务安装异常: {e}")
        return


# ---------- 9. 查看日志 ----------

def cmd_view_log():
    """查看 auto_checkin.log。"""
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║  9. 查看日志                                           ║")
    print("╚════════════════════════════════════════════════════════╝")
    print("┌──────────────────────────────────────────────────────┐")
    print("│  [1] 查看自动签到日志 (auto_checkin.log)              │")
    print("│  [2] 查看签到历史记录 (checkin_history.log)           │")
    print("│  [3] 实时跟踪日志 (tail -f)                           │")
    print("│  [4] 查看系统服务日志 (journalctl)                    │")
    print("│  [0] 返回主菜单                                        │")
    print("└──────────────────────────────────────────────────────┘")

    choice = input("请选择: ").strip()
    if choice == "0":
        return
    elif choice == "1":
        _view_file(LOG_FILE, "auto_checkin.log")
    elif choice == "2":
        _view_file(HISTORY_FILE, "checkin_history.log")
    elif choice == "3":
        if not LOG_FILE.exists():
            print("⚠️  日志文件不存在")
            return
        print(f"\n实时跟踪 {LOG_FILE.name} (Ctrl+C 退出):")
        try:
            run_cmd(f"tail -f {LOG_FILE}", check=False, timeout=None)
        except KeyboardInterrupt:
            print("\n已退出跟踪。")
    elif choice == "4":
        ok, out = run_cmd(f"sudo journalctl -u {SERVICE_NAME} --no-pager -n 50", check=False, timeout=30)
        if ok:
            print(out)
        else:
            print("⚠️  无法获取系统日志（可能服务未安装或无 sudo 权限）")
    else:
        print("⚠️  无效选择")


def _view_file(path, label):
    """查看文件内容（尾随 50 行）。"""
    if not path.exists():
        print(f"⚠️  文件不存在: {path}")
        return
    ok, out = run_cmd(f"tail -50 {path}")
    if ok:
        print(f"\n--- {label} (最近 50 行) ---")
        print(out)
    else:
        print(f"⚠️  无法读取 {path}")


# ---------- 10. 查看签到历史 ----------

def cmd_view_history():
    """查看签到历史记录。"""
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║  10. 查看签到历史                                       ║")
    print("╚════════════════════════════════════════════════════════╝")
    _view_file(HISTORY_FILE, "checkin_history.log")


# ---------- 11. 编辑签到时间配置 ----------

def cmd_edit_time_config():
    """编辑签到时间、时区、随机延迟。"""
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║  11. 编辑签到时间配置                                   ║")
    print("╚════════════════════════════════════════════════════════╝")

    _, env = load_env_to_lines()
    print("\n当前配置:")
    print(f"  签到时间: {env.get('CHECKIN_HOUR', '?')}:{env.get('CHECKIN_MINUTE', '?')}")
    print(f"  时区:     {env.get('TIMEZONE', '?')}")
    print(f"  随机延迟: {env.get('RANDOM_DELAY_MIN', '?')} - {env.get('RANDOM_DELAY_MAX', '?')} 秒")
    print()

    # 修改时间
    if confirm("是否修改签到时间？"):
        h = get_input("  输入小时 (0-23): ", default=env.get("CHECKIN_HOUR", "9"))
        m = get_input("  输入分钟 (0-59): ", default=env.get("CHECKIN_MINUTE", "0"))
        set_env("CHECKIN_HOUR", h)
        set_env("CHECKIN_MINUTE", m)
        print(f"✅ 签到时间已设为 {h}:{m}")

    # 修改时区
    if confirm("是否修改时区？", default=False):
        print("  常见时区:")
        print("    Asia/Shanghai   中国")
        print("    Asia/Tokyo      日本")
        print("    UTC             协调世界时")
        print("    Europe/London   伦敦")
        tz = get_input("  输入时区 (默认: Asia/Shanghai): ", default="Asia/Shanghai")
        set_env("TIMEZONE", tz)
        print(f"✅ 时区已设为 {tz}")

    # 随机延迟
    if confirm("是否修改随机延迟？", default=False):
        dmin = get_input("  最小延迟 (秒): ", default=env.get("RANDOM_DELAY_MIN", "0"))
        dmax = get_input("  最大延迟 (秒): ", default=env.get("RANDOM_DELAY_MAX", "300"))
        set_env("RANDOM_DELAY_MIN", dmin)
        set_env("RANDOM_DELAY_MAX", dmax)
        print(f"✅ 随机延迟已设为 {dmin} - {dmax} 秒")

    # 提示重启服务
    print("\n提示: 修改配置后需要重启签到程序使配置生效。")
    print("  [8] -> [5] 重启后台签到程序")
    print("  或 sudo systemctl restart " + SERVICE_NAME)


# ---------- 13. 备份配置 ----------

def cmd_backup():
    """备份 .env 和 session 文件。"""
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║  12. 备份配置                                           ║")
    print("╚════════════════════════════════════════════════════════╝")

    if not ENV_FILE.exists() and not SESSION_FILE.exists():
        print("⚠️  没有可备份的配置文件")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = SCRIPT_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / f"backup_{timestamp}"
    backup_path.mkdir()

    items = []
    if ENV_FILE.exists():
        shutil.copy2(ENV_FILE, backup_path / ".env")
        items.append(".env")
    if SESSION_FILE.exists():
        shutil.copy2(SESSION_FILE, backup_path / "telegram_session.session")
        items.append("session")

    print(f"✅ 已备份到: {backup_path}")
    for item in items:
        print(f"    - {item}")

    # 列出所有备份
    print("\n  所有备份:")
    for d in sorted(backup_dir.iterdir()):
        if d.is_dir():
            print(f"    - {d.name}")

    if confirm("是否清理旧备份（只保留最近 5 个）？", default=False):
        backups = sorted(backup_dir.iterdir())
        if len(backups) > 5:
            for old in backups[:-5]:
                shutil.rmtree(old)
                print(f"  已删除: {old.name}")
            print("✅ 旧备份已清理")


# ---------- 14. 恢复配置 ----------

def cmd_restore():
    """从备份中恢复配置。"""
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║  13. 恢复配置                                           ║")
    print("╚════════════════════════════════════════════════════════╝")

    backup_dir = SCRIPT_DIR / "backups"
    if not backup_dir.exists():
        print("⚠️  没有备份目录")
        return

    backups = sorted(d for d in backup_dir.iterdir() if d.is_dir())
    if not backups:
        print("⚠️  没有找到任何备份")
        return

    print("\n可用的备份:")
    for i, b in enumerate(backups):
        print(f"  [{i+1}] {b.name}")

    try:
        idx = int(input("  选择备份编号 (0 取消): ").strip()) - 1
        if idx < 0 or idx >= len(backups):
            return
        chosen = backups[idx]
    except ValueError:
        return

    # 先自动备份当前
    print(f"\n正在从 {chosen.name} 恢复...")
    if not confirm("恢复前会自动备份当前配置，确认继续？"):
        return

    # 备份当前
    _cmd_backup_auto()

    # 恢复
    env_backup = chosen / ".env"
    sess_backup = chosen / "telegram_session.session"

    if env_backup.exists():
        shutil.copy2(env_backup, ENV_FILE)
        print("✅ .env 已恢复")
    if sess_backup.exists():
        shutil.copy2(sess_backup, SESSION_FILE)
        print("✅ Session 文件已恢复")

    print("\n✅ 恢复完成！")
    print("提示: 恢复后建议重启签到程序。")


def _cmd_backup_auto():
    """自动备份当前配置（无交互）。"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = SCRIPT_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    p = backup_dir / f"pre_restore_{timestamp}"
    p.mkdir()
    if ENV_FILE.exists():
        shutil.copy2(ENV_FILE, p / ".env")
    if SESSION_FILE.exists():
        shutil.copy2(SESSION_FILE, p / "telegram_session.session")


# ---------- 15. 一键卸载 ----------

def cmd_uninstall():
    """一键卸载：停止服务、删除 systemd、删除 venv、删除项目。"""
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║  14. 一键卸载                                           ║")
    print("╚════════════════════════════════════════════════════════╝")
    print("\n⚠️  ⚠️  ⚠️  警告！此操作将：")
    print("  ① 停止签到程序")
    print("  ② 停止并删除 systemd 系统服务")
    print("  ③ 删除 Python 虚拟环境")
    print("  ④ 删除整个项目目录")
    print("  ⑤ 清理日志文件")
    print("\n所有配置和数据将永久丢失！")
    print("建议先使用 [13] 备份配置。")
    wait()

    if not confirm("确认卸载？"):
        return

    print("\n正在卸载...")

    # 停止后台进程
    _stop_background()
    print("  已停止后台进程")

    # systemd 服务
    ok, _ = run_cmd(f"sudo systemctl stop {SERVICE_NAME} 2>/dev/null")
    ok, _ = run_cmd(f"sudo systemctl disable {SERVICE_NAME} 2>/dev/null")
    ok, _ = run_cmd(f"sudo rm -f {SYSTEMD_PATH}")
    ok, _ = run_cmd("sudo systemctl daemon-reload 2>/dev/null")
    print("  systemd 服务已清理")

    # 删除日志
    for lf in [LOG_FILE, HISTORY_FILE]:
        if lf.exists():
            lf.unlink()
    print("  日志文件已清理")

    print("\n✅ 卸载完成。")
    print("如需重新安装，可重新克隆/下载项目并运行 manager.py。")


# ---------- 16. 自动获取验证码 ----------

def cmd_get_code():
    """自动获取 Telegram 验证码。"""
    print("\n正在自动获取 Telegram 验证码...")
    py = venv_python()
    if not py or not Path(py).exists():
        print("❌ 虚拟环境未创建，请先运行 [1] 一键安装")
        return

    targets = get_targets()
    if not targets:
        print("⚠️  当前没有配置签到目标，无法确定验证码来源")
        print("   请先运行 [2] 配置签到目标")
        if not confirm("仍然继续获取验证码？", default=False):
            return

    print("  提示：请确保在 Telegram 上触发了发送验证码（如点击 /login 等）")
    print("  脚本将自动检查已有的私聊消息，并监听新的验证码消息")
    print("  等待中，Ctrl+C 停止...\n")
    ok, out = run_cmd(f"{py} get_code.py", check=False, timeout=300)
    if out:
        print(out[-3000:])


# ---------- 主循环 ----------

def main():
    """程序入口。"""
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    while True:
        banner()
        # 显示简要状态
        _, env = load_env_to_lines()
        api_ok = bool(env.get("API_ID") and env.get("API_HASH"))
        targets = get_targets()
        sess_ok = SESSION_FILE.exists()
        print(f"  状态: API凭证={'✅' if api_ok else '❌'}  "
              f"签到目标={len(targets)}  "
              f"Session={'✅' if sess_ok else '❌'}  "
              f"venv={'✅' if VENV_DIR.exists() else '❌'}")

        try:
            choice = main_menu()
        except KeyboardInterrupt:
            print("\n\n再见！")
            break

        if choice == "0":
            print("\n再见！")
            break
        elif choice == "1":
            cmd_install()
        elif choice == "2":
            cmd_configure_targets()
        elif choice == "3":
            cmd_test_login()
        elif choice == "4":
            cmd_list_groups()
        elif choice == "5":
            cmd_test_buttons()
        elif choice == "6":
            cmd_test_group()
        elif choice == "7":
            cmd_manual_checkin()
        elif choice == "8":
            cmd_service_manage()
        elif choice == "9":
            cmd_view_log()
        elif choice == "10":
            cmd_view_history()
        elif choice == "11":
            cmd_edit_time_config()
        elif choice == "12":
            cmd_backup()
        elif choice == "13":
            cmd_restore()
        elif choice == "14":
            cmd_uninstall()
        elif choice == "15":
            cmd_get_code()
        else:
            print("\n⚠️  无效选择，请重新输入")
        print()


if __name__ == "__main__":
    main()
