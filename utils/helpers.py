"""
工具函数模块 - 常用的辅助函数
Utility Functions Module - Common helper functions
"""

from datetime import datetime
from typing import Optional
import re


def format_date(date_str: str, input_format: str = '%Y-%m-%d', output_format: str = '%Y年%m月%d日') -> str:
    """
    格式化日期字符串
    Format date string

    Args:
        date_str: 输入日期字符串
        input_format: 输入日期格式
        output_format: 输出日期格式

    Returns:
        格式化后的日期字符串
    """
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except (ValueError, TypeError):
        return date_str


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    截断文本到指定长度
    Truncate text to specified length

    Args:
        text: 输入文本
        max_length: 最大长度
        suffix: 截断后缀

    Returns:
        截断后的文本
    """
    if not text:
        return ''

    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def validate_url(url: str) -> bool:
    """
    验证URL格式是否有效
    Validate URL format

    Args:
        url: URL字符串

    Returns:
        是否有效
    """
    if not url:
        return False

    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(url_pattern.match(url))


def sanitize_html(html: str) -> str:
    """
    简单的HTML转义处理
    Simple HTML escaping

    Args:
        html: HTML字符串

    Returns:
        转义后的字符串
    """
    if not html:
        return ''

    # 替换特殊字符
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;'
    }

    for old, new in replacements.items():
        html = html.replace(old, new)

    return html


def get_news_source_label(source: str) -> str:
    """
    获取新闻来源的显示标签
    Get display label for news source

    Args:
        source: 新闻来源

    Returns:
        格式化的来源标签
    """
    source_labels = {
        'techcrunch': 'TechCrunch',
        'reuters': '路透社',
        'bloomberg': '彭博社',
        'ap news': '美联社',
        'the verge': 'The Verge'
    }

    source_lower = source.lower()
    return source_labels.get(source_lower, source)


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    计算阅读时间（分钟）
    Calculate reading time in minutes

    Args:
        text: 文本内容
        words_per_minute: 每分钟阅读字数

    Returns:
        预计阅读时间（分钟）
    """
    if not text:
        return 0

    word_count = len(text.split())
    reading_time = max(1, round(word_count / words_per_minute))

    return reading_time


def format_error_message(error: Exception) -> str:
    """
    格式化错误消息
    Format error message

    Args:
        error: 异常对象

    Returns:
        格式化的错误消息
    """
    error_type = type(error).__name__
    error_message = str(error)

    return f"{error_type}: {error_message}"
