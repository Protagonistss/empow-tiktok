"""Apify数据集成工具 - 快速设置脚本

这个脚本帮助用户快速配置环境和验证安装。
"""

import os
import sys
from pathlib import Path
import subprocess


def print_banner():
    """打印横幅"""
    print("🚀 Apify数据集成工具 - 快速设置")
    print("="*50)


def check_python_version():
    """检查Python版本"""
    print("\n📋 检查Python环境...")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    else:
        print("✅ Python版本符合要求")
        return True


def check_dependencies():
    """检查依赖包"""
    print("\n📦 检查依赖包...")
    required_packages = [
        'apify-client',
        'requests', 
        'python-dotenv',
        'pydantic',
        'loguru'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (未安装)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 安装缺失的包:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ 所有依赖包已安装")
        return True


def check_project_structure():
    """检查项目结构"""
    print("\n📁 检查项目结构...")
    
    required_dirs = ['src', 'data', 'logs']
    required_files = [
        'src/__init__.py',
        'src/config.py', 
        'src/apify_service.py',
        'src/task_manager.py',
        'src/core.py',
        'main.py',
        '.env.example'
    ]
    
    # 检查目录
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ (缺失)")
            Path(dir_name).mkdir(exist_ok=True)
            print(f"   已创建目录: {dir_name}/")
    
    # 检查文件
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (缺失)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  缺失 {len(missing_files)} 个文件")
        return False
    else:
        print("✅ 项目结构完整")
        return True


def setup_env_file():
    """设置环境文件"""
    print("\n🔧 配置环境文件...")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✅ .env文件已存在")
        
        # 检查是否包含API Token
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'APIFY_API_TOKEN=' in content and not content.count('APIFY_API_TOKEN=\n'):
                print("✅ API Token已配置")
                return True
            else:
                print("⚠️  API Token未配置")
    else:
        if env_example.exists():
            # 复制示例文件
            with open(env_example, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ 已创建.env文件（基于.env.example）")
        else:
            # 创建基本的.env文件
            basic_env = """# Apify API配置
APIFY_API_TOKEN=your_apify_api_token_here
APIFY_BASE_URL=https://api.apify.com/v2
APIFY_TIMEOUT=30
APIFY_MAX_RETRIES=3

# 应用配置
APP_DEBUG=false
APP_LOG_LEVEL=INFO
APP_DATA_DIR=./data
"""
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(basic_env)
            print("✅ 已创建基本.env文件")
    
    print("\n💡 请编辑.env文件，设置你的APIFY_API_TOKEN")
    print("   获取API Token: https://console.apify.com/account/integrations")
    return False


def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 测试基本功能...")
    
    try:
        # 添加src到路径
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        # 测试导入
        from src.config import config_manager
        from src.core import apify_integration
        
        print("✅ 模块导入成功")
        
        # 测试配置
        validation = config_manager.validate_config()
        if validation['app_configured']:
            print("✅ 应用配置正常")
        else:
            print("❌ 应用配置异常")
        
        if validation['apify_configured']:
            print("✅ Apify配置正常")
            
            # 测试连接
            status = apify_integration.get_status()
            if status['client_ready']:
                print("✅ Apify客户端连接成功")
                return True
            else:
                print("❌ Apify客户端连接失败")
        else:
            print("⚠️  Apify配置未完成（需要API Token）")
        
        return False
        
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False


def show_next_steps(all_good=False):
    """显示后续步骤"""
    print("\n🎯 后续步骤:")
    
    if all_good:
        print("✅ 环境配置完成！你可以:")
        print("   1. python main.py          # 运行主程序")
        print("   2. python example.py       # 查看使用示例")
        print("   3. 开始开发你的数据获取脚本")
    else:
        print("⚠️  还需要完成以下步骤:")
        print("   1. 编辑.env文件，设置APIFY_API_TOKEN")
        print("   2. 运行 python setup.py 重新检查")
        print("   3. 运行 python main.py 测试功能")
    
    print("\n📚 文档和帮助:")
    print("   - README.md        # 项目说明")
    print("   - .env.example     # 环境变量模板")
    print("   - src/             # 源码目录")


def main():
    """主函数"""
    print_banner()
    
    # 执行检查
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("项目结构", check_project_structure),
        ("环境配置", setup_env_file),
        ("基本功能", test_basic_functionality)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {name}检查失败: {e}")
            results.append(False)
    
    # 总结
    print("\n📊 检查结果:")
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有检查通过！")
        show_next_steps(True)
    else:
        print("⚠️  部分检查未通过")
        show_next_steps(False)


if __name__ == "__main__":
    main()