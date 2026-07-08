"""
自动签到功能模块
"""
import logging
import asyncio
import random
from datetime import datetime
from telegram_client import TelegramClientManager
import config

logger = logging.getLogger(__name__)


class AutoCheckin:
    """自动签到类"""
    
    def __init__(self):
        self.client_manager = TelegramClientManager()
    
    async def perform_checkin(self, skip_delay=False):
        """执行签到操作（所有目标）
        
        Args:
            skip_delay: True 则跳过随机延迟（手动签到使用）
        """
        try:
            # 启动客户端
            await self.client_manager.start_client()
            
            # 遍历所有签到目标
            for target_config in config.CHECKIN_TARGETS:
                await self._checkin_single_target(target_config, skip_delay=skip_delay)
                
                # 多个目标之间添加延迟
                if len(config.CHECKIN_TARGETS) > 1 and not skip_delay:
                    await asyncio.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ 签到失败: {e}", exc_info=True)
        finally:
            await self.client_manager.disconnect()
    
    async def _checkin_single_target(self, target_config, skip_delay=False):
        """
        执行单个目标的签到
        
        Args:
            target_config: 签到配置字典
            skip_delay: True 则跳过随机延迟（手动签到使用）
        """
        try:
            name = target_config.get('name', target_config['target'])
            target = target_config['target']
            command = target_config['command']
            button_text = target_config.get('button_text', '')
            
            logger.info(f"\n{'='*60}")
            logger.info(f"开始签到: {name}")
            logger.info(f"{'='*60}")
            
            # 随机延迟（模拟人类行为），手动签到时跳过
            if not skip_delay and config.RANDOM_DELAY_MAX > 0:
                delay = random.randint(config.RANDOM_DELAY_MIN, config.RANDOM_DELAY_MAX)
                logger.info(f"⏳ 随机延迟 {delay} 秒...")
                await asyncio.sleep(delay)
            
            # 检查签到方式：按钮点击 或 文本命令
            response = None
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if button_text:
                # 使用按钮点击方式
                logger.info(f"📤 向 {target} 发送 {command} 并点击按钮: {button_text}")
                response = await self.client_manager.click_inline_button(
                    target,
                    command,
                    button_text
                )
            else:
                # 使用文本命令方式
                logger.info(f"📤 向 {target} 发送签到命令: {command}")
                response = await self.client_manager.get_bot_response(
                    target,
                    command
                )
            
            # 记录签到结果
            if response:
                logger.info(f"✅ [{current_time}] {name} 签到成功!")
                logger.info(f"📨 回复: {response[:200]}")  # 只显示前200字符
                
                # 保存签到记录
                self._save_checkin_record(name, target, command, current_time, response)
            else:
                logger.warning(f"⚠️ [{current_time}] {name} 未收到回复或签到失败")
            
        except Exception as e:
            logger.error(f"❌ {name} 签到失败: {e}", exc_info=True)
    
    def _save_checkin_record(self, name, target, command, timestamp, response):
        """保存签到记录到文件"""
        try:
            with open('checkin_history.log', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"签到目标: {name}\n")
                f.write(f"时间: {timestamp}\n")
                f.write(f"目标: {target}\n")
                f.write(f"命令: {command}\n")
                f.write(f"回复: {response}\n")
        except Exception as e:
            logger.error(f"保存签到记录失败: {e}")


async def test_checkin():
    """测试签到功能"""
    logger.info("开始测试签到...")
    checkin = AutoCheckin()
    await checkin.perform_checkin()
    logger.info("测试完成")


if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # 运行测试
    asyncio.run(test_checkin())
