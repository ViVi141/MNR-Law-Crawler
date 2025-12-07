"""
爬取配置选项卡
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Callable

from core import Config


class CrawlTab:
    """爬取配置选项卡"""
    
    def __init__(
        self,
        parent,
        config: Config,
        start_callback: Callable,
        stop_callback: Callable
    ):
        """初始化"""
        self.config = config
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        
        self.frame = ttk.Frame(parent, padding="12")
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 数据源选择
        source_frame = ttk.LabelFrame(self.frame, text="数据源选择（至少选择一个）", padding="10")
        source_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        data_sources = self.config.get("data_sources", [])
        if not data_sources:
            # 如果没有配置数据源列表，使用默认配置（向后兼容）
            data_sources = [
                {
                    "name": "政府信息公开平台",
                    "base_url": self.config.get("base_url", "https://gi.mnr.gov.cn/"),
                    "search_api": self.config.get("search_api", "https://search.mnr.gov.cn/was5/web/search"),
                    "channel_id": self.config.get("channel_id", "216640"),
                    "enabled": True
                },
                {
                    "name": "政策法规库",
                    "base_url": "https://f.mnr.gov.cn/",
                    "search_api": "https://search.mnr.gov.cn/was5/web/search",
                    "channel_id": "174757",
                    "enabled": False
                }
            ]
        
        # 确保所有数据源都有完整的配置信息
        for ds in data_sources:
            if "search_api" not in ds:
                ds["search_api"] = self.config.get("search_api", "https://search.mnr.gov.cn/was5/web/search")
            if "ajax_api" not in ds:
                ds["ajax_api"] = self.config.get("ajax_api", "https://search.mnr.gov.cn/was/ajaxdata_jsonp.jsp")
            if "channel_id" not in ds:
                ds["channel_id"] = self.config.get("channel_id", "216640")
        
        self.data_source_vars = {}
        for idx, ds in enumerate(data_sources):
            var = tk.BooleanVar(value=ds.get("enabled", True))
            ds_name = ds.get("name", f"数据源{idx+1}")
            self.data_source_vars[ds_name] = var
            ttk.Checkbutton(
                source_frame,
                text=ds_name + f" ({ds.get('base_url', '')})",
                variable=var
            ).grid(row=idx, column=0, sticky="w", padx=5, pady=2)
        
        # 提示标签
        ttk.Label(
            source_frame,
            text="提示：至少选择一个数据源，多个数据源将按顺序执行",
            font=("", 8),
            foreground="gray"
        ).grid(row=len(data_sources), column=0, sticky="w", padx=5, pady=(5, 0))
        
        mode_frame = ttk.LabelFrame(self.frame, text="爬取模式", padding="10")
        mode_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        self.crawl_mode = tk.StringVar(value="single")
        
        ttk.Radiobutton(
            mode_frame,
            text="爬取单个政策（测试）",
            variable=self.crawl_mode,
            value="single",
            command=self._on_mode_change
        ).grid(row=0, column=0, sticky="w", padx=5)
        
        ttk.Radiobutton(
            mode_frame,
            text="批量爬取所有政策",
            variable=self.crawl_mode,
            value="batch",
            command=self._on_mode_change
        ).grid(row=0, column=1, sticky="w", padx=5)
        
        search_frame = ttk.LabelFrame(self.frame, text="搜索条件", padding="10")
        search_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        ttk.Label(search_frame, text="关键词:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.keywords = tk.StringVar(value="")
        ttk.Entry(
            search_frame,
            textvariable=self.keywords,
            width=50
        ).grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        ttk.Label(search_frame, text="(多个关键词用空格分隔)", font=("", 8)).grid(row=0, column=2, sticky="w", padx=6, pady=6)
        
        ttk.Label(search_frame, text="起始日期:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.start_date = tk.StringVar(value="")
        ttk.Entry(
            search_frame,
            textvariable=self.start_date,
            width=20
        ).grid(row=1, column=1, sticky="w", padx=6, pady=6)
        ttk.Label(search_frame, text="(格式: YYYY-MM-DD，留空表示不限制)", font=("", 8)).grid(row=1, column=2, sticky="w", padx=6, pady=6)
        
        ttk.Label(search_frame, text="结束日期:").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        self.end_date = tk.StringVar(value="")
        ttk.Entry(
            search_frame,
            textvariable=self.end_date,
            width=20
        ).grid(row=2, column=1, sticky="w", padx=6, pady=6)
        ttk.Label(search_frame, text="(格式: YYYY-MM-DD，留空表示不限制)", font=("", 8)).grid(row=2, column=2, sticky="w", padx=6, pady=6)
        
        search_frame.columnconfigure(1, weight=1)
        
        output_frame = ttk.LabelFrame(self.frame, text="输出设置", padding="10")
        output_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        ttk.Label(output_frame, text="输出目录:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        
        self.output_dir = tk.StringVar(value=self.config.get("output_dir", "crawled_data"))
        
        ttk.Entry(
            output_frame,
            textvariable=self.output_dir,
            width=50
        ).grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        
        ttk.Button(
            output_frame,
            text="浏览...",
            command=self._browse_output_dir,
            width=12
        ).grid(row=0, column=2, padx=(6, 0), pady=6)
        
        output_frame.columnconfigure(1, weight=1)
        
        download_frame = ttk.LabelFrame(self.frame, text="文件下载选项", padding="10")
        download_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        self.download_docx = tk.BooleanVar(value=self.config.get("download_docx", True))
        self.download_doc = tk.BooleanVar(value=self.config.get("download_doc", True))
        self.download_pdf = tk.BooleanVar(value=self.config.get("download_pdf", False))
        self.download_all_files = tk.BooleanVar(value=self.config.get("download_all_files", False))
        
        self.download_docx_check = ttk.Checkbutton(
            download_frame,
            text="下载DOCX文件",
            variable=self.download_docx,
            command=self._on_download_option_change
        )
        self.download_docx_check.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.download_doc_check = ttk.Checkbutton(
            download_frame,
            text="下载DOC文件",
            variable=self.download_doc,
            command=self._on_download_option_change
        )
        self.download_doc_check.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        self.download_pdf_check = ttk.Checkbutton(
            download_frame,
            text="下载PDF文件",
            variable=self.download_pdf,
            command=self._on_download_option_change
        )
        self.download_pdf_check.grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        self.download_all_files_check = ttk.Checkbutton(
            download_frame,
            text="下载所有形式的附件",
            variable=self.download_all_files,
            command=self._on_download_all_change
        )
        self.download_all_files_check.grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=(8, 2))
        
        if self.download_all_files.get():
            self._on_download_all_change()
        
        proxy_frame = ttk.LabelFrame(self.frame, text="代理设置（可选）", padding="10")
        proxy_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        self.use_proxy = tk.BooleanVar(value=self.config.get("use_proxy", False))
        
        ttk.Checkbutton(
            proxy_frame,
            text="启用代理IP（快代理）",
            variable=self.use_proxy,
            command=self._on_proxy_toggle
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        ttk.Label(proxy_frame, text="Secret ID:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        
        kuaidaili_key = self.config.get("kuaidaili_api_key", "")
        secret_id = ""
        secret_key = ""
        if kuaidaili_key and ":" in kuaidaili_key:
            parts = kuaidaili_key.split(":", 1)
            secret_id = parts[0] if len(parts) > 0 else ""
            secret_key = parts[1] if len(parts) > 1 else ""
        
        self.kuaidaili_secret_id = tk.StringVar(value=secret_id)
        
        self.secret_id_entry = ttk.Entry(
            proxy_frame,
            textvariable=self.kuaidaili_secret_id,
            width=50
        )
        self.secret_id_entry.grid(row=1, column=1, sticky="ew", padx=6, pady=4)
        self.secret_id_entry.config(state="disabled" if not self.use_proxy.get() else "normal")
        
        ttk.Label(proxy_frame, text="Secret Key:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        
        self.kuaidaili_secret_key = tk.StringVar(value=secret_key)
        
        self.secret_key_entry = ttk.Entry(
            proxy_frame,
            textvariable=self.kuaidaili_secret_key,
            width=50,
            show="*"
        )
        self.secret_key_entry.grid(row=2, column=1, sticky="ew", padx=6, pady=4)
        self.secret_key_entry.config(state="disabled" if not self.use_proxy.get() else "normal")
        
        proxy_frame.columnconfigure(1, weight=1)
        
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(
            button_frame,
            text="开始爬取",
            command=self._on_start,
            width=14
        )
        self.start_button.grid(row=0, column=0, padx=(0, 12))
        
        self.stop_button = ttk.Button(
            button_frame,
            text="停止爬取",
            command=self._on_stop,
            width=14,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=0)
        
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
    
    def _on_mode_change(self):
        """爬取模式改变事件"""
        pass  # 自然资源部爬虫不需要特殊处理
    
    def _on_proxy_toggle(self):
        """代理开关切换事件"""
        if self.use_proxy.get():
            self.secret_id_entry.config(state="normal")
            self.secret_key_entry.config(state="normal")
        else:
            self.secret_id_entry.config(state="disabled")
            self.secret_key_entry.config(state="disabled")
    
    def _on_download_all_change(self):
        """下载所有文件选项改变事件"""
        if self.download_all_files.get():
            self.download_docx_check.config(state="disabled")
            self.download_doc_check.config(state="disabled")
            self.download_pdf_check.config(state="disabled")
        else:
            self.download_docx_check.config(state="normal")
            self.download_doc_check.config(state="normal")
            self.download_pdf_check.config(state="normal")
    
    def _on_download_option_change(self):
        """文件类型选项改变事件"""
        if self.download_docx.get() or self.download_doc.get() or self.download_pdf.get():
            if self.download_all_files.get():
                self.download_all_files.set(False)
                self._on_download_all_change()
    
    def _browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.output_dir.get()
        )
        if directory:
            self.output_dir.set(directory)
    
    def _on_start(self):
        """开始爬取按钮点击事件"""
        import tkinter.messagebox as messagebox
        
        # 保存数据源选择
        data_sources = self.config.get("data_sources", [])
        if not data_sources:
            # 如果没有配置数据源列表，使用默认配置（向后兼容）
            data_sources = [{
                "name": "政府信息公开平台",
                "base_url": self.config.get("base_url", "https://gi.mnr.gov.cn/"),
                "search_api": self.config.get("search_api", "https://search.mnr.gov.cn/was5/web/search"),
                "channel_id": self.config.get("channel_id", "216640"),
                "enabled": True
            }]
        
        # 更新数据源的启用状态
        enabled_count = 0
        for ds in data_sources:
            ds_name = ds.get("name", "")
            if ds_name in self.data_source_vars:
                ds["enabled"] = self.data_source_vars[ds_name].get()
                if ds["enabled"]:
                    enabled_count += 1
        
        # 验证至少选择一个数据源
        if enabled_count == 0:
            messagebox.showerror("错误", "请至少选择一个数据源！")
            return
        
        self.config.set("data_sources", data_sources)
        
        # 显示选中的数据源信息（仅在多个数据源时显示）
        enabled_sources = [ds.get("name") for ds in data_sources if ds.get("enabled", False)]
        if len(enabled_sources) > 1:
            # 不显示弹窗，只在日志中提示，避免打断用户操作
            pass  # 信息会在爬取过程中通过callback显示
        
        # 解析关键词
        keywords_str = self.keywords.get().strip()
        keywords = [kw.strip() for kw in keywords_str.split() if kw.strip()] if keywords_str else []
        
        # 验证日期格式
        start_date = self.start_date.get().strip()
        end_date = self.end_date.get().strip()
        
        if start_date:
            try:
                from datetime import datetime
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("错误", "起始日期格式错误，请使用 YYYY-MM-DD 格式")
                return
        
        if end_date:
            try:
                from datetime import datetime
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("错误", "结束日期格式错误，请使用 YYYY-MM-DD 格式")
                return
        
        crawl_type = self.crawl_mode.get()
        
        kuaidaili_api_key = ""
        if self.use_proxy.get():
            secret_id = self.kuaidaili_secret_id.get().strip()
            secret_key = self.kuaidaili_secret_key.get().strip()
            if secret_id and secret_key:
                kuaidaili_api_key = f"{secret_id}:{secret_key}"
        
        kwargs = {
            "output_dir": self.output_dir.get(),
            "keywords": keywords,
            "start_date": start_date if start_date else None,
            "end_date": end_date if end_date else None,
            "download_docx": self.download_docx.get(),
            "download_doc": self.download_doc.get(),
            "download_pdf": self.download_pdf.get(),
            "download_all_files": self.download_all_files.get(),
            "use_proxy": self.use_proxy.get(),
            "kuaidaili_api_key": kuaidaili_api_key
        }
        
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        self.start_callback(crawl_type, **kwargs)
    
    def _on_stop(self):
        """停止爬取按钮点击事件"""
        self.stop_callback()
        
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

