"""
后台调度模块 - 自动刷新新闻
Background Scheduler Module - Auto refresh news
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scraper import NewsScraper
from config import get_config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsScheduler:
    """新闻自动刷新调度器"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scraper = None
        self.config = get_config()
        self.last_refresh = None

    def start(self):
        """启动调度器"""
        if self.scheduler.running:
            logger.warning("调度器已经在运行中")
            return

        # 添加定时任务 - 每小时刷新一次
        self.scheduler.add_job(
            func=self.refresh_news_task,
            trigger=IntervalTrigger(hours=1),
            id='news_refresh',
            name='刷新新闻',
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("新闻调度器已启动，每小时刷新一次")

    def stop(self):
        """停止调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("新闻调度器已停止")

    def refresh_news_task(self):
        """定时刷新新闻的任务"""
        try:
            if not self.scraper:
                self.scraper = NewsScraper(self.config)

            logger.info("开始自动刷新新闻...")
            result = self.scraper.refresh_news()

            self.last_refresh = datetime.now()

            if result['success']:
                logger.info(f"自动刷新成功，共 {result['count']} 条新闻")
            else:
                logger.warning(f"自动刷新失败: {result['message']}")

            return result
        except Exception as e:
            logger.error(f"自动刷新新闻时出错: {str(e)}")
            return {'success': False, 'message': str(e)}

    def get_status(self):
        """获取调度器状态"""
        return {
            'running': self.scheduler.running,
            'last_refresh': self.last_refresh.isoformat() if self.last_refresh else None,
            'next_refresh': self.scheduler.get_job('news_refresh').next_run_time.isoformat()
            if self.scheduler.running and self.scheduler.get_job('news_refresh') else None
        }

    def trigger_manual_refresh(self):
        """手动触发刷新"""
        return self.refresh_news_task()


# 全局调度器实例
scheduler = NewsScheduler()


def init_scheduler(app):
    """
    初始化调度器（配合 Flask 应用）
    Initialize scheduler with Flask app
    """
    with app.app_context():
        scheduler.start()

    return scheduler
