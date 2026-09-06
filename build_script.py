import sys
import os
import PyInstaller.__main__

APP_VERSION = "V1.5"  # 20260906 192644 版本升级至 V1.5
BUILD_DATE = "20260906"  # 20260906 192644 构建日期更新为 20260906
BUILD_NAME = f"DirCopyTool_{BUILD_DATE}_{APP_VERSION}"

def check_dependencies():
    """检查必要的依赖库是否已安装"""
    try:
        import docx
        print("✅ python-docx 库已安装")
    except ImportError:
        print("⚠️  警告：python-docx 库未安装，DOCX导出功能可能无法正常工作")
        print("   请运行: pip install python-docx>=0.8.11")
        response = input("是否继续打包？(y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    try:
        import xlsxwriter
        print("✅ XlsxWriter 库已安装")  # 20260402 102700 增加xlsx导出依赖检查
    except ImportError:
        print("⚠️  警告：XlsxWriter 库未安装，XLSX导出功能可能无法正常工作")  # 20260402 102700 增加xlsx导出依赖检查
        print("   请运行: pip install XlsxWriter")
        response = input("是否继续打包？(y/n): ")
        if response.lower() != 'y':
            sys.exit(1)

def build_exe():
    print(f"=== DirTreeCopy {APP_VERSION} 打包脚本 ===")
    print("检查依赖和文件...")
    
    # 检查依赖库
    check_dependencies()
    
    # 检查必要文件是否存在
    if not os.path.exists('main_app.py'):
        print("❌ 错误：找不到 main_app.py 文件")
        sys.exit(1)
    else:
        print("✅ main_app.py 文件存在")
    
    if not os.path.exists('app_icon.ico'):
        print("⚠️  警告：找不到 app_icon.ico 文件，将使用默认图标")
        icon_param = []
    else:
        print("✅ app_icon.ico 文件存在")
        icon_param = ['--icon=app_icon.ico']
    
    params = [
        'main_app.py',
        f'--name={BUILD_NAME}',
        '--noconsole',
        '--onefile',
        '--clean',
        '--windowed',
        # 排除不需要的模块以减小体积
        '--exclude-module=PIL',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=IPython',
        '--exclude-module=jupyter',
        # 包含python-docx相关模块（确保DOCX功能正常）
        '--hidden-import=docx',
        '--hidden-import=docx.shared',
        '--hidden-import=docx.enum.text',
        '--hidden-import=docx.oxml.shared',
        '--hidden-import=lxml',  # python-docx的依赖
        '--hidden-import=xlsxwriter',  # 20260402 102700 确保XLSX导出依赖被打包进EXE
    ] + icon_param
    
    print("\n=== 打包配置 ===")
    print(f"目标文件: {BUILD_NAME}.exe")
    print(f"打包模式: 单文件模式 (--onefile)")
    print(f"窗口模式: 无控制台窗口 (--windowed)")
    print(f"图标文件: {'已包含' if icon_param else '使用默认'}")
    print(f"DOCX支持: 已包含 python-docx 相关模块")
    
    try:
        print("\n🚀 开始打包...")
        PyInstaller.__main__.run(params)
        
        # 检查生成的文件
        exe_path = os.path.join('dist', f'{BUILD_NAME}.exe')
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"\n✅ 打包完成！")
            print(f"📁 输出文件: {exe_path}")
            print(f"📊 文件大小: {file_size:.1f} MB")
            print(f"\n🎉 DirTreeCopy {APP_VERSION} 已成功打包！")
            print(f"   支持功能: 10种导出格式 + DOCX超链接")  # 20260402 102700 更新导出格式数量说明
        else:
            print("⚠️  打包完成，但未找到输出文件")
            
    except Exception as e:
        print(f"❌ 打包失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
