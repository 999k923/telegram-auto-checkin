"""
列出所有群组和对话 - 帮助找到正确的群组名称
"""
import asyncio
import logging
from telegram_client import TelegramClientManager
from telethon.tl.types import Chat, Channel, User

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
            
            # 判断类型
            if hasattr(entity, 'bot') and entity.bot:
                # 机器人
                bots.append({
                    'name': name,
                    'id': entity.id,
                    'username': getattr(entity, 'username', None),
                    'type': '机器人'
                })
            elif isinstance(entity, Chat):
                # 普通群组
                groups.append({
                    'name': name,
                    'id': entity.id,
                    'username': getattr(entity, 'username', None),
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
            elif isinstance(entity, User):
                # 私聊用户
                users.append({
                    'name': name,
                    'id': entity.id,
                    'type': '用户'
                })
            else:
                users.append({
                    'name': name,
                    'id': entity.id,
                    'type': '用户'
                })
        
        # 显示群组
        if groups:
            logger.info("\n" + "=" * 60)
            logger.info("📱 群组列表（共 {} 个）".format(len(groups)))
            logger.info("=" * 60)
            for idx, group in enumerate(groups):
                logger.info(f"\n[{idx + 1}] 名称: {group['name']}")
                logger.info(f"    类型: {group['type']}")
                logger.info(f"    ID: {group['id']}")
                if group.get('username'):
                    logger.info(f"    用户名: @{group['username']}")
                logger.info(f"    ✅ 配置使用: {group['name']}")
        else:
            logger.info("\n📱 群组列表: 无")
        
        # 显示频道
        if channels:
            logger.info("\n" + "=" * 60)
            logger.info("📢 频道列表（共 {} 个）".format(len(channels)))
            logger.info("=" * 60)
            for idx, channel in enumerate(channels):
                logger.info(f"\n[{idx + 1}] 名称: {channel['name']}")
                logger.info(f"    ID: {channel['id']}")
                if channel.get('username'):
                    logger.info(f"    用户名: @{channel['username']}")
                logger.info(f"    ✅ 配置使用: {channel['name']}")
        else:
            logger.info("\n📢 频道列表: 无")
        
        # 显示机器人
        if bots:
            logger.info("\n" + "=" * 60)
            logger.info("🤖 机器人列表（共 {} 个）".format(len(bots)))
            logger.info("=" * 60)
            for idx, bot in enumerate(bots):
                logger.info(f"\n[{idx + 1}] 名称: {bot['name']}")
                if bot.get('username'):
                    logger.info(f"    用户名: @{bot['username']}")
                logger.info(f"    ID: {bot['id']}")
                logger.info(f"    ✅ 配置使用: @{bot['username']}")
        else:
            logger.info("\n🤖 机器人列表: 无")
        
        # 显示用户（私聊）
        if users:
            logger.info("\n" + "=" * 60)
            logger.info("👤 私聊用户列表（共 {} 个）".format(len(users)))
            logger.info("=" * 60)
            for idx, user in enumerate(users):
                logger.info(f"\n[{idx + 1}] 名称: {user['name']}")
                logger.info(f"    ID: {user['id']}")
        else:
            logger.info("\n👤 私聊用户列表: 无")
        
        await client_manager.disconnect()
        
        logger.info("\n" + "=" * 60)
        logger.info("提示：")
        logger.info("=" * 60)
        logger.info("1. 复制上面显示的【名称】到 .env 配置中")
        logger.info("2. 群组/频道名称必须完全匹配（包括大小写、空格）")
        logger.info("3. 机器人使用 @username 格式")
        logger.info("4. 所有目标都可以用于签到（不限类型）")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n❌ 获取对话列表失败: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(list_all_dialogs())
