"""Apify数据集成工具 - 主入口

这是一个用于验证Apify数据对接逻辑的命令行工具。
专注于后端逻辑验证和渐进式开发。
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core import apify_integration
from src.task_manager import TaskStatus
from loguru import logger


def print_banner():
    """打印横幅"""
    print("="*60)
    print("🚀 Apify数据集成工具 - 后端逻辑验证")
    print("📝 专注于渐进式开发和功能验证")
    print("="*60)
    print()


def check_environment():
    """检查环境配置"""
    print("📋 环境检查:")
    
    # 检查.env文件
    env_file = Path(".env")
    if env_file.exists():
        print("  ✅ .env文件存在")
    else:
        print("  ⚠️  .env文件不存在，请复制.env.example并配置")
        print("     cp .env.example .env")
    
    # 检查API Token
    api_token = os.getenv("APIFY_API_TOKEN")
    if api_token:
        print(f"  ✅ API Token已配置 (长度: {len(api_token)})")
    else:
        print("  ❌ APIFY_API_TOKEN未配置")
    
    print()


def demo_basic_functionality():
    """演示基本功能"""
    print("🔧 基本功能演示:")
    
    # 获取系统状态
    status = apify_integration.get_status()
    print(f"  配置状态: {'✅' if status['configured'] else '❌'}")
    print(f"  客户端就绪: {'✅' if status['client_ready'] else '❌'}")
    print(f"  任务数量: {status['task_count']}")
    
    if not status['configured']:
        print("  ⚠️  请先配置API Token")
        return False
    
    if not status['client_ready']:
        print("  ⚠️  客户端未就绪")
        return False
    
    print("  ✅ 系统就绪")
    return True


def demo_actor_listing():
    """演示Actor列表功能"""
    print("\n📋 Actor列表演示:")
    
    try:
        actors = apify_integration.list_available_actors(limit=5)
        if actors:
            print(f"  找到 {len(actors)} 个Actor:")
            for i, actor in enumerate(actors[:3], 1):
                name = actor.get('name', 'Unknown')
                actor_id = actor.get('id', 'Unknown')
                print(f"    {i}. {name} ({actor_id})")
            if len(actors) > 3:
                print(f"    ... 还有 {len(actors) - 3} 个")
        else:
            print("  ❌ 未找到可用的Actor")
    except Exception as e:
        print(f"  ❌ 获取Actor列表失败: {e}")


def demo_task_management():
    """演示任务管理功能"""
    print("\n📝 任务管理演示:")
    
    # 列出现有任务
    tasks = apify_integration.list_tasks()
    print(f"  当前任务数量: {len(tasks)}")
    
    if tasks:
        print("  最近的任务:")
        for task in tasks[:3]:
            status_emoji = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.RUNNING: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.CANCELLED: "🚫"
            }.get(task.status, "❓")
            
            print(f"    {status_emoji} {task.name} ({task.status})")
            if task.result_count > 0:
                print(f"      📊 结果数量: {task.result_count}")
    else:
        print("  📭 暂无任务")


def interactive_demo():
    """交互式演示"""
    print("\n🎮 交互式演示:")
    print("  输入 'help' 查看可用命令")
    print("  输入 'quit' 退出")
    print()
    
    while True:
        try:
            command = input(">>> ").strip().lower()
            
            if command == 'quit':
                print("👋 再见！")
                break
            elif command == 'help':
                print("  可用命令:")
                print("    status  - 显示系统状态")
                print("    actors  - 列出可用Actor")
                print("    tasks   - 列出任务")
                print("    help    - 显示帮助")
                print("    quit    - 退出")
            elif command == 'status':
                status = apify_integration.get_status()
                print(f"  系统状态: {status}")
            elif command == 'actors':
                demo_actor_listing()
            elif command == 'tasks':
                demo_task_management()
            else:
                print(f"  ❓ 未知命令: {command}")
                print("  输入 'help' 查看可用命令")
        
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"  ❌ 错误: {e}")


def main():
    """主函数"""
    print_banner()
    
    # 环境检查
    check_environment()
    
    # 初始化系统
    print("🚀 初始化系统...")
    setup_result = apify_integration.setup()
    
    if setup_result['success']:
        print("  ✅ 系统初始化成功")
    else:
        print(f"  ❌ 系统初始化失败: {setup_result['message']}")
        print("\n💡 提示:")
        print("  1. 确保已配置APIFY_API_TOKEN环境变量")
        print("  2. 检查网络连接")
        print("  3. 验证API Token是否有效")
        return
    
    print()
    
    # 基本功能演示
    if demo_basic_functionality():
        demo_actor_listing()
        demo_task_management()
        
        # 交互式演示
        interactive_demo()
    
    print("\n🎯 演示完成！")
    print("💡 接下来你可以:")
    print("  1. 查看src/目录下的模块代码")
    print("  2. 使用core.py中的API创建自定义功能")
    print("  3. 扩展task_manager.py添加更多任务类型")
    print("  4. 在apify_client.py中添加更多API封装")


if __name__ == "__main__":
    main()
