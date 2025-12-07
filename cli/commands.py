"""
命令行命令模块
"""

import argparse
from typing import List

from core import Config, PolicyCrawler
from utils import Logger


class CLI:
    """命令行界面类"""
    
    def __init__(self):
        """初始化CLI"""
        self.config = Config()
        self.logger = Logger.get_logger(level=self.config.get("log_level", "INFO"))
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """创建参数解析器"""
        parser = argparse.ArgumentParser(
            description='MNR Law Crawler (自然资源部法规爬虫工具) v2.0 - 命令行版',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  # 爬取单个政策（测试模式，获取第一条政策）
  python main.py crawl

  # 使用关键词搜索
  python main.py batch --keywords "土地 规划"

  # 指定日期范围
  python main.py batch --start-date "2024-01-01" --end-date "2024-12-31"

  # 指定输出目录
  python main.py batch --output my_data

  # 使用代理
  python main.py batch --proxy --kuaidaili-key "key:secret"

  # 查看配置
  python main.py config --show

  # 修改配置
  python main.py config --set request_delay=3

  # 重置配置
  python main.py config --reset
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='子命令')
        
        # crawl命令
        crawl_parser = subparsers.add_parser('crawl', help='爬取单个政策（测试模式）')
        crawl_parser.add_argument('--keywords', type=str, default=None, help='关键词（多个用空格分隔）')
        crawl_parser.add_argument('--start-date', type=str, default=None, help='起始日期 (YYYY-MM-DD)')
        crawl_parser.add_argument('--end-date', type=str, default=None, help='结束日期 (YYYY-MM-DD)')
        crawl_parser.add_argument('--output', type=str, default=None, help='输出目录')
        crawl_parser.add_argument('--proxy', action='store_true', help='启用代理')
        crawl_parser.add_argument('--kuaidaili-key', type=str, default=None, help='快代理API密钥')
        
        # batch命令
        batch_parser = subparsers.add_parser('batch', help='批量爬取政策')
        batch_parser.add_argument('--keywords', type=str, default=None, help='关键词（多个用空格分隔）')
        batch_parser.add_argument('--start-date', type=str, default=None, help='起始日期 (YYYY-MM-DD)')
        batch_parser.add_argument('--end-date', type=str, default=None, help='结束日期 (YYYY-MM-DD)')
        batch_parser.add_argument('--output', type=str, default=None, help='输出目录')
        batch_parser.add_argument('--proxy', action='store_true', help='启用代理')
        batch_parser.add_argument('--kuaidaili-key', type=str, default=None, help='快代理API密钥')
        batch_parser.add_argument('--limit', type=int, default=None, help='限制爬取数量')
        
        # config命令
        config_parser = subparsers.add_parser('config', help='配置管理')
        config_group = config_parser.add_mutually_exclusive_group(required=True)
        config_group.add_argument('--show', action='store_true', help='显示当前配置')
        config_group.add_argument('--set', type=str, help='设置配置项 (格式: key=value)')
        config_group.add_argument('--reset', action='store_true', help='重置为默认配置')
        
        # version命令
        subparsers.add_parser('version', help='显示版本信息')
        
        return parser
    
    def run(self, args: List[str] = None):
        """运行CLI"""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return
        
        if parsed_args.command == 'crawl':
            self._crawl_single(parsed_args)
        elif parsed_args.command == 'batch':
            self._crawl_batch(parsed_args)
        elif parsed_args.command == 'config':
            self._manage_config(parsed_args)
        elif parsed_args.command == 'version':
            self._show_version()
    
    def _crawl_single(self, args):
        """爬取单个政策"""
        print("="*60)
        print("爬取单个政策（测试模式）")
        print("="*60)
        
        # 解析关键词
        keywords = []
        if args.keywords:
            keywords = [kw.strip() for kw in args.keywords.split() if kw.strip()]
        
        if args.output:
            self.config.set("output_dir", args.output)
        if args.proxy:
            self.config.set("use_proxy", True)
        if args.kuaidaili_key:
            self.config.set("kuaidaili_api_key", args.kuaidaili_key)
            self.config.set("use_proxy", True)
        
        crawler = PolicyCrawler(self.config, progress_callback=self._print_progress)
        
        def progress_callback(msg):
            print(msg)
        
        try:
            print("\n[测试模式] 获取第一页政策列表...")
            policies = crawler.search_all_policies(
                keywords=keywords,
                start_date=args.start_date,
                end_date=args.end_date,
                callback=progress_callback
            )
            
            if not policies or len(policies) == 0:
                print("[X] 未找到政策")
                return
            
            print(f"获取到 {len(policies)} 条政策")
            
            policy = policies[0]
            print(f"\n选择政策: {policy.title}")
            print(f"ID: {policy.id}")
            
            success = crawler.crawl_single_policy(policy, progress_callback)
            
            if success:
                print("\n[OK] 爬取成功！")
            else:
                print("\n[X] 爬取失败")
        
        except KeyboardInterrupt:
            print("\n\n用户中断")
        except Exception as e:
            print(f"\n\n发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            crawler.close()
    
    def _crawl_batch(self, args):
        """批量爬取政策"""
        print("="*60)
        print("批量爬取政策")
        print("="*60)
        
        # 解析关键词
        keywords = []
        if args.keywords:
            keywords = [kw.strip() for kw in args.keywords.split() if kw.strip()]
        
        if args.output:
            self.config.set("output_dir", args.output)
        if args.proxy:
            self.config.set("use_proxy", True)
        if args.kuaidaili_key:
            self.config.set("kuaidaili_api_key", args.kuaidaili_key)
            self.config.set("use_proxy", True)
        
        crawler = PolicyCrawler(self.config, progress_callback=self._print_progress)
        
        def progress_callback(msg):
            print(msg)
        
        try:
            if args.limit:
                print(f"\n[测试模式] 限制爬取数量: {args.limit}")
                all_policies = crawler.search_all_policies(
                    keywords=keywords,
                    start_date=args.start_date,
                    end_date=args.end_date,
                    callback=progress_callback
                )
                all_policies = all_policies[:args.limit]
                
                crawler.progress.total_count = len(all_policies)
                for i, policy in enumerate(all_policies, 1):
                    print(f"\n进度: [{i}/{len(all_policies)}]")
                    success = crawler.crawl_single_policy(policy, progress_callback)
                    
                    if success:
                        crawler.progress.completed_count += 1
                    else:
                        crawler.progress.failed_count += 1
            else:
                crawler.crawl_batch(
                    keywords=keywords,
                    start_date=args.start_date,
                    end_date=args.end_date,
                    callback=progress_callback
                )
            
            print("\n[OK] 批量爬取完成！")
        
        except KeyboardInterrupt:
            print("\n\n用户中断")
        except Exception as e:
            print(f"\n\n发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            crawler.close()
    
    def _manage_config(self, args):
        """管理配置"""
        if args.show:
            print("="*60)
            print("当前配置")
            print("="*60)
            for key, value in self.config.config.items():
                print(f"{key}: {value}")
        
        elif args.set:
            try:
                key, value = args.set.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit():
                    value = float(value)
                
                self.config.set(key, value)
                self.config.save()
                print(f"[OK] 已设置: {key} = {value}")
            
            except Exception as e:
                print(f"[X] 设置失败: {e}")
        
        elif args.reset:
            confirm = input("确认重置为默认配置？(y/N): ")
            if confirm.lower() == 'y':
                self.config.reset()
                print("[OK] 配置已重置")
            else:
                print("[取消] 未进行重置")
    
    def _show_version(self):
        """显示版本信息"""
        print("="*60)
        print("MNR Law Crawler (自然资源部法规爬虫工具)")
        print("="*60)
        print("版本: 2.0.0")
        print("项目名: mnr-law-crawler")
        print("作者: ViVi141")
        print("GitHub: https://github.com/ViVi141/mnr-law-crawler")
        print("邮箱: 747384120@qq.com")
        print("描述: GUI和命令行二合一的政策爬虫工具")
        print("")
        print("支持功能:")
        print("  - 单个政策爬取")
        print("  - 批量政策爬取")
        print("  - DOCX/DOC/PDF转Markdown")
        print("  - RAG知识库格式生成")
        print("  - 代理IP支持")
        print("  - GUI图形界面")
        print("="*60)
    
    def _print_progress(self, progress):
        """打印进度信息"""
        if progress.total_count > 0:
            percentage = progress.progress_percentage
            print(f"\r进度: {percentage:.1f}% ({progress.completed_count + progress.failed_count}/{progress.total_count})", end='', flush=True)

