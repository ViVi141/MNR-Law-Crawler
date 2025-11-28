"""
配置管理模块
"""

import os
import json
from typing import Any


class Config:
    """配置管理类"""

    # 默认配置
    DEFAULT_CONFIG = {
        # 数据源配置（支持多个网站）
        "data_sources": [
            {
                "name": "政策法规库",
                "base_url": "https://f.mnr.gov.cn/",
                "search_api": "https://search.mnr.gov.cn/was5/web/search",
                "ajax_api": "https://search.mnr.gov.cn/was/ajaxdata_jsonp.jsp",
                "channel_id": "174757",
                "enabled": True
            }
        ],
        # 兼容旧配置（向后兼容）
        "base_url": "https://f.mnr.gov.cn/",
        "search_api": "https://search.mnr.gov.cn/was5/web/search",
        "ajax_api": "https://search.mnr.gov.cn/was/ajaxdata_jsonp.jsp",
        "channel_id": "174757",  # 政策法规库的频道ID
        
        # 请求配置
        "request_delay": 2,
        "retry_delay": 5,
        "max_retries": 3,
        "rate_limit_delay": 30,
        "session_rotate_interval": 50,
        "timeout": 30,
        
        # 爬取配置
        "page_size": 20,
        "perpage": 20,  # 每页数量
        "max_pages": 999999,  # 最大翻页数
        "max_empty_pages": 3,  # 最大连续空页数
        "categories": [],  # 分类列表，空列表表示搜索全部分类
        
        # 输出配置
        "output_dir": "crawled_data",
        "save_json": True,
        "save_markdown": True,
        "save_docx": True,  # 是否保存DOCX格式
        "save_files": True,
        
        # 搜索配置
        "keywords": [],  # 关键词列表
        "start_date": "",  # 起始日期 yyyy-MM-dd
        "end_date": "",  # 结束日期 yyyy-MM-dd
        
        # 文件下载配置
        "download_docx": True,
        "download_doc": True,
        "download_pdf": False,
        "download_all_files": False,  # 下载所有形式的附件（忽略文件类型）
        
        # 代理配置
        "use_proxy": False,
        "kuaidaili_api_key": "",
        
        # 日志配置
        "log_level": "INFO",
        "log_file": "crawler.log",
        
        # GUI配置
        "window_width": 1200,
        "window_height": 1000,
        "theme": "light",
    }
    
    def __init__(self, config_file: str = "config.json"):
        """初始化配置
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self) -> bool:
        """从文件加载配置
        
        Returns:
            加载是否成功
        """
        if not os.path.exists(self.config_file):
            self.save()
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                self.config.update(user_config)
            return True
        except Exception as e:
            print(f"配置加载失败: {e}")
            return False
    
    def save(self) -> bool:
        """保存配置到文件
        
        Returns:
            保存是否成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"配置保存失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置项
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            是否成功
        """
        self.config[key] = value
        return self.save()
    
    def reset(self) -> bool:
        """重置为默认配置
        
        Returns:
            是否成功
        """
        self.config = self.DEFAULT_CONFIG.copy()
        return self.save()
    
    @property
    def output_dir(self) -> str:
        """输出目录"""
        return self.get("output_dir", "crawled_data")
    
    @property
    def use_proxy(self) -> bool:
        """是否使用代理"""
        return self.get("use_proxy", False)
    
    @property
    def kuaidaili_api_key(self) -> str:
        """快代理API密钥"""
        return self.get("kuaidaili_api_key", "")

