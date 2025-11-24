"""
数据验证工具
"""

import re
from typing import Any


class Validator:
    """数据验证器"""
    
    @staticmethod
    def is_valid_policy_id(policy_id: str) -> bool:
        """验证政策ID格式"""
        if not policy_id:
            return False
        # UUID格式或其他格式
        return len(policy_id) > 0
    
    @staticmethod
    def is_valid_law_rule_type(law_rule_type: Any) -> bool:
        """验证政策类型"""
        try:
            return int(law_rule_type) in [1, 2, 3]
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """验证日期格式"""
        if not date_str:
            return False
        
        patterns = [
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
        ]
        
        return any(bool(re.match(p, date_str)) for p in patterns)
    
    @staticmethod
    def clean_html_entities(text: str) -> str:
        """清理HTML实体"""
        if not text:
            return ""
        
        replacements = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&nbsp;': ' ',
            '&#39;': "'",
            '&quot;': '"',
        }
        
        for entity, char in replacements.items():
            text = text.replace(entity, char)
        
        return text
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """净化文件名"""
        if not filename:
            return "untitled"
        
        illegal_chars = r'<>:"/\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
        filename = filename.strip()
        
        if not filename:
            filename = "untitled"
        
        return filename
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """验证URL格式"""
        if not url:
            return False
        
        pattern = r'^https?://[\w\-]+(\.[\w\-]+)+[/#?]?.*$'
        return bool(re.match(pattern, url))

