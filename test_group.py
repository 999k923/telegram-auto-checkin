"""
测试脚本 - 查看群组的按钮和可用命令
"""
import asyncio
import logging
from telegram_client import TelegramClientManager

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def test_group():
    """测试群组签到"""
    logger.info("=" * 60)
    logger.info("查看群组签到方式")
    logger.info("=" * 60)
    
    try:
        client_manager = TelegramClientManager()
        await client_manager.start_client()
        
        # 输入群组名称
        group_name = input("\n输入群组名称 (默认: Cloud Cat Group): ").strip()
        if not group_name:
            group_name = "Cloud Cat Group"
        
        # 输入要测试的命令
        command = input(f"输入要发送的命令 (默认: /checkin): ").strip()
        if not command:
            command = "/checkin"
        
        logger.info(f"\n向群组 '{group_name}' 发送: {command}")
        await client_manager.send_message(group_name, command)
        
        # 等待响应
        await asyncio.sleep(3)
        
        # 获取最新消息
        messages = await client_manager.client.get_messages(group_name, limit=3)
        
        if not messages:
            logger.error("❌ 未收到消息")
            logger.info("\n提示: 请确认:")
            logger.info("1. 群组名称是否正确")
            logger.info("2. 你是否在该群组中")
            logger.info("3. 机器人是否在群组中")
            return
        
        # 显示最近的消息
        logger.info(f"\n📨 群组最近的消息:")
        logger.info("-" * 60)
        for idx, msg in enumerate(messages):
            sender = "你" if msg.out else (msg.sender.first_name if msg.sender else "未知")
            text = msg.text if msg.text else "(无文字内容)"
            logger.info(f"\n[{idx + 1}] 发送者: {sender}")
            logger.info(f"内容: {text[:200]}")
            
            # 检查按钮
            if msg.reply_markup:
                logger.info("🔘 此消息包含按钮:")
                for row_idx, row in enumerate(msg.reply_markup.rows):
                    for btn_idx, button in enumerate(row.buttons):
                        logger.info(f"  [{row_idx + 1}-{btn_idx + 1}] {button.text}")
        
        logger.info("-" * 60)
        
        # 询问是否测试点击按钮
        test_click = input("\n是否测试点击按钮? (y/n): ").strip().lower()
        if test_click == 'y':
            button_text = input("输入要点击的按钮文字: ").strip()
            
            if button_text:
                logger.info(f"\n点击按钮: {button_text}")
                result = await client_manager.click_inline_button(
                    group_name,
                    command,
                    button_text
                )
                
                if result:
                    logger.info(f"\n✅ 成功! 回复:\n{result}")
                else:
                    logger.warning("\n⚠️ 点击失败或无回复")
        
        await client_manager.disconnect()
        
        logger.info("\n" + "=" * 60)
        logger.info("测试完成！")
        logger.info("=" * 60)
        logger.info("\n根据测试结果，在 .env 中配置:")
        logger.info(f'  群组名称: {group_name}')
        logger.info(f'  签到命令: {command}')
        if button_text:
            logger.info(f'  按钮文字: {button_text}')
        else:
            logger.info(f'  签到方式: 文本命令（无按钮）')
        
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(test_group())
