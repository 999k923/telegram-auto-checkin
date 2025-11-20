"""
测试脚本 - 验证 Telegram 登录和配置
"""
import asyncio
import logging
from telegram_client import TelegramClientManager
import config

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def test_login():
    """测试登录"""
    logger.info("=" * 60)
    logger.info("Telegram 登录测试")
    logger.info("=" * 60)
    
    try:
        client_manager = TelegramClientManager()
        await client_manager.start_client()
        
        logger.info("\n✅ 登录成功！")
        logger.info(f"📱 目标机器人: {config.BOT_USERNAME}")
        logger.info(f"📝 签到命令: {config.CHECKIN_COMMAND}")
        
        # 测试发送消息
        response = input("\n是否测试发送签到命令? (y/n): ")
        if response.lower() == 'y':
            logger.info(f"\n向 {config.BOT_USERNAME} 发送: {config.CHECKIN_COMMAND}")
            result = await client_manager.get_bot_response(
                config.BOT_USERNAME,
                config.CHECKIN_COMMAND
            )
            
            if result:
                logger.info(f"\n✅ 收到回复:\n{result}")
            else:
                logger.warning("\n⚠️ 未收到回复")
        
        await client_manager.disconnect()
        logger.info("\n测试完成！")
        
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(test_login())
