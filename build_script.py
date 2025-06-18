import sys
import os
import PyInstaller.__main__

def build_exe():
    # 检查必要文件是否存在
    if not os.path.exists('main_app.py'):
        print("错误：找不到 main_app.py 文件")
        sys.exit(1)
    
    if not os.path.exists('app_icon.ico'):
        print("警告：找不到 app_icon.ico 文件，将使用默认图标")
        icon_param = []
    else:
        icon_param = ['--icon=app_icon.ico']
    
    params = [
        'main_app.py',
        '--name=DirCopyTool_250618_V1.0',
        '--noconsole',
        '--onefile',
        '--clean',
        '--windowed',
        '--exclude-module=PIL',  # 20250618 如果不使用图像处理
        '--exclude-module=matplotlib',  # 20250618 如果不使用绘图
    ] + icon_param
    
    try:
        print("开始打包...")
        PyInstaller.__main__.run(params)
        print("打包完成！")
    except Exception as e:
        print(f"打包失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()