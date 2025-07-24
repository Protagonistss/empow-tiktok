"""配置管理模块

负责管理Apify API配置、环境变量和应用设置。
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from loguru import logger

# 加载环境变量
load_dotenv()


class ApifyConfig(BaseModel):
    """Apify配置模型"""
    
    api_token: str = Field(..., description="Apify API Token")
    base_url: str = Field(default="https://api.apify.com/v2", description="Apify API基础URL")
    timeout: int = Field(default=30, description="请求超时时间(秒)")
    max_retries: int = Field(default=3, description="最大重试次数")
    
    class Config:
        env_prefix = "APIFY_"


class AppConfig(BaseModel):
    """应用配置模型"""
    
    debug: bool = Field(default=False, description="调试模式")
    log_level: str = Field(default="INFO", description="日志级别")
    data_dir: str = Field(default="./data", description="数据存储目录")
    
    class Config:
        env_prefix = "APP_"


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self._apify_config: Optional[ApifyConfig] = None
        self._app_config: Optional[AppConfig] = None
        self._load_configs()
    
    def _load_configs(self):
        """加载配置"""
        try:
            # 加载应用配置
            self._app_config = AppConfig()
            logger.info("应用配置加载成功")
            
            # 加载Apify配置
            api_token = os.getenv("APIFY_API_TOKEN")
            if not api_token:
                logger.warning("未找到APIFY_API_TOKEN环境变量")
                return
            
            self._apify_config = ApifyConfig(api_token=api_token)
            logger.info("Apify配置加载成功")
            
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
    
    @property
    def apify(self) -> Optional[ApifyConfig]:
        """获取Apify配置"""
        return self._apify_config
    
    @property
    def app(self) -> AppConfig:
        """获取应用配置"""
        return self._app_config or AppConfig()
    
    def set_apify_token(self, token: str) -> bool:
        """设置Apify API Token"""
        try:
            self._apify_config = ApifyConfig(api_token=token)
            logger.info("Apify API Token设置成功")
            return True
        except Exception as e:
            logger.error(f"Apify API Token设置失败: {e}")
            return False
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return self._apify_config is not None
    
    def validate_config(self) -> dict:
        """验证配置"""
        result = {
            "apify_configured": self._apify_config is not None,
            "app_configured": self._app_config is not None,
            "errors": []
        }
        
        if not self._apify_config:
            result["errors"].append("Apify API Token未配置")
        
        return result


# 全局配置管理器实例
config_manager = ConfigManager()