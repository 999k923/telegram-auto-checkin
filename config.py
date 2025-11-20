"""
配置文件管理
"""
import os
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Telegram API 配置
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

# 签到时间配置
CHECKIN_HOUR = int(os.getenv('CHECKIN_HOUR', 9))
CHECKIN_MINUTE = int(os.getenv('CHECKIN_MINUTE', 0))

# 时区配置
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Shanghai')

# 随机延迟配置（秒）
RANDOM_DELAY_MIN = int(os.getenv('RANDOM_DELAY_MIN', 0))
RANDOM_DELAY_MAX = int(os.getenv('RANDOM_DELAY_MAX', 300))

# Session 文件路径
SESSION_NAME = 'telegram_session'

# 签到目标配置（支持多个）
def get_checkin_targets():
    """
    获取签到目标列表
    支持两种配置方式：
    1. 单个目标（兼容旧版）
    2. 多个目标（JSON 格式）
    """
    targets = []
    
    # 方式一：从 CHECKIN_TARGETS 读取 JSON 配置（新版，支持多个）
    targets_json = os.getenv('CHECKIN_TARGETS')
    if targets_json:
        try:
            targets = json.loads(targets_json)
            return targets
        except json.JSONDecodeError:
            pass
    
    # 方式二：从单个配置读取（旧版，兼容性）
    bot_username = os.getenv('BOT_USERNAME')
    if bot_username:
        target = {
            'name': bot_username,
            'target': bot_username,
            'command': os.getenv('CHECKIN_COMMAND', '/start'),
            'button_text': os.getenv('CHECKIN_BUTTON_TEXT', '')
        }
        targets.append(target)
    
    return targets

# 获取所有签到目标
CHECKIN_TARGETS = get_checkin_targets()

# 验证必需的配置
if not API_ID or not API_HASH:
    raise ValueError("请在 .env 文件中设置 API_ID 和 API_HASH")
if not PHONE_NUMBER:
    raise ValueError("请在 .env 文件中设置 PHONE_NUMBER")
if not CHECKIN_TARGETS:
    raise ValueError("请在 .env 文件中设置签到目标（BOT_USERNAME 或 CHECKIN_TARGETS）")
