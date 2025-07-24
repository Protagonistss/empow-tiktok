"""核心业务逻辑模块

提供高级API接口，整合配置管理、客户端和任务管理功能。
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from .config import config_manager
from .apify_service import apify_client
from .task_manager import task_manager, Task, TaskStatus


class ApifyDataIntegration:
    """Apify数据集成主类"""
    
    def __init__(self):
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志"""
        log_level = config_manager.app.log_level
        logger.remove()  # 移除默认处理器
        logger.add(
            "logs/app.log",
            rotation="10 MB",
            retention="7 days",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        )
        logger.add(
            lambda msg: print(msg, end=""),
            level=log_level,
            format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}"
        )
        logger.info("日志系统初始化完成")
    
    def setup(self, api_token: str = None) -> Dict[str, Any]:
        """初始化设置"""
        logger.info("开始初始化Apify数据集成工具")
        
        result = {
            "success": False,
            "message": "",
            "config_status": {},
            "connection_status": False
        }
        
        try:
            # 设置API Token（如果提供）
            if api_token:
                if config_manager.set_apify_token(api_token):
                    logger.info("API Token设置成功")
                else:
                    result["message"] = "API Token设置失败"
                    return result
            
            # 验证配置
            config_status = config_manager.validate_config()
            result["config_status"] = config_status
            
            if not config_status["apify_configured"]:
                result["message"] = "Apify配置未完成，请设置API Token"
                return result
            
            # 重新初始化客户端
            apify_client._initialize_client()
            
            # 测试连接
            connection_status = apify_client.test_connection()
            result["connection_status"] = connection_status
            
            if not connection_status:
                result["message"] = "Apify连接测试失败"
                return result
            
            result["success"] = True
            result["message"] = "初始化成功"
            logger.info("Apify数据集成工具初始化完成")
            
        except Exception as e:
            result["message"] = f"初始化失败: {e}"
            logger.error(f"初始化失败: {e}")
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "configured": config_manager.is_configured(),
            "client_ready": apify_client.is_ready(),
            "config_validation": config_manager.validate_config(),
            "task_count": len(task_manager.list_tasks())
        }
    
    def list_available_actors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """列出可用的Actor"""
        logger.info("获取可用Actor列表")
        return apify_client.list_actors(limit=limit)
    
    def get_actor_info(self, actor_id: str) -> Optional[Dict[str, Any]]:
        """获取Actor详细信息"""
        logger.info(f"获取Actor信息: {actor_id}")
        return apify_client.get_actor_info(actor_id)
    
    def create_data_task(self, name: str, actor_id: str, 
                        input_data: Dict[str, Any] = None,
                        description: str = None,
                        **kwargs) -> Optional[Task]:
        """创建数据获取任务"""
        logger.info(f"创建数据任务: {name}")
        
        if not apify_client.is_ready():
            logger.error("Apify客户端未就绪")
            return None
        
        # 验证Actor是否存在
        actor_info = apify_client.get_actor_info(actor_id)
        if not actor_info:
            logger.error(f"Actor不存在: {actor_id}")
            return None
        
        return task_manager.create_task(
            name=name,
            actor_id=actor_id,
            input_data=input_data or {},
            description=description,
            **kwargs
        )
    
    def run_task(self, task_id: str) -> bool:
        """运行任务"""
        logger.info(f"运行任务: {task_id}")
        return task_manager.run_task(task_id)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务信息"""
        return task_manager.get_task(task_id)
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """列出任务"""
        return task_manager.list_tasks(status=status)
    
    def get_task_results(self, task_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取任务结果"""
        logger.info(f"获取任务结果: {task_id}")
        return task_manager.get_task_results(task_id, limit=limit)
    
    def export_task_results(self, task_id: str, format: str = "json") -> Optional[bytes]:
        """导出任务结果"""
        logger.info(f"导出任务结果: {task_id}, 格式: {format}")
        return task_manager.export_task_results(task_id, format=format)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        logger.info(f"取消任务: {task_id}")
        return task_manager.cancel_task(task_id)
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        logger.info(f"删除任务: {task_id}")
        return task_manager.delete_task(task_id)
    
    def quick_run(self, actor_id: str, input_data: Dict[str, Any] = None,
                 task_name: str = None) -> Optional[Dict[str, Any]]:
        """快速运行Actor并获取结果"""
        task_name = task_name or f"Quick run {actor_id}"
        logger.info(f"快速运行: {task_name}")
        
        # 创建任务
        task = self.create_data_task(
            name=task_name,
            actor_id=actor_id,
            input_data=input_data,
            description="快速运行任务"
        )
        
        if not task:
            return None
        
        # 运行任务
        success = self.run_task(task.id)
        if not success:
            return {
                "success": False,
                "task_id": task.id,
                "message": "任务运行失败"
            }
        
        # 获取结果
        results = self.get_task_results(task.id)
        
        return {
            "success": True,
            "task_id": task.id,
            "result_count": len(results),
            "results": results[:10],  # 只返回前10个结果作为预览
            "message": f"任务完成，共获取 {len(results)} 条数据"
        }


# 全局实例
apify_integration = ApifyDataIntegration()