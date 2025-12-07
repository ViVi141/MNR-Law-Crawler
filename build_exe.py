#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
打包为exe的脚本
"""

import os
import sys
import subprocess
import shutil
from importlib.util import find_spec
from pathlib import Path

def build_exe():
    """使用PyInstaller打包为exe"""
    
    print("=" * 60)
    print("MNR Law Crawler - 打包为EXE")
    print("=" * 60)
    
    # 检查PyInstaller是否安装
    if find_spec("PyInstaller") is not None:
        print("[OK] PyInstaller 已安装")
    else:
        print("[INFO] PyInstaller 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller 安装完成")
    
    # 清理之前的构建文件
    print("\n清理之前的构建文件...")
    for dir_name in ['build', 'dist', '__pycache__']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  已删除: {dir_name}/")
    
    # 清理spec文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"  已删除: {spec_file}")
    
    # PyInstaller命令参数
    cmd = [
        'pyinstaller',
        '--name=MNR-Law-Crawler',
        '--onefile',  # 打包成单个exe文件
        '--windowed',  # 无控制台窗口（GUI模式）
        '--icon=NONE',  # 如果有图标文件可以指定
        '--add-data=config.json.example;.',  # 包含配置文件模板
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=bs4',
        '--hidden-import=requests',
        '--hidden-import=docx',
        '--hidden-import=pypdf',
        '--collect-all=tkinter',  # 收集所有tkinter相关文件
        '--noconfirm',  # 覆盖输出目录而不询问
        'main.py'
    ]
    
    # 如果是Windows，使用分号分隔路径
    if sys.platform == 'win32':
        cmd[5] = '--add-data=config.json.example;.'
    
    print("\n开始打包...")
    print(f"命令: {' '.join(cmd)}")
    print("-" * 60)
    print("提示: 打包过程可能需要几分钟，请耐心等待...")
    print("-" * 60)
    
    try:
        # 执行打包（实时显示输出）
        subprocess.run(cmd, check=True)
        
        print("\n" + "=" * 60)
        print("[OK] 打包完成！")
        print("=" * 60)
        exe_path = 'dist/MNR-Law-Crawler.exe'
        if os.path.exists(exe_path):
            print(f"\n输出文件位置: {exe_path}")
            print(f"文件大小: {os.path.getsize(exe_path) / 1024 / 1024:.2f} MB")
        print("\n提示:")
        print("  1. 首次运行需要 config.json 配置文件")
        print("  2. 可以将 config.json.example 复制为 config.json 并修改")
        print("  3. 建议将exe和config.json放在同一目录下")
        
    except subprocess.CalledProcessError as e:
        print("\n[ERROR] 打包失败！")
        print(f"返回码: {e.returncode}")
        return False
    
    return True

if __name__ == "__main__":
    build_exe()

