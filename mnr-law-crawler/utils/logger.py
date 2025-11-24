"""
日志模块
"""

import logging
import sys
from typing import Optional
from pathlib import Path


class Logger:
    """日志管理器"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(
        cls,
        name: str = "mnr-law-crawler",
        level: str = "INFO",
        log_file: Optional[str] = None
    ) -> logging.Logger:
        """获取或创建日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别
            log_file: 日志文件路径
            
        Returns:
            日志记录器
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # 清除现有处理器
        logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def info(cls, message: str):
        """记录信息"""
        cls.get_logger().info(message)
    
    @classmethod
    def warning(cls, message: str):
        """记录警告"""
        cls.get_logger().warning(message)
    
    @classmethod
    def error(cls, message: str):
        """记录错误"""
        cls.get_logger().error(message)
    
    @classmethod
    def debug(cls, message: str):
        """记录调试信息"""
        cls.get_logger().debug(message)

