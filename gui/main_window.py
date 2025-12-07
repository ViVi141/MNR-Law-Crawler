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
        self.root.title("MNR Law Crawler (自然资源部法规爬虫工具) v2.0")
        
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
        
        logging.info("欢迎使用 MNR Law Crawler (自然资源部法规爬虫工具) v2.0")
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
                from urllib.parse import urlparse
                
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
                    
                    # 根据数据源分组，获取每个数据源的第一条政策
                    source_policies = {}  # {数据源名称: 第一条政策}
                    
                    # 获取启用的数据源配置
                    data_sources = self.config.get("data_sources", [])
                    enabled_sources = [ds for ds in data_sources if ds.get("enabled", True)]
                    
                    # 为每个数据源找到第一条政策
                    used_policies = set()  # 记录已使用的政策索引，避免重复分配
                    
                    for data_source in enabled_sources:
                        source_name = data_source.get("name", "未知数据源")
                        base_url = data_source.get("base_url", "")
                        
                        # 从base_url提取域名（例如：gi.mnr.gov.cn 或 f.mnr.gov.cn）
                        domain = ""
                        if base_url:
                            try:
                                parsed = urlparse(base_url)
                                domain = parsed.netloc
                                # 如果没有netloc，尝试从path中提取
                                if not domain and parsed.path:
                                    # 移除协议前缀
                                    path = parsed.path.strip('/')
                                    if path:
                                        domain = path.split('/')[0]
                            except (ValueError, AttributeError):
                                domain = ""
                        
                        # 查找该数据源的第一条政策（通过URL域名匹配）
                        matched = False
                        for idx, policy in enumerate(policies):
                            if source_name in source_policies:
                                break  # 已经找到该数据源的第一条政策
                            
                            # 跳过已使用的政策
                            if idx in used_policies:
                                continue
                                
                            policy_url = policy.link or policy.source or policy.url
                            if policy_url and domain:
                                # 检查政策URL是否包含该数据源的域名
                                # 例如：gi.mnr.gov.cn 或 f.mnr.gov.cn
                                if domain in policy_url:
                                    source_policies[source_name] = policy
                                    used_policies.add(idx)
                                    matched = True
                                    logging.info(f"[测试模式] 数据源 '{source_name}' 匹配到政策: {policy.title[:50]}...")
                                    break
                        
                        # 如果通过URL没有匹配到，且该数据源还没有政策，则按顺序分配
                        if not matched and source_name not in source_policies:
                            for idx, policy in enumerate(policies):
                                if idx not in used_policies:
                                    source_policies[source_name] = policy
                                    used_policies.add(idx)
                                    logging.info(f"[测试模式] 数据源 '{source_name}' 按顺序分配政策: {policy.title[:50]}...")
                                    break
                    
                    # 如果仍然没有匹配到任何数据源，使用第一条政策作为默认
                    if not source_policies and policies:
                        source_policies["默认"] = policies[0]
                        logging.warning("[测试模式] 无法匹配数据源，使用默认政策")
                    
                    # 设置进度总数
                    total_count = len(source_policies)
                    self.crawler.progress = CrawlProgress()
                    self.crawler.progress.start_time = datetime.now()
                    self.crawler.progress.total_count = total_count
                    self._update_progress(self.crawler.progress)
                    
                    # 对每个数据源的第一条政策进行爬取
                    completed_count = 0
                    failed_count = 0
                    
                    for source_name, policy in source_policies.items():
                        logging.info(f"\n[测试模式] 爬取数据源 '{source_name}' 的第一条政策: {policy.title}")
                        
                        self.crawler.progress.current_policy_id = policy.id
                        self.crawler.progress.current_policy_title = policy.title
                        self._update_progress(self.crawler.progress)
                        
                        success = self.crawler.crawl_single_policy(policy, progress_callback)
                        
                        if success:
                            completed_count += 1
                            self.crawler.progress.completed_count = completed_count
                            self.crawler.progress.completed_policies.append(policy.id)
                            logging.info(f"[测试模式] 数据源 '{source_name}' 的第一条政策爬取成功")
                        else:
                            failed_count += 1
                            self.crawler.progress.failed_count = failed_count
                            # 失败信息已在crawl_single_policy中记录到失败日志
                            self.crawler.progress.failed_policies.append({
                                'id': policy.id,
                                'title': policy.title,
                                'link': policy.link or policy.source or policy.url,
                                'pub_date': policy.pub_date,
                                'doc_number': policy.doc_number,
                                'reason': f'数据源 {source_name} 爬取失败'
                            })
                            logging.error(f"[测试模式] 数据源 '{source_name}' 的第一条政策爬取失败")
                        
                        self._update_progress(self.crawler.progress)
                    
                    self.crawler.progress.end_time = datetime.now()
                    self._update_progress(self.crawler.progress)
                    
                    if completed_count > 0:
                        self._show_completion(
                            "测试完成", 
                            f"测试模式完成！\n成功: {completed_count} 条\n失败: {failed_count} 条\n\n每个数据源的第一条政策已保存。"
                        )
                    else:
                        self._show_error("测试失败", "所有数据源的政策爬取都失败了，请查看日志")
                else:
                    self._show_error("未找到政策", "没有找到符合条件的政策")
                    self.crawler.progress = CrawlProgress()
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
        from utils.logger import Logger
        
        # 从配置读取日志设置
        log_level = self.config.get("log_level", "INFO")
        log_file = self.config.get("log_file", "crawler.log")
        log_dir = self.config.get("log_dir", "logs")
        
        # 设置文件和控制台日志
        Logger.setup_from_config({
            "log_level": log_level,
            "log_file": log_file,
            "log_dir": log_dir
        })
        
        # 设置GUI日志（输出到文本组件）
        gui_logger = Logger.get_gui_logger(self.log_text, level=log_level)
        
        # 将根logger也输出到GUI
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # 添加GUI处理器到根logger（如果还没有）
        has_gui_handler = any(isinstance(h, logging.Handler) and hasattr(h, 'text_widget') 
                             for h in root_logger.handlers)
        if not has_gui_handler:
            # 复用GUI logger的handler
            for handler in gui_logger.handlers:
                root_logger.addHandler(handler)
    
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

