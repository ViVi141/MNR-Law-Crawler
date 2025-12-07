#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MNR Law Crawler (自然资源部法规爬虫工具) v2.0 - 统一入口
GUI和命令行二合一版本
"""

import sys

# 设置控制台编码为UTF-8（Windows）
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def main():
    """主函数"""
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 命令行模式
        from cli import CLI
        cli = CLI()
        cli.run()
    else:
        # GUI模式
        try:
            from gui import MainWindow
            app = MainWindow()
            app.run()
        except ImportError as e:
            print(f"GUI模块加载失败: {e}")
            print("\n可能缺少依赖库，尝试安装: pip install -r requirements.txt")
            print("\n或使用命令行模式: python main.py --help")
            sys.exit(1)


if __name__ == "__main__":
    main()

