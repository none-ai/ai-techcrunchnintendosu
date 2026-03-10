"""
API 模块 - 提供 REST API 接口
API Module - REST API endpoints
"""

from flask import Blueprint, jsonify, request, current_app
from scraper import NewsScraper
from config import get_config
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 API Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


def get_scraper():
    """获取爬虫实例"""
    config = get_config()
    return NewsScraper(config)


@api_bp.route('/news')
def get_news():
    """
    获取新闻列表
    Query params:
        - limit: 返回数量限制 (default: 10)
        - source: 按来源筛选
        - keyword: 搜索关键词
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        source = request.args.get('source', '')
        keyword = request.args.get('keyword', '')

        scraper = get_scraper()

        if keyword:
            news_list = scraper.search_news(keyword)
        elif source:
            news_list = scraper.filter_by_source(source)
        else:
            news_list = scraper.get_latest_news(limit=limit)

        # 限制返回数量
        news_list = news_list[:limit]

        return jsonify({
            'success': True,
            'count': len(news_list),
            'data': news_list
        })
    except Exception as e:
        logger.error(f"API获取新闻错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/news/<int:news_id>')
def get_news_detail(news_id):
    """
    获取单条新闻详情
    """
    try:
        scraper = get_scraper()
        news = scraper.get_news_by_id(news_id)

        if not news:
            return jsonify({
                'success': False,
                'error': 'News not found'
            }), 404

        return jsonify({
            'success': True,
            'data': news
        })
    except Exception as e:
        logger.error(f"API获取新闻详情错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/sources')
def get_sources():
    """
    获取所有新闻来源
    """
    try:
        scraper = get_scraper()
        all_news = scraper.search_news()
        sources = list(set([news['source'] for news in all_news]))

        return jsonify({
            'success': True,
            'count': len(sources),
            'data': sources
        })
    except Exception as e:
        logger.error(f"API获取来源错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/categories')
def get_categories():
    """
    获取所有新闻分类
    """
    try:
        scraper = get_scraper()
        categories = scraper.get_categories()

        return jsonify({
            'success': True,
            'count': len(categories),
            'data': categories
        })
    except Exception as e:
        logger.error(f"API获取分类错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/news/category/<category>')
def get_news_by_category(category):
    """
    按分类获取新闻
    """
    try:
        scraper = get_scraper()
        news_list = scraper.filter_by_category(category)

        return jsonify({
            'success': True,
            'count': len(news_list),
            'data': news_list
        })
    except Exception as e:
        logger.error(f"API获取分类新闻错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/refresh', methods=['POST'])
def refresh_news():
    """
    刷新新闻数据
    """
    try:
        scraper = get_scraper()
        result = scraper.refresh_news()

        return jsonify({
            'success': result['success'],
            'count': result['count'],
            'message': result['message']
        })
    except Exception as e:
        logger.error(f"API刷新新闻错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/health')
def health_check():
    """
    健康检查接口
    """
    return jsonify({
        'success': True,
        'status': 'healthy',
        'version': '1.0.0'
    })


@api_bp.route('/stats')
def get_stats():
    """
    获取新闻统计信息
    """
    try:
        scraper = get_scraper()
        all_news = scraper.search_news()
        
        sources = list(set([news['source'] for news in all_news]))
        categories = scraper.get_categories()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_news': len(all_news),
                'total_sources': len(sources),
                'total_categories': len(categories),
                'sources': sources,
                'categories': categories
            }
        })
    except Exception as e:
        logger.error(f"API获取统计信息错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
