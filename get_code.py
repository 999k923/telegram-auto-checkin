import asyncio
import logging
import re
from telethon import events
from telegram_client import TelegramClientManager

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def listen_for_auth_code():
    logger.info("=" * 60)
    logger.info("正在通过现有 Session 启动验证码监听器...")
    logger.info("=" * 60)
    
    try:
        # 复用现有的客户端管理器
        client_manager = TelegramClientManager()
        await client_manager.start_client()
        
        # 拿到实际的 telethon client 实例
        client = client_manager.client
        
        # 检查 Session 是否有效
        if not await client.is_user_authorized():
            logger.error("❌ 失败: 该 Session 文件已失效或已被官方强制下线。")
            await client_manager.disconnect()
            return

        logger.info("🚀 成功登录并进入监听状态！")
        logger.info("【 此时，请在你的新设备上点击发送验证码 】\n")

        # 注册事件监听器：只监听来自 Telegram 官方账号（777000）的消息
        @client.on(events.NewMessage(chats=777000))
        async def handler(event):
            msg_text = event.message.message
            logger.info("\n" + "="*40)
            logger.info(f"📩 收到 Telegram 官方消息:\n\n{msg_text}")
            logger.info("="*40)
            
            # 使用正则表达式匹配 5-6 位验证码
            code = re.search(r'\b\d{5,6}\b', msg_text)
            if code:
                logger.info(f"\n🎉 自动识别到登录验证码: 🌟 {code.group(0)} 🌟")
            else:
                logger.warning("\n⚠️ 未在消息中匹配到验证码，请手动查看上方消息主体。")

        # 保持程序运行以持续等待新消息
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"\n❌ 运行过程中出现错误: {e}", exc_info=True)

if __name__ == '__main__':
    try:
        asyncio.run(listen_for_auth_code())
    except KeyboardInterrupt:
        logger.info("\n程序已手动停止。")
