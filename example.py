"""Apify数据集成工具 - 使用示例

这个脚本展示了如何使用核心API进行数据获取和处理。
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core import apify_integration
from src.task_manager import TaskStatus


def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 1. 检查系统状态
    print("\n1. 检查系统状态")
    status = apify_integration.get_status()
    print(f"配置状态: {status['configured']}")
    print(f"客户端就绪: {status['client_ready']}")
    
    if not status['configured']:
        print("❌ 请先配置APIFY_API_TOKEN环境变量")
        return
    
    # 2. 获取可用Actor
    print("\n2. 获取可用Actor")
    actors = apify_integration.list_available_actors(limit=3)
    if actors:
        print(f"找到 {len(actors)} 个Actor:")
        for actor in actors:
            print(f"  - {actor.get('name', 'Unknown')} ({actor.get('id', 'Unknown')})")
    else:
        print("❌ 未找到可用Actor")
        return
    
    # 3. 创建任务示例（不实际运行）
    print("\n3. 创建任务示例")
    if actors:
        first_actor = actors[0]
        task = apify_integration.create_data_task(
            name="示例任务",
            actor_id=first_actor['id'],
            input_data={"example": "data"},
            description="这是一个示例任务"
        )
        
        if task:
            print(f"✅ 任务创建成功: {task.name} ({task.id})")
            print(f"   Actor: {first_actor['name']}")
            print(f"   状态: {task.status}")
        else:
            print("❌ 任务创建失败")


def example_task_management():
    """任务管理示例"""
    print("\n=== 任务管理示例 ===")
    
    # 1. 列出所有任务
    print("\n1. 列出所有任务")
    tasks = apify_integration.list_tasks()
    print(f"总任务数: {len(tasks)}")
    
    if tasks:
        print("最近的任务:")
        for task in tasks[:3]:
            print(f"  - {task.name} ({task.status}) - {task.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    # 2. 按状态筛选任务
    print("\n2. 按状态筛选任务")
    for status in [TaskStatus.PENDING, TaskStatus.COMPLETED, TaskStatus.FAILED]:
        filtered_tasks = apify_integration.list_tasks(status=status)
        print(f"  {status}: {len(filtered_tasks)} 个任务")


def example_actor_exploration():
    """Actor探索示例"""
    print("\n=== Actor探索示例 ===")
    
    if not apify_integration.get_status()['client_ready']:
        print("❌ 客户端未就绪")
        return
    
    # 1. 获取更多Actor信息
    print("\n1. 获取Actor详细信息")
    actors = apify_integration.list_available_actors(limit=2)
    
    if actors:
        for actor in actors[:1]:  # 只查看第一个
            actor_id = actor['id']
            print(f"\n查看Actor: {actor['name']}")
            
            # 获取详细信息
            actor_info = apify_integration.get_actor_info(actor_id)
            if actor_info:
                print(f"  描述: {actor_info.get('description', 'N/A')[:100]}...")
                print(f"  版本: {actor_info.get('taggedBuilds', {}).get('latest', 'N/A')}")
                print(f"  运行次数: {actor_info.get('stats', {}).get('totalRuns', 'N/A')}")
            else:
                print("  ❌ 无法获取详细信息")


def example_configuration():
    """配置管理示例"""
    print("\n=== 配置管理示例 ===")
    
    # 显示当前配置状态
    from src.config import config_manager
    
    print("\n1. 配置验证")
    validation = config_manager.validate_config()
    print(f"Apify配置: {'✅' if validation['apify_configured'] else '❌'}")
    print(f"应用配置: {'✅' if validation['app_configured'] else '❌'}")
    
    if validation['errors']:
        print("配置错误:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    print("\n2. 应用配置")
    app_config = config_manager.app
    print(f"调试模式: {app_config.debug}")
    print(f"日志级别: {app_config.log_level}")
    print(f"数据目录: {app_config.data_dir}")


def main():
    """主函数"""
    print("🚀 Apify数据集成工具 - 使用示例")
    print("="*50)
    
    # 初始化系统
    print("\n初始化系统...")
    setup_result = apify_integration.setup()
    
    if setup_result['success']:
        print("✅ 系统初始化成功")
    else:
        print(f"❌ 系统初始化失败: {setup_result['message']}")
        print("\n💡 请确保:")
        print("  1. 已设置APIFY_API_TOKEN环境变量")
        print("  2. 网络连接正常")
        print("  3. API Token有效")
        print("\n继续演示其他功能...")
    
    # 运行示例
    try:
        example_configuration()
        example_basic_usage()
        example_task_management()
        example_actor_exploration()
        
        print("\n🎯 示例完成！")
        print("\n💡 接下来你可以:")
        print("  1. 运行 python main.py 进入交互模式")
        print("  2. 查看 src/ 目录下的源码")
        print("  3. 根据需要扩展功能")
        print("  4. 创建自己的数据获取脚本")
        
    except Exception as e:
        print(f"\n❌ 运行示例时出错: {e}")
        print("请检查配置和网络连接")


if __name__ == "__main__":
    main()