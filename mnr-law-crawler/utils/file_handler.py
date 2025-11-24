"""
文件处理工具
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path


class FileHandler:
    """文件处理器"""
    
    @staticmethod
    def read_json(filepath: str) -> Optional[Dict]:
        """读取JSON文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取JSON失败: {e}")
            return None
    
    @staticmethod
    def write_json(filepath: str, data: Dict, indent: int = 2) -> bool:
        """写入JSON文件"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            return True
        except Exception as e:
            print(f"写入JSON失败: {e}")
            return False
    
    @staticmethod
    def read_text(filepath: str) -> Optional[str]:
        """读取文本文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文本失败: {e}")
            return None
    
    @staticmethod
    def write_text(filepath: str, content: str) -> bool:
        """写入文本文件"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文本失败: {e}")
            return False
    
    @staticmethod
    def list_files(directory: str, extension: str = None) -> List[str]:
        """列出目录中的文件"""
        try:
            files = []
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    if extension is None or filename.endswith(extension):
                        files.append(filepath)
            return files
        except Exception as e:
            print(f"列出文件失败: {e}")
            return []
    
    @staticmethod
    def ensure_dir(directory: str) -> bool:
        """确保目录存在"""
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败: {e}")
            return False
    
    @staticmethod
    def get_file_size(filepath: str) -> int:
        """获取文件大小"""
        try:
            return os.path.getsize(filepath)
        except (OSError, FileNotFoundError):
            return 0
    
    @staticmethod
    def file_exists(filepath: str) -> bool:
        """检查文件是否存在"""
        return os.path.exists(filepath) and os.path.isfile(filepath)

