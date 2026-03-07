"""
配置模块 - 应用程序配置管理
Configuration module - Application settings management
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# Flask 配置
class Config:
    """Flask 应用配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'nintendo-tariff-news-secret-key')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

    # 爬虫配置
    REQUEST_TIMEOUT = 30  # 请求超时时间(秒)
    MAX_RETRIES = 3  # 最大重试次数
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    # 搜索关键词
    SEARCH_KEYWORDS = ['Nintendo', 'tariff', 'US government', 'refund', 'lawsuit']

    # 缓存配置
    CACHE_TIMEOUT = 3600  # 缓存超时时间(秒)

    # 模板配置
    TEMPLATES_AUTO_RELOAD = True


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


# 配置字典
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """获取当前配置"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_dict.get(env, DevelopmentConfig)
