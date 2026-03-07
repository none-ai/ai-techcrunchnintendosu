# Nintendo 关税诉讼新闻聚合应用

## 项目简介

本项目是一个 Flask Web 应用，用于聚合和展示关于 Nintendo 起诉美国政府要求退还关税款项的新闻资讯。

## 项目结构

```
.
├── app.py                 # Flask 应用主文件
├── config.py             # 配置文件
├── requirements.txt     # Python 依赖
├── README.md            # 说明文档
├── scraper/             # 爬虫模块
│   ├── __init__.py
│   └── news_scraper.py  # 新闻爬虫
├── templates/           # HTML 模板
│   ├── index.html      # 首页模板
│   └── article.html   # 文章详情模板
└── utils/              # 工具模块
    ├── __init__.py
    └── helpers.py      # 辅助函数
```

## 功能特性

- 新闻列表展示
- 新闻详情页
- 按来源筛选新闻
- 搜索功能
- 阅读时间计算
- 响应式设计
- 错误处理
- 手动刷新新闻

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python app.py
```

应用将在 http://0.0.0.0:5000 启动

### 3. 访问应用

在浏览器中打开 http://localhost:5000

## 技术栈

- **后端**: Flask 3.0
- **前端**: HTML5 + CSS3
- **爬虫**: requests
- **Python**: 3.8+

## 开发说明

### 配置

在 `config.py` 中可以修改以下配置：

- `DEBUG`: 调试模式
- `REQUEST_TIMEOUT`: 请求超时时间
- `MAX_RETRIES`: 最大重试次数
- `SEARCH_KEYWORDS`: 搜索关键词
- `CACHE_TIMEOUT`: 缓存超时时间

### 模块说明

- **scraper**: 负责从外部获取新闻数据
- **utils**: 包含日期格式化、文本处理等辅助函数
- **templates**: 前端模板文件

作者: stlin256的openclaw
