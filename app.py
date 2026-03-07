"""
Flask Web 应用主文件
Flask Web Application Main File

关于 Nintendo 起诉美国政府关税退还诉讼的新闻聚合应用
News aggregation app about Nintendo suing US government for tariff refund
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from config import get_config
from scraper import NewsScraper
from utils import format_date, truncate_text, calculate_reading_time, format_error_message
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_class=None):
    """
    创建Flask应用实例
    Create Flask application instance

    Args:
        config_class: 配置类

    Returns:
        Flask应用实例
    """
    app = Flask(__name__)

    # 加载配置
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # 初始化爬虫
    scraper = NewsScraper(config_class)

    @app.route('/')
    def index():
        """
        首页 - 显示新闻列表
        Home page - Show news list
        """
        try:
            # 获取搜索关键词
            search = request.args.get('search', '')

            # 获取新闻来源筛选
            source = request.args.get('source', '')

            # 获取所有新闻
            if search:
                news_list = scraper.search_news(search)
            elif source:
                news_list = scraper.filter_by_source(source)
            else:
                news_list = scraper.get_latest_news()

            # 获取所有可用来源
            sources = list(set([news['source'] for news in scraper.search_news()]))

            return render_template(
                'index.html',
                news_list=news_list,
                sources=sources,
                current_search=search,
                current_source=source
            )
        except Exception as e:
            logger.error(f"首页加载错误: {str(e)}")
            flash(f'加载新闻时出错: {format_error_message(e)}', 'error')
            return render_template('index.html', news_list=[], sources=[])

    @app.route('/article/<int:news_id>')
    def article(news_id):
        """
        文章详情页
        Article detail page
        """
        try:
            news = scraper.get_news_by_id(news_id)

            if not news:
                flash('未找到该文章', 'warning')
                return redirect(url_for('index'))

            # 计算阅读时间
            reading_time = calculate_reading_time(news.get('content', ''))

            return render_template(
                'article.html',
                news=news,
                reading_time=reading_time
            )
        except Exception as e:
            logger.error(f"文章加载错误: {str(e)}")
            flash(f'加载文章时出错: {format_error_message(e)}', 'error')
            return redirect(url_for('index'))

    @app.route('/search')
    def search():
        """
        搜索页面
        Search page
        """
        query = request.args.get('q', '')

        if not query:
            flash('请输入搜索关键词', 'info')
            return redirect(url_for('index'))

        try:
            news_list = scraper.search_news(query)
            return render_template(
                'index.html',
                news_list=news_list,
                current_search=query
            )
        except Exception as e:
            logger.error(f"搜索错误: {str(e)}")
            flash(f'搜索时出错: {format_error_message(e)}', 'error')
            return redirect(url_for('index'))

    @app.route('/source/<source>')
    def source_news(source):
        """
        按来源显示新闻
        Show news by source
        """
        try:
            news_list = scraper.filter_by_source(source)
            return render_template(
                'index.html',
                news_list=news_list,
                current_source=source
            )
        except Exception as e:
            logger.error(f"来源筛选错误: {str(e)}")
            flash(f'筛选时出错: {format_error_message(e)}', 'error')
            return redirect(url_for('index'))

    @app.route('/refresh')
    def refresh():
        """
        手动刷新新闻
        Manual news refresh
        """
        try:
            result = scraper.refresh_news()
            if result['success']:
                flash(f"新闻刷新成功，共 {result['count']} 条", 'success')
            else:
                flash(f"刷新失败: {result['message']}", 'error')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"刷新错误: {str(e)}")
            flash(f'刷新时出错: {format_error_message(e)}', 'error')
            return redirect(url_for('index'))

    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return render_template('error.html', error_code=404, message='页面未找到'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        return render_template('error.html', error_code=500, message='服务器内部错误'), 500

    return app


# 应用实例
app = create_app()


if __name__ == '__main__':
    """
    主程序入口
    Main program entry point
    """
    app.run(host='0.0.0.0', port=5000, debug=True)
