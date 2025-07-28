#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启梦教育平台启动脚本
"""

import subprocess
import sys
import os

def main():
    """启动应用"""
    print("=" * 50)
    print("启梦教育平台")
    print("=" * 50)
    
    # 检查是否在虚拟环境中
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("建议在虚拟环境中运行此应用")
    
    # 检查依赖
    try:
        import flask
        print("✓ Flask 已安装")
    except ImportError:
        print("✗ Flask 未安装，正在安装依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # 启动应用
    print("\n正在启动应用...")
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n应用已停止")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()