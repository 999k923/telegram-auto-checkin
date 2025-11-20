"""
手动签到脚本 - 立即执行一次签到
"""
import asyncio
import logging
from checkin import AutoCheckin

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main():
    """手动执行签到"""
    logger.info("=" * 60)
    logger.info("手动签到")
    logger.info("=" * 60)
    
    checkin = AutoCheckin()
    await checkin.perform_checkin()
    
    logger.info("\n签到完成！")


if __name__ == '__main__':
    asyncio.run(main())
