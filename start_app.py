#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import pymysql
        import cryptography
        import dotenv
        import requests
        print("✓ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ {str(e)}")
        return False

def install_dependencies():
    """安装依赖"""
    print("正在安装依赖...")
    
    # 使用pip安装依赖
    try:
        # 尝试使用--break-system-packages参数安装
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--break-system-packages"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        try:
            # 如果失败，尝试不使用--break-system-packages参数安装
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"安装依赖失败: {e}")
            print("请尝试手动安装依赖: pip install -r requirements.txt")
            return False
    
    print("依赖安装完成")
    return True

def start_app():
    """启动应用"""
    print("正在启动应用...")
    
    # 检查是否在虚拟环境中
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        print("警告: 未在虚拟环境中运行")
    
    # 尝试启动应用
    try:
        # 使用子进程启动应用，这样可以捕获输出
        process = subprocess.Popen([sys.executable, "run.py"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  text=True,
                                  bufsize=1,
                                  universal_newlines=True)
        
        print("应用已启动，访问 http://localhost:5000")
        print("按 Ctrl+C 停止应用")
        
        # 实时输出应用日志
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # 检查进程是否正常退出
        return_code = process.poll()
        if return_code != 0:
            print(f"应用异常退出，退出码: {return_code}")
            error = process.stderr.read()
            print(f"错误信息: {error}")
            return False
        
        return True
    
    except KeyboardInterrupt:
        print("\n应用已停止")
        return True
    except Exception as e:
        print(f"启动应用失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("启梦教育平台启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        if not install_dependencies():
            print("无法安装依赖，请检查网络连接或手动安装")
            return
    
    # 启动应用
    start_app()

if __name__ == "__main__":
    main()
