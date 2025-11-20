"""
主程序 - 定时自动签到
"""
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from checkin import AutoCheckin
import config

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('auto_checkin.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CheckinScheduler:
    """签到调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone(config.TIMEZONE))
        self.checkin = AutoCheckin()
    
    async def scheduled_checkin(self):
        """定时执行的签到任务"""
        logger.info("🔔 定时签到任务触发")
        await self.checkin.perform_checkin()
    
    def start(self):
        """启动调度器"""
        # 添加定时任务
        self.scheduler.add_job(
            self.scheduled_checkin,
            trigger=CronTrigger(
                hour=config.CHECKIN_HOUR,
                minute=config.CHECKIN_MINUTE,
                timezone=pytz.timezone(config.TIMEZONE)
            ),
            id='daily_checkin',
            name='每日自动签到',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("=" * 60)
        logger.info("🚀 自动签到程序已启动")
        logger.info(f"⏰ 签到时间: 每天 {config.CHECKIN_HOUR:02d}:{config.CHECKIN_MINUTE:02d} ({config.TIMEZONE})")
        logger.info(f"📱 签到目标数量: {len(config.CHECKIN_TARGETS)} 个")
        for idx, target in enumerate(config.CHECKIN_TARGETS, 1):
            method = "按钮点击" if target.get('button_text') else "发送命令"
            logger.info(f"   {idx}. {target['name']} - {method}")
        logger.info("=" * 60)
    
    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("调度器已停止")


async def main():
    """主函数"""
    try:
        # 创建调度器
        scheduler = CheckinScheduler()
        scheduler.start()
        
        # 询问是否立即测试签到
        logger.info("\n提示: 程序已启动，将在每天 {0:02d}:{1:02d} 自动签到".format(
            config.CHECKIN_HOUR, config.CHECKIN_MINUTE
        ))
        
        # 保持程序运行
        while True:
            await asyncio.sleep(3600)  # 每小时检查一次
            
    except KeyboardInterrupt:
        logger.info("\n接收到停止信号，正在关闭...")
        scheduler.stop()
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(main())
