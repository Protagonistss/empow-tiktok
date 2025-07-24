"""任务管理模块

负责管理数据获取任务的创建、执行、监控和结果处理。
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

from loguru import logger
from pydantic import BaseModel, Field

from .apify_service import apify_client
from .config import config_manager


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskConfig(BaseModel):
    """任务配置模型"""
    
    actor_id: str = Field(..., description="Actor ID")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="输入数据")
    max_items: Optional[int] = Field(default=None, description="最大项目数")
    timeout: int = Field(default=300, description="超时时间(秒)")
    

class Task(BaseModel):
    """任务模型"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="任务名称")
    description: Optional[str] = Field(default=None, description="任务描述")
    config: TaskConfig = Field(..., description="任务配置")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    run_id: Optional[str] = Field(default=None, description="Apify运行ID")
    dataset_id: Optional[str] = Field(default=None, description="数据集ID")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    result_count: int = Field(default=0, description="结果数量")
    
    class Config:
        use_enum_values = True


class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._data_dir = Path(config_manager.app.data_dir)
        self._tasks_file = self._data_dir / "tasks.json"
        self._ensure_data_dir()
        self._load_tasks()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        self._data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"数据目录: {self._data_dir}")
    
    def _load_tasks(self):
        """加载任务"""
        if not self._tasks_file.exists():
            logger.info("任务文件不存在，创建新的任务存储")
            return
        
        try:
            with open(self._tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            for task_data in tasks_data:
                task = Task(**task_data)
                self._tasks[task.id] = task
            
            logger.info(f"加载了 {len(self._tasks)} 个任务")
            
        except Exception as e:
            logger.error(f"加载任务失败: {e}")
    
    def _save_tasks(self):
        """保存任务"""
        try:
            tasks_data = [task.dict() for task in self._tasks.values()]
            
            with open(self._tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.debug("任务保存成功")
            
        except Exception as e:
            logger.error(f"保存任务失败: {e}")
    
    def create_task(self, name: str, actor_id: str, input_data: Dict[str, Any] = None, 
                   description: str = None, **kwargs) -> Task:
        """创建任务"""
        config = TaskConfig(
            actor_id=actor_id,
            input_data=input_data or {},
            **kwargs
        )
        
        task = Task(
            name=name,
            description=description,
            config=config
        )
        
        self._tasks[task.id] = task
        self._save_tasks()
        
        logger.info(f"创建任务: {task.name} ({task.id})")
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self._tasks.get(task_id)
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """列出任务"""
        tasks = list(self._tasks.values())
        
        if status:
            tasks = [task for task in tasks if task.status == status]
        
        # 按创建时间倒序排列
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        return tasks
    
    def run_task(self, task_id: str) -> bool:
        """运行任务"""
        task = self.get_task(task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return False
        
        if task.status != TaskStatus.PENDING:
            logger.error(f"任务状态不允许运行: {task.status}")
            return False
        
        if not apify_client.is_ready():
            logger.error("Apify客户端未就绪")
            task.status = TaskStatus.FAILED
            task.error_message = "Apify客户端未就绪"
            self._save_tasks()
            return False
        
        try:
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            self._save_tasks()
            
            logger.info(f"开始运行任务: {task.name}")
            
            # 运行Actor
            actor_run = apify_client.run_actor(
                actor_id=task.config.actor_id,
                run_input=task.config.input_data
            )
            
            if not actor_run:
                raise Exception("Actor运行失败")
            
            task.run_id = actor_run.id
            
            # 检查运行状态
            if actor_run.status == "SUCCEEDED":
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                
                # 获取数据集ID
                if actor_run.output and 'datasetId' in actor_run.output:
                    task.dataset_id = actor_run.output['datasetId']
                    
                    # 获取结果数量
                    dataset_items = apify_client.get_dataset_items(
                        task.dataset_id, limit=1
                    )
                    task.result_count = len(dataset_items)
                
                logger.info(f"任务完成: {task.name}, 结果数量: {task.result_count}")
                
            else:
                task.status = TaskStatus.FAILED
                task.error_message = f"Actor运行状态: {actor_run.status}"
                logger.error(f"任务失败: {task.name}, 状态: {actor_run.status}")
            
            self._save_tasks()
            return task.status == TaskStatus.COMPLETED
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            self._save_tasks()
            
            logger.error(f"任务运行失败: {task.name}, 错误: {e}")
            return False
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.get_task(task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return False
        
        if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            logger.error(f"任务状态不允许取消: {task.status}")
            return False
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        self._save_tasks()
        
        logger.info(f"任务已取消: {task.name}")
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        if task_id not in self._tasks:
            logger.error(f"任务不存在: {task_id}")
            return False
        
        task = self._tasks[task_id]
        del self._tasks[task_id]
        self._save_tasks()
        
        logger.info(f"任务已删除: {task.name}")
        return True
    
    def get_task_results(self, task_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取任务结果"""
        task = self.get_task(task_id)
        if not task or not task.dataset_id:
            logger.error(f"任务或数据集不存在: {task_id}")
            return []
        
        dataset_items = apify_client.get_dataset_items(task.dataset_id, limit=limit)
        return [item.data for item in dataset_items]
    
    def export_task_results(self, task_id: str, format: str = "json") -> Optional[bytes]:
        """导出任务结果"""
        task = self.get_task(task_id)
        if not task or not task.dataset_id:
            logger.error(f"任务或数据集不存在: {task_id}")
            return None
        
        return apify_client.download_dataset(task.dataset_id, format=format)


# 全局任务管理器实例
task_manager = TaskManager()