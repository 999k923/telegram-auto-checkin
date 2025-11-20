"""
列出所有群组和对话 - 帮助找到正确的群组名称
"""
import asyncio
import logging
from telegram_client import TelegramClientManager
from telethon.tl.types import Chat, Channel

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def list_all_dialogs():
    """列出所有对话（群组、频道、机器人等）"""
    logger.info("=" * 60)
    logger.info("列出所有群组和对话")
    logger.info("=" * 60)
    
    try:
        client_manager = TelegramClientManager()
        await client_manager.start_client()
        
        logger.info("\n正在获取对话列表...")
        
        # 获取所有对话
        dialogs = await client_manager.client.get_dialogs()
        
        groups = []
        channels = []
        bots = []
        users = []
        
        for dialog in dialogs:
            entity = dialog.entity
            name = dialog.name
            
            if isinstance(entity, Chat):
                # 普通群组
                groups.append({
                    'name': name,
                    'id': entity.id,
                    'type': '群组'
                })
            elif isinstance(entity, Channel):
                if entity.broadcast:
                    # 频道
                    channels.append({
                        'name': name,
                        'id': entity.id,
                        'username': entity.username,
                        'type': '频道'
                    })
                else:
                    # 超级群组
                    groups.append({
                        'name': name,
                        'id': entity.id,
                        'username': entity.username,
                        'type': '超级群组'
                    })
            elif hasattr(entity, 'bot') and entity.bot:
                # 机器人
                bots.append({
                    'name': name,
                    'id': entity.id,
                    'username': entity.username,
                    'type': '机器人'
                })
            else:
                # 私聊用户
                users.append({
                    'name': name,
                    'id': entity.id,
                    'type': '用户'
                })
        
        # 显示群组
        if groups:
            logger.info("\n" + "=" * 60)
            logger.info("📱 群组列表")
            logger.info("=" * 60)
            for idx, group in enumerate(groups):
                logger.info(f"\n[{idx + 1}] 名称: {group['name']}")
                logger.info(f"    类型: {group['type']}")
                logger.info(f"    ID: {group['id']}")
                if 'username' in group and group['username']:
                    logger.info(f"    用户名: @{group['username']}")
                logger.info(f"    ✅ 配置使用: {group['name']}")
        
        # 显示机器人
        if bots:
            logger.info("\n" + "=" * 60)
            logger.info("🤖 机器人列表")
            logger.info("=" * 60)
            for idx, bot in enumerate(bots):
                logger.info(f"\n[{idx + 1}] 名称: {bot['name']}")
                logger.info(f"    用户名: @{bot['username']}")
                logger.info(f"    ID: {bot['id']}")
                logger.info(f"    ✅ 配置使用: @{bot['username']}")
        
        # 显示频道（可选）
        if channels and len(channels) < 20:
            logger.info("\n" + "=" * 60)
            logger.info("📢 频道列表（前20个）")
            logger.info("=" * 60)
            for idx, channel in enumerate(channels[:20]):
                logger.info(f"\n[{idx + 1}] 名称: {channel['name']}")
                if channel.get('username'):
                    logger.info(f"    用户名: @{channel['username']}")
        
        await client_manager.disconnect()
        
        logger.info("\n" + "=" * 60)
        logger.info("提示：")
        logger.info("=" * 60)
        logger.info("1. 复制上面显示的【名称】到 .env 配置中")
        logger.info("2. 群组名称必须完全匹配（包括大小写、空格）")
        logger.info("3. 机器人使用 @username 格式")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n❌ 获取对话列表失败: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(list_all_dialogs())
