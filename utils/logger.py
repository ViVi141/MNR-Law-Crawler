"""
日志模块 - 优化版
提供统一的日志管理，支持文件轮转、日志级别控制、性能优化
"""

import logging
import sys
from typing import Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（用于控制台输出）"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # 添加颜色
        if sys.stdout.isatty() and record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        
        return super().format(record)


class Logger:
    """日志管理器 - 优化版"""
    
    _loggers = {}
    _default_log_dir = Path("logs")
    
    @classmethod
    def get_logger(
        cls,
        name: str = "mnr-law-crawler",
        level: str = "INFO",
        log_file: Optional[str] = None,
        log_dir: Optional[str] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True,
        file_output: bool = True
    ) -> logging.Logger:
        """获取或创建日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: 日志文件路径（如果为None，使用默认路径）
            log_dir: 日志目录（如果为None，使用默认目录）
            max_bytes: 单个日志文件最大大小（字节）
            backup_count: 保留的备份文件数量
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            
        Returns:
            日志记录器
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # 清除现有处理器，避免重复添加
        logger.handlers.clear()
        
        # 防止日志传播到根logger
        logger.propagate = False
        
        # 控制台处理器（带颜色）
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_formatter = ColoredFormatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # 文件处理器（带轮转）
        if file_output:
            if log_file is None:
                # 使用默认日志目录和文件名
                if log_dir is None:
                    log_dir = cls._default_log_dir
                else:
                    log_dir = Path(log_dir)
                
                log_dir.mkdir(parents=True, exist_ok=True)
                log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            else:
                log_file = Path(log_file)
                log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 使用RotatingFileHandler实现日志轮转
            file_handler = RotatingFileHandler(
                str(log_file),
                encoding='utf-8',
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
            file_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def setup_from_config(cls, config: dict):
        """从配置字典设置日志
        
        Args:
            config: 配置字典，包含 log_level, log_file, log_dir 等
        """
        log_level = config.get("log_level", "INFO")
        log_file = config.get("log_file")
        log_dir = config.get("log_dir")
        
        cls.get_logger(
            level=log_level,
            log_file=log_file,
            log_dir=log_dir
        )
    
    @classmethod
    def info(cls, message: str, logger_name: str = "mnr-law-crawler"):
        """记录信息"""
        cls.get_logger(logger_name).info(message)
    
    @classmethod
    def warning(cls, message: str, logger_name: str = "mnr-law-crawler"):
        """记录警告"""
        cls.get_logger(logger_name).warning(message)
    
    @classmethod
    def error(cls, message: str, logger_name: str = "mnr-law-crawler", exc_info: bool = False):
        """记录错误"""
        cls.get_logger(logger_name).error(message, exc_info=exc_info)
    
    @classmethod
    def debug(cls, message: str, logger_name: str = "mnr-law-crawler"):
        """记录调试信息"""
        cls.get_logger(logger_name).debug(message)
    
    @classmethod
    def exception(cls, message: str, logger_name: str = "mnr-law-crawler"):
        """记录异常（自动包含堆栈跟踪）"""
        cls.get_logger(logger_name).exception(message)
    
    @classmethod
    def get_gui_logger(cls, text_widget, level: str = "INFO") -> logging.Logger:
        """获取GUI日志记录器（输出到文本组件）
        
        Args:
            text_widget: Tkinter Text组件
            level: 日志级别
            
        Returns:
            日志记录器
        """
        logger = logging.getLogger("gui")
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        logger.handlers.clear()
        logger.propagate = False
        
        class TextHandler(logging.Handler):
            """自定义处理器，输出到Tkinter Text组件"""
            
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                def append():
                    try:
                        self.text_widget.insert("end", msg + '\n')
                        self.text_widget.see("end")
                        # 限制日志行数，避免内存占用过大
                        lines = int(self.text_widget.index('end-1c').split('.')[0])
                        if lines > 10000:
                            self.text_widget.delete('1.0', '5000.0')
                    except Exception:
                        pass  # 忽略GUI更新错误
                
                # 使用after确保线程安全
                if hasattr(self.text_widget, 'after'):
                    self.text_widget.after(0, append)
        
        handler = TextHandler(text_widget)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')  # GUI只显示消息，不显示时间戳等
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    @classmethod
    def get_failure_logger(cls, log_dir: Optional[str] = None) -> logging.Logger:
        """获取失败日志记录器（专门记录爬取失败的政策）
        
        Args:
            log_dir: 日志目录（如果为None，使用默认目录）
            
        Returns:
            失败日志记录器
        """
        logger_name = "crawler-failures"
        
        if logger_name in cls._loggers:
            return cls._loggers[logger_name]
        
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.propagate = False
        
        # 确定日志文件路径
        if log_dir is None:
            log_dir = cls._default_log_dir
        else:
            log_dir = Path(log_dir)
        
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"failures_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 文件处理器（带轮转）
        file_handler = RotatingFileHandler(
            str(log_file),
            encoding='utf-8',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10  # 保留更多备份
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        cls._loggers[logger_name] = logger
        return logger
    
    @classmethod
    def log_failed_policy(
        cls,
        title: str,
        link: str,
        reason: str,
        pub_date: str = "",
        doc_number: str = "",
        log_dir: Optional[str] = None
    ):
        """记录失败的政策
        
        Args:
            title: 政策标题
            link: 政策链接
            reason: 失败原因
            pub_date: 发布日期
            doc_number: 发文字号
            log_dir: 日志目录
        """
        failure_logger = cls.get_failure_logger(log_dir)
        message = f"标题: {title} | 链接: {link} | 发布日期: {pub_date} | 发文字号: {doc_number} | 失败原因: {reason}"
        failure_logger.info(message)
