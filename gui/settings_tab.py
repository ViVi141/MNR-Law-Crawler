"""
设置选项卡
"""

import tkinter as tk
from tkinter import ttk, messagebox

from core import Config


class SettingsTab:
    """设置选项卡"""
    
    def __init__(self, parent, config: Config):
        """初始化"""
        self.config = config
        
        self.frame = ttk.Frame(parent, padding="10")
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        request_frame = ttk.LabelFrame(self.frame, text="请求设置", padding="8")
        request_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        request_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        ttk.Label(request_frame, text="请求延迟(秒):").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.request_delay = tk.StringVar(value=str(self.config.get("request_delay", 2)))
        ttk.Entry(request_frame, textvariable=self.request_delay, width=12).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        ttk.Label(request_frame, text="重试延迟(秒):").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.retry_delay = tk.StringVar(value=str(self.config.get("retry_delay", 5)))
        ttk.Entry(request_frame, textvariable=self.retry_delay, width=12).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        ttk.Label(request_frame, text="最大重试次数:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.max_retries = tk.StringVar(value=str(self.config.get("max_retries", 3)))
        ttk.Entry(request_frame, textvariable=self.max_retries, width=12).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        ttk.Label(request_frame, text="限流延迟(秒):").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.rate_limit_delay = tk.StringVar(value=str(self.config.get("rate_limit_delay", 30)))
        ttk.Entry(request_frame, textvariable=self.rate_limit_delay, width=12).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        ttk.Label(request_frame, text="超时时间(秒):").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.timeout = tk.StringVar(value=str(self.config.get("timeout", 30)))
        ttk.Entry(request_frame, textvariable=self.timeout, width=12).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        
        crawl_frame = ttk.LabelFrame(self.frame, text="爬取设置", padding="8")
        crawl_frame.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        crawl_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        ttk.Label(crawl_frame, text="每页数量:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.page_size = tk.StringVar(value=str(self.config.get("page_size", 20)))
        ttk.Entry(crawl_frame, textvariable=self.page_size, width=12).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1
        
        ttk.Label(crawl_frame, text="会话轮换间隔:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.session_rotate_interval = tk.StringVar(value=str(self.config.get("session_rotate_interval", 50)))
        ttk.Entry(crawl_frame, textvariable=self.session_rotate_interval, width=12).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        
        output_frame = ttk.LabelFrame(self.frame, text="输出设置", padding="8")
        output_frame.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        
        self.save_json = tk.BooleanVar(value=self.config.get("save_json", True))
        self.save_markdown = tk.BooleanVar(value=self.config.get("save_markdown", True))
        self.save_docx = tk.BooleanVar(value=self.config.get("save_docx", True))
        self.save_files = tk.BooleanVar(value=self.config.get("save_files", True))
        
        ttk.Checkbutton(output_frame, text="保存JSON数据", variable=self.save_json).grid(row=0, column=0, sticky="w", padx=5, pady=3)
        ttk.Checkbutton(output_frame, text="保存Markdown文件", variable=self.save_markdown).grid(row=1, column=0, sticky="w", padx=5, pady=3)
        ttk.Checkbutton(output_frame, text="保存DOCX文件", variable=self.save_docx).grid(row=2, column=0, sticky="w", padx=5, pady=3)
        ttk.Checkbutton(output_frame, text="保存附件文件", variable=self.save_files).grid(row=3, column=0, sticky="w", padx=5, pady=3)
        
        log_frame = ttk.LabelFrame(self.frame, text="日志设置", padding="8")
        log_frame.grid(row=3, column=0, sticky="ew", pady=(0, 6))
        log_frame.columnconfigure(1, weight=1)
        
        ttk.Label(log_frame, text="日志级别:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.log_level = tk.StringVar(value=self.config.get("log_level", "INFO"))
        log_combo = ttk.Combobox(
            log_frame,
            textvariable=self.log_level,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=12
        )
        log_combo.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=4, column=0, pady=(12, 0))
        
        ttk.Button(
            button_frame,
            text="保存设置",
            command=self._save_settings,
            width=14
        ).grid(row=0, column=0, padx=(0, 12))
        
        ttk.Button(
            button_frame,
            text="恢复默认",
            command=self._reset_settings,
            width=14
        ).grid(row=0, column=1, padx=0)
        
        self.frame.columnconfigure(0, weight=1)
    
    def _save_settings(self):
        """保存设置"""
        try:
            # 时间相关字段支持小数
            self.config.set("request_delay", float(self.request_delay.get()))
            self.config.set("retry_delay", float(self.retry_delay.get()))
            self.config.set("rate_limit_delay", float(self.rate_limit_delay.get()))
            self.config.set("timeout", float(self.timeout.get()))
            
            # 整数字段
            self.config.set("max_retries", int(self.max_retries.get()))
            self.config.set("page_size", int(self.page_size.get()))
            self.config.set("session_rotate_interval", int(self.session_rotate_interval.get()))
            self.config.set("save_json", self.save_json.get())
            self.config.set("save_markdown", self.save_markdown.get())
            self.config.set("save_docx", self.save_docx.get())
            self.config.set("save_files", self.save_files.get())
            self.config.set("log_level", self.log_level.get())
            
            self.config.save()
            
            messagebox.showinfo("成功", "设置已保存")
        
        except ValueError as e:
            messagebox.showerror("错误", f"设置值无效:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败:\n{str(e)}")
    
    def _reset_settings(self):
        """重置设置"""
        confirm = messagebox.askyesno("确认", "确定要恢复默认设置吗？")
        if confirm:
            self.config.reset()
            
            self.request_delay.set(str(self.config.get("request_delay")))
            self.retry_delay.set(str(self.config.get("retry_delay")))
            self.max_retries.set(str(self.config.get("max_retries")))
            self.rate_limit_delay.set(str(self.config.get("rate_limit_delay")))
            self.timeout.set(str(self.config.get("timeout")))
            self.page_size.set(str(self.config.get("page_size")))
            self.session_rotate_interval.set(str(self.config.get("session_rotate_interval")))
            self.save_json.set(self.config.get("save_json"))
            self.save_markdown.set(self.config.get("save_markdown"))
            self.save_docx.set(self.config.get("save_docx"))
            self.save_files.set(self.config.get("save_files"))
            self.log_level.set(self.config.get("log_level"))
            
            messagebox.showinfo("成功", "设置已恢复为默认值")

