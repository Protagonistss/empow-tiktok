"""Apify客户端模块

封装与Apify API的交互逻辑，提供数据获取和任务管理功能。
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from apify_client import ApifyClient
from loguru import logger
from pydantic import BaseModel

from .config import config_manager


class ActorRun(BaseModel):
    """Actor运行结果模型"""
    
    id: str
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    stats: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None


class DatasetItem(BaseModel):
    """数据集项目模型"""
    
    data: Dict[str, Any]
    created_at: datetime = datetime.now()


class ApifyDataClient:
    """Apify数据客户端"""
    
    def __init__(self):
        self._client: Optional[ApifyClient] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化Apify客户端"""
        if not config_manager.is_configured():
            logger.warning("Apify配置未完成，客户端初始化跳过")
            return
        
        try:
            apify_config = config_manager.apify
            self._client = ApifyClient(apify_config.api_token)
            logger.info("Apify客户端初始化成功")
        except Exception as e:
            logger.error(f"Apify客户端初始化失败: {e}")
    
    def is_ready(self) -> bool:
        """检查客户端是否就绪"""
        return self._client is not None
    
    def test_connection(self) -> bool:
        """测试连接"""
        if not self.is_ready():
            logger.error("客户端未初始化")
            return False
        
        try:
            # 获取用户信息来测试连接
            user_info = self._client.user().get()
            logger.info(f"连接测试成功，用户: {user_info.get('username', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False
    
    def list_actors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取Actor列表"""
        if not self.is_ready():
            logger.error("客户端未初始化")
            return []
        
        try:
            actors = self._client.actors().list(limit=limit)
            logger.info(f"获取到 {len(actors.items)} 个Actor")
            return actors.items
        except Exception as e:
            logger.error(f"获取Actor列表失败: {e}")
            return []
    
    def run_actor(self, actor_id: str, run_input: Dict[str, Any] = None) -> Optional[ActorRun]:
        """运行Actor"""
        if not self.is_ready():
            logger.error("客户端未初始化")
            return None
        
        try:
            logger.info(f"开始运行Actor: {actor_id}")
            run = self._client.actor(actor_id).call(run_input=run_input or {})
            
            actor_run = ActorRun(
                id=run['id'],
                status=run['status'],
                started_at=run.get('startedAt'),
                finished_at=run.get('finishedAt'),
                stats=run.get('stats'),
                output=run.get('output')
            )
            
            logger.info(f"Actor运行完成: {actor_run.id}, 状态: {actor_run.status}")
            return actor_run
            
        except Exception as e:
            logger.error(f"运行Actor失败: {e}")
            return None
    
    def get_run_status(self, run_id: str) -> Optional[str]:
        """获取运行状态"""
        if not self.is_ready():
            logger.error("客户端未初始化")
            return None
        
        try:
            run = self._client.run(run_id).get()
            return run.get('status')
        except Exception as e:
            logger.error(f"获取运行状态失败: {e}")
            return None
    
    def get_dataset_items(self, dataset_id: str, limit: int = 100) -> List[DatasetItem]:
        """获取数据集项目"""
        if not self.is_ready():
            logger.error("客户端未初始化")
            return []
        
        try:
            dataset = self._client.dataset(dataset_id)
            items = dataset.list_items(limit=limit)
            
            dataset_items = [
                DatasetItem(data=item) for item in items.items
            ]
            
            logger.info(f"获取到 {len(dataset_items)} 个数据项")
            return dataset_items
            
        except Exception as e:
            logger.error(f"获取数据集项目失败: {e}")
            return []
    
    def download_dataset(self, dataset_id: str, format: str = "json") -> Optional[bytes]:
        """下载数据集"""
        if not self.is_ready():
            logger.error("客户端未初始化")
            return None
        
        try:
            dataset = self._client.dataset(dataset_id)
            data = dataset.download_items(item_format=format)
            
            logger.info(f"数据集下载成功，格式: {format}")
            return data
            
        except Exception as e:
            logger.error(f"下载数据集失败: {e}")
            return None
    
    def get_actor_info(self, actor_id: str) -> Optional[Dict[str, Any]]:
        """获取Actor信息"""
        if not self.is_ready():
            logger.error("客户端未初始化")
            return None
        
        try:
            actor = self._client.actor(actor_id).get()
            logger.info(f"获取Actor信息成功: {actor.get('name', 'Unknown')}")
            return actor
        except Exception as e:
            logger.error(f"获取Actor信息失败: {e}")
            return None


# 全局客户端实例
apify_client = ApifyDataClient()