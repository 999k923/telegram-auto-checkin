"""
测试脚本 - 查看机器人的所有按钮
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


async def test_buttons():
    """测试查看机器人按钮"""
    logger.info("=" * 60)
    logger.info("查看机器人按钮")
    logger.info("=" * 60)
    
    try:
        client_manager = TelegramClientManager()
        await client_manager.start_client()
        
        # 发送命令
        command = input(f"\n输入要发送的命令 (默认: {config.CHECKIN_COMMAND}): ").strip()
        if not command:
            command = config.CHECKIN_COMMAND
        
        logger.info(f"\n向 {config.BOT_USERNAME} 发送: {command}")
        await client_manager.send_message(config.BOT_USERNAME, command)
        
        # 等待响应
        await asyncio.sleep(2)
        
        # 获取最新消息
        messages = await client_manager.client.get_messages(config.BOT_USERNAME, limit=1)
        
        if not messages:
            logger.error("❌ 未收到消息")
            return
        
        message = messages[0]
        
        # 显示消息文本
        if message.text:
            logger.info(f"\n📨 机器人回复:\n{message.text}\n")
        
        # 检查按钮
        if message.reply_markup:
            logger.info("🔘 找到以下按钮:")
            logger.info("-" * 60)
            
            button_list = []
            for row_idx, row in enumerate(message.reply_markup.rows):
                row_buttons = []
                for btn_idx, button in enumerate(row.buttons):
                    logger.info(f"  [{row_idx + 1}-{btn_idx + 1}] {button.text}")
                    row_buttons.append(button.text)
                    button_list.append(button.text)
            
            logger.info("-" * 60)
            
            # 询问是否测试点击
            if button_list:
                test_click = input("\n是否测试点击按钮? (y/n): ").strip().lower()
                if test_click == 'y':
                    button_text = input(f"输入要点击的按钮文字 (如: {button_list[0]}): ").strip()
                    
                    if button_text:
                        logger.info(f"\n点击按钮: {button_text}")
                        result = await client_manager.click_inline_button(
                            config.BOT_USERNAME,
                            command,
                            button_text
                        )
                        
                        if result:
                            logger.info(f"\n✅ 成功! 机器人回复:\n{result}")
                        else:
                            logger.warning("\n⚠️ 点击失败或无回复")
        else:
            logger.warning("❌ 此消息没有按钮")
            logger.info("提示: 尝试发送其他命令，如 /start, /menu 等")
        
        await client_manager.disconnect()
        
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(test_buttons())
