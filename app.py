"""
Flask Web 应用主文件
Flask Web Application Main File

关于 Nintendo 起诉美国政府关税退还诉讼的新闻聚合应用
News aggregation app about Nintendo suing US government for tariff refund
"""

from flask import Flask, render_template, request, redirect, url_for, flash, Response, g
from config import get_config
from scraper import NewsScraper
from utils import format_date, truncate_text, calculate_reading_time, format_error_message
from api import api_bp
from datetime import datetime
import logging
import uuid
import xml.etree.ElementTree as ET

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

    # Request ID middleware
    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())[:8]
        logger.info(f"[{g.request_id}] {request.method} {request.path}")

    @app.after_request
    def after_request(response):
        logger.info(f"[{g.request_id}] Status: {response.status_code}")
        response.headers['X-Request-ID'] = g.request_id
        return response

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'request_id': g.request_id}, 200

    # 注册 API Blueprint
    app.register_blueprint(api_bp)

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

    @app.route('/category/<category>')
    def category_news(category):
        """
        按分类显示新闻
        Show news by category
        """
        try:
            news_list = scraper.filter_by_category(category)
            categories = scraper.get_categories()
            return render_template(
                'index.html',
                news_list=news_list,
                current_category=category,
                categories=categories
            )
        except Exception as e:
            logger.error(f"分类筛选错误: {str(e)}")
            flash(f'筛选时出错: {format_error_message(e)}', 'error')
            return redirect(url_for('index'))

    @app.route('/categories')
    def categories():
        """
        显示所有分类
        Show all categories
        """
        try:
            categories = scraper.get_categories()
            return render_template(
                'index.html',
                news_list=[],
                categories=categories,
                show_categories_only=True
            )
        except Exception as e:
            logger.error(f"获取分类错误: {str(e)}")
            flash(f'获取分类时出错: {format_error_message(e)}', 'error')
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

    @app.route('/feed')
    def rss_feed():
        """
        RSS 2.0 订阅源
        RSS 2.0 Feed
        """
        try:
            news_list = scraper.get_latest_news(limit=20)

            # 构建 RSS XML
            rss = ET.Element('rss', version='2.0')
            channel = ET.SubElement(rss, 'channel')

            # 频道信息
            title = ET.SubElement(channel, 'title')
            title.text = 'Nintendo 关税诉讼新闻'

            link = ET.SubElement(channel, 'link')
            link.text = request.host_url

            description = ET.SubElement(channel, 'description')
            description.text = '关于 Nintendo 起诉美国政府要求退还关税款项的新闻资讯'

            language = ET.SubElement(channel, 'language')
            language.text = 'zh-cn'

            # 添加新闻项
            for news in news_list:
                item = ET.SubElement(channel, 'item')

                item_title = ET.SubElement(item, 'title')
                item_title.text = news.get('title', '')

                item_link = ET.SubElement(item, 'link')
                item_link.text = request.host_url + f'/article/{news.get("id")}'

                item_desc = ET.SubElement(item, 'description')
                item_desc.text = news.get('summary', '')

                item_date = ET.SubElement(item, 'pubDate')
                item_date.text = news.get('date', '')

                item_source = ET.SubElement(item, 'source')
                item_source.text = news.get('source', '')

            # 生成 XML 字符串
            xml_str = ET.tostring(rss, encoding='unicode')

            return Response(
                xml_str,
                mimetype='application/rss+xml',
                headers={'Content-Type': 'application/rss+xml; charset=utf-8'}
            )
        except Exception as e:
            logger.error(f"RSS生成错误: {str(e)}")
            flash(f'生成RSS订阅源时出错', 'error')
            return redirect(url_for('index'))

    @app.route('/feed.xml')
    def rss_feed_xml():
        """RSS 2.0 订阅源 (XML 扩展名)"""
        return rss_feed()

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
