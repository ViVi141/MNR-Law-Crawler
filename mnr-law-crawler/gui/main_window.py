"""
主窗口模块
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import threading
import logging
from typing import Optional

from core import Config, PolicyCrawler, CrawlProgress
from .crawl_tab import CrawlTab
from .progress_tab import ProgressTab
from .settings_tab import SettingsTab


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        self.root = tk.Tk()
        self.root.title("MNR Law Crawler (自然资源部法规爬虫工具) v1.0")
        
        # 加载配置
        self.config = Config()
        
        # 设置窗口大小和位置
        window_width = self.config.get("window_width", 1200)
        window_height = self.config.get("window_height", 1000)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        max_width = int(screen_width * 0.8)
        max_height = int(screen_height * 0.8)
        window_width = min(window_width, max_width)
        window_height = min(window_height, max_height)
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.root.minsize(960, 800)
        
        if sys.platform == 'win32':
            default_font = ("Microsoft YaHei UI", 10)
            self.root.option_add("*Font", default_font)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.crawler: Optional[PolicyCrawler] = None
        self.crawl_thread: Optional[threading.Thread] = None
        self.is_crawling = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.root, padding="12")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=3)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        self.crawl_tab = CrawlTab(self.notebook, self.config, self._on_start_crawl, self._on_stop_crawl)
        self.progress_tab = ProgressTab(self.notebook, self.config)
        self.settings_tab = SettingsTab(self.notebook, self.config)
        
        self.notebook.add(self.crawl_tab.frame, text="  爬取配置  ")
        self.notebook.add(self.progress_tab.frame, text="  爬取进度  ")
        self.notebook.add(self.settings_tab.frame, text="  设置  ")
        
        log_frame = ttk.LabelFrame(main_frame, text="日志输出", padding="8")
        log_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=(8, 0))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            wrap=tk.CHAR,
            font=("Consolas", 9) if sys.platform == 'win32' else ("Courier", 9),
            bg="#f8f8f8",
            relief=tk.FLAT,
            borderwidth=1
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        clear_button = ttk.Button(log_frame, text="清空日志", command=self._clear_log, width=12)
        clear_button.grid(row=1, column=0, sticky="e", padx=4, pady=4)
        
        self._setup_logging()
        
        logging.info("欢迎使用 MNR Law Crawler (自然资源部法规爬虫工具) v1.0")
        logging.info("请在\"爬取配置\"选项卡中设置参数，然后点击\"开始爬取\"按钮")
    
    def _on_start_crawl(self, crawl_type: str, **kwargs):
        """开始爬取回调"""
        if self.is_crawling:
            messagebox.showwarning("警告", "爬取任务正在进行中，请等待完成")
            return
        
        self.notebook.select(1)
        
        for key, value in kwargs.items():
            if value is not None:
                self.config.set(key, value)
        
        self.crawler = PolicyCrawler(self.config, progress_callback=self._update_progress)
        
        from core import CrawlProgress
        initial_progress = CrawlProgress()
        self._update_progress(initial_progress)
        
        self.is_crawling = True
        self.crawl_thread = threading.Thread(
            target=self._run_crawl,
            args=(crawl_type,),
            daemon=True
        )
        self.crawl_thread.start()
    
    def _run_crawl(self, crawl_type: str):
        """运行爬取任务"""
        try:
            keywords = self.config.get("keywords", [])
            start_date = self.config.get("start_date")
            end_date = self.config.get("end_date")
            
            def progress_callback(msg):
                """进度回调函数"""
                logging.info(msg)
            
            if crawl_type == 'single':
                from core import CrawlProgress
                from datetime import datetime
                self.crawler.progress = CrawlProgress()
                self.crawler.progress.start_time = datetime.now()
                self.crawler.progress.total_count = 1
                self._update_progress(self.crawler.progress)
                
                logging.info("\n[测试模式] 获取第一页政策列表...")
                policies = self.crawler.search_all_policies(
                    keywords=keywords,
                    start_date=start_date,
                    end_date=end_date,
                    callback=progress_callback,
                    limit_pages=1  # 测试模式只获取第一页
                )
                
                if policies and len(policies) > 0:
                    logging.info(f"获取到 {len(policies)} 条政策")
                    
                    policy = policies[0]
                    logging.info(f"\n选择政策: {policy.title}")
                    
                    self.crawler.progress.current_policy_id = policy.id
                    self.crawler.progress.current_policy_title = policy.title
                    self._update_progress(self.crawler.progress)
                    
                    success = self.crawler.crawl_single_policy(policy, progress_callback)
                    
                    if success:
                        self.crawler.progress.completed_count = 1
                        self.crawler.progress.completed_policies.append(policy.id)
                        self._show_completion("爬取完成", "单个政策爬取成功！")
                    else:
                        self.crawler.progress.failed_count = 1
                        self.crawler.progress.failed_policies.append({
                            'id': policy.id,
                            'title': policy.title,
                            'reason': '爬取失败'
                        })
                        self._show_error("爬取失败", "政策爬取失败，请查看日志")
                    
                    self.crawler.progress.end_time = datetime.now()
                    self._update_progress(self.crawler.progress)
                else:
                    self._show_error("未找到政策", "没有找到符合条件的政策")
                    self.crawler.progress.end_time = datetime.now()
                    self._update_progress(self.crawler.progress)
            
            elif crawl_type == 'batch':
                from core import CrawlProgress
                self.crawler.progress = CrawlProgress()
                
                progress = self.crawler.crawl_batch(
                    keywords=keywords,
                    start_date=start_date,
                    end_date=end_date,
                    callback=progress_callback
                )
                
                self._update_progress(progress)
                
                self._show_completion("爬取完成", f"批量爬取完成！\n成功: {progress.completed_count}\n失败: {progress.failed_count}")
        
        except Exception as e:
            self._show_error("错误", f"爬取过程中发生错误:\n{str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.is_crawling = False
            if self.crawler:
                self.crawler.close()
            
            self.root.after(0, self._restore_button_state)
    
    def _on_stop_crawl(self):
        """停止爬取回调"""
        if not self.is_crawling:
            messagebox.showinfo("提示", "当前没有正在进行的爬取任务")
            return
        
        confirm = messagebox.askyesno("确认", "确定要停止当前爬取任务吗？")
        if confirm:
            self.is_crawling = False
            logging.info("\n用户请求停止爬取任务...")
            
            if self.crawler:
                self.crawler.request_stop()
            
            messagebox.showinfo("提示", "已发送停止信号，等待任务结束...")
    
    def _restore_button_state(self):
        """恢复按钮状态"""
        if hasattr(self, 'crawl_tab'):
            self.crawl_tab.start_button.config(state="normal")
            self.crawl_tab.stop_button.config(state="disabled")
    
    def _update_progress(self, progress: CrawlProgress):
        """更新进度"""
        self.root.after(0, self.progress_tab.update_progress, progress)
    
    def _show_completion(self, title: str, message: str):
        """显示完成消息"""
        self.root.after(0, messagebox.showinfo, title, message)
    
    def _show_error(self, title: str, message: str):
        """显示错误消息"""
        self.root.after(0, messagebox.showerror, title, message)
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        logging.info("日志已清空")
    
    def _setup_logging(self):
        """配置日志系统"""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                    self.text_widget.update_idletasks()
                self.text_widget.after(0, append)
        
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        
        text_handler = TextHandler(self.log_text)
        text_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        text_handler.setFormatter(formatter)
        logger.addHandler(text_handler)
        
        if sys.__stdout__:
            console_handler = logging.StreamHandler(sys.__stdout__)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
    
    def _on_closing(self):
        """窗口关闭事件"""
        if self.is_crawling:
            confirm = messagebox.askyesno(
                "确认退出",
                "爬取任务正在进行中，确定要退出吗？"
            )
            if not confirm:
                return
        
        if hasattr(self, 'progress_tab'):
            self.progress_tab.stop_timer()
        
        if self.crawler:
            self.crawler.close()
        
        self.root.destroy()
    
    def run(self):
        """运行主窗口"""
        self.root.mainloop()

