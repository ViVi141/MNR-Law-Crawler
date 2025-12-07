"""
核心业务逻辑模块
"""

__version__ = "2.0.0"
__author__ = "ViVi141"
__project_name__ = "mnr-law-crawler"
__github_url__ = "https://github.com/ViVi141/mnr-law-crawler"
__email__ = "747384120@qq.com"

from .crawler import PolicyCrawler
from .converter import DocumentConverter
from .api_client import APIClient
from .config import Config
from .models import Policy, PolicyDetail, FileAttachment, CrawlProgress

__all__ = [
    "PolicyCrawler",
    "DocumentConverter",
    "APIClient",
    "Config",
    "Policy",
    "PolicyDetail",
    "FileAttachment",
    "CrawlProgress",
]

