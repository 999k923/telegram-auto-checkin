"""
Telegram 客户端管理
"""
import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import config

logger = logging.getLogger(__name__)


class TelegramClientManager:
    """Telegram 客户端管理器"""
    
    def __init__(self):
        self.client = TelegramClient(
            config.SESSION_NAME,
            config.API_ID,
            config.API_HASH
        )
    
    async def start_client(self):
        """启动客户端并登录"""
        await self.client.start(phone=config.PHONE_NUMBER)
        
        if not await self.client.is_user_authorized():
            logger.info("需要登录...")
            
            # 发送验证码
            await self.client.send_code_request(config.PHONE_NUMBER)
            
            try:
                # 等待用户输入验证码
                code = input('请输入收到的验证码: ')
                await self.client.sign_in(config.PHONE_NUMBER, code)
            except SessionPasswordNeededError:
                # 如果启用了两步验证
                password = input('请输入两步验证密码: ')
                await self.client.sign_in(password=password)
        
        logger.info("✅ Telegram 客户端登录成功")
        me = await self.client.get_me()
        logger.info(f"当前登录账号: {me.first_name} (@{me.username})")
    
    async def get_entity(self, target):
        """
        获取目标实体（支持多种格式）
        
        Args:
            target: 目标标识（用户名、群组名称、ID等）
        
        Returns:
            实体对象
        """
        try:
            # 尝试直接获取
            entity = await self.client.get_entity(target)
            return entity
        except Exception as e:
            logger.warning(f"直接获取实体失败: {e}")
            
            # 如果是数字，尝试作为ID
            if isinstance(target, int) or (isinstance(target, str) and target.lstrip('-').isdigit()):
                try:
                    entity_id = int(target)
                    entity = await self.client.get_entity(entity_id)
                    logger.info(f"✅ 通过ID找到实体: {entity_id}")
                    return entity
                except:
                    pass
            
            # 搜索对话列表
            logger.info(f"在对话列表中搜索: {target}")
            async for dialog in self.client.iter_dialogs():
                if dialog.name == target or (hasattr(dialog.entity, 'username') and dialog.entity.username == target.lstrip('@')):
                    logger.info(f"✅ 在对话列表中找到: {dialog.name}")
                    return dialog.entity
            
            raise ValueError(f"无法找到目标: {target}")
    
    async def send_message(self, target, message):
        """
        发送消息到指定目标
        
        Args:
            target: 目标用户名、群组名称或ID
            message: 消息内容
        """
        try:
            # 获取实体
            entity = await self.get_entity(target)
            result = await self.client.send_message(entity, message)
            logger.info(f"✅ 消息已发送到 {target}: {message}")
            return result
        except Exception as e:
            logger.error(f"❌ 发送消息失败: {e}")
            raise
    
    async def get_bot_response(self, target, command, timeout=10):
        """
        发送命令并等待机器人回复
        
        Args:
            target: 机器人用户名或实体
            command: 要发送的命令
            timeout: 等待回复超时时间（秒）
        """
        try:
            # 获取对话
            from telethon import functions
            import asyncio
            
            # 获取实体
            entity = await self.get_entity(target)
            
            # 发送命令
            await self.client.send_message(entity, command)
            logger.info(f"✅ 命令已发送到 {target}: {command}")
            
            # 等待回复
            logger.info(f"等待 {target} 的回复...")
            await asyncio.sleep(2)  # 给机器人一点时间响应
            
            # 获取最新消息
            messages = await self.client.get_messages(entity, limit=5)
            
            if messages:
                logger.info(f"收到回复: {messages[0].text}")
                return messages[0].text
            
            return None
        except Exception as e:
            logger.error(f"❌ 获取机器人回复失败: {e}")
            return None
    
    async def click_inline_button(self, target, command, button_text):
        """
        发送命令并点击内联键盘按钮
        
        Args:
            target: 机器人用户名、群组名称或ID
            command: 要发送的命令（如 /start）
            button_text: 按钮文字（如 "签到"）
        """
        try:
            import asyncio
            from telethon.tl.types import KeyboardButtonCallback, KeyboardButtonUrl
            
            # 获取实体
            entity = await self.get_entity(target)
            
            # 发送命令
            logger.info(f"📤 向 {target} 发送命令: {command}")
            await self.client.send_message(entity, command)
            
            # 等待机器人响应
            await asyncio.sleep(2)
            
            # 获取最新消息（包含内联键盘）
            messages = await self.client.get_messages(entity, limit=1)
            
            if not messages:
                logger.error("❌ 未收到机器人消息")
                return None
            
            message = messages[0]
            logger.info(f"收到消息: {message.text[:100] if message.text else '(无文字)'}")
            
            # 检查是否有内联键盘
            if not message.reply_markup:
                logger.error("❌ 消息中没有键盘按钮")
                return None
            
            # 查找匹配的按钮
            button_found = False
            for row in message.reply_markup.rows:
                for button in row.buttons:
                    logger.info(f"找到按钮: {button.text}")
                    
                    # 检查按钮文字是否包含目标文字
                    if button_text in button.text:
                        logger.info(f"🎯 找到目标按钮: {button.text}")
                        
                        # 点击按钮
                        await message.click(text=button.text)
                        button_found = True
                        logger.info(f"✅ 已点击按钮: {button.text}")
                        
                        # 等待响应
                        await asyncio.sleep(2)
                        
                        # 获取点击后的回复
                        response_messages = await self.client.get_messages(entity, limit=3)
                        if response_messages:
                            response_text = response_messages[0].text
                            logger.info(f"📨 点击后收到回复: {response_text[:200] if response_text else '(无文字)'}")
                            return response_text
                        
                        break
                
                if button_found:
                    break
            
            if not button_found:
                logger.error(f"❌ 未找到包含 '{button_text}' 的按钮")
                logger.info("可用的按钮有:")
                for row in message.reply_markup.rows:
                    for button in row.buttons:
                        logger.info(f"  - {button.text}")
                return None
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 点击按钮失败: {e}", exc_info=True)
            return None
    
    async def disconnect(self):
        """断开连接"""
        await self.client.disconnect()
        logger.info("Telegram 客户端已断开")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client.is_connected():
            self.client.disconnect()
