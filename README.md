# Apify数据集成工具 - 后端逻辑验证

🚀 专注于渐进式开发和功能验证的Python项目，用于与Apify平台对接获取网络爬虫数据。

## 📋 项目特点

- ✅ **纯后端逻辑**：专注于数据对接和处理，无UI界面
- ✅ **渐进式开发**：模块化设计，便于逐步扩展功能
- ✅ **完整封装**：提供配置管理、客户端、任务管理等完整功能
- ✅ **易于验证**：命令行界面，快速验证功能逻辑

## 🏗️ 项目结构

```
empow-tiktok/
├── src/                    # 核心源码目录
│   ├── __init__.py        # 包初始化
│   ├── config.py          # 配置管理模块
│   ├── apify_service.py   # Apify客户端封装
│   ├── task_manager.py    # 任务管理模块
│   └── core.py            # 核心业务逻辑
├── data/                   # 数据存储目录
├── logs/                   # 日志文件目录
├── main.py                # 主入口文件
├── .env.example           # 环境变量模板
└── pyproject.toml         # 项目配置
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用pip安装（推荐）
pip install apify-client requests python-dotenv pydantic loguru

# 或使用uv（如果网络允许）
uv sync
```

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加你的Apify API Token
# APIFY_API_TOKEN=your_apify_api_token_here
```

### 3. 运行项目

```bash
python main.py
```

## 🎮 交互式演示

运行项目后，你将看到：

1. **环境检查**：验证配置文件和API Token
2. **系统初始化**：连接Apify服务
3. **功能演示**：展示Actor列表、任务管理等
4. **交互式命令**：支持实时操作

### 可用命令

- `status` - 显示系统状态
- `actors` - 列出可用Actor
- `tasks` - 列出任务
- `help` - 显示帮助
- `quit` - 退出程序

## 📚 核心模块说明

### 配置管理 (config.py)

```python
from src.config import config_manager

# 检查配置状态
status = config_manager.validate_config()
print(status)

# 设置API Token
config_manager.set_apify_token("your_token")
```

### Apify服务 (apify_service.py)

```python
from src.apify_service import apify_client

# 测试连接
if apify_client.test_connection():
    print("连接成功")

# 获取Actor列表
actors = apify_client.list_actors(limit=10)

# 运行Actor
result = apify_client.run_actor("actor_id", {"input": "data"})
```

### 任务管理 (task_manager.py)

```python
from src.task_manager import task_manager

# 创建任务
task = task_manager.create_task(
    name="测试任务",
    actor_id="some_actor_id",
    input_data={"url": "https://example.com"}
)

# 运行任务
success = task_manager.run_task(task.id)

# 获取结果
results = task_manager.get_task_results(task.id)
```

### 核心API (core.py)

```python
from src.core import apify_integration

# 初始化
setup_result = apify_integration.setup(api_token="your_token")

# 快速运行
result = apify_integration.quick_run(
    actor_id="apify/web-scraper",
    input_data={"startUrls": [{"url": "https://example.com"}]}
)
```

## 🔧 开发指南

### 扩展新功能

1. **添加新的Actor封装**：在`apify_service.py`中添加专用方法
2. **扩展任务类型**：在`task_manager.py`中添加新的任务配置
3. **增加业务逻辑**：在`core.py`中添加高级API
4. **自定义配置**：在`config.py`中添加新的配置项

### 日志和调试

- 日志文件：`logs/app.log`
- 调试模式：设置`APP_DEBUG=true`
- 日志级别：通过`APP_LOG_LEVEL`控制

### 数据存储

- 任务数据：`data/tasks.json`
- 下载数据：`data/`目录下
- 配置文件：`.env`

## 🎯 使用场景

1. **数据验证**：快速验证Apify Actor的数据获取能力
2. **批量处理**：创建多个任务进行批量数据处理
3. **API测试**：测试不同Actor的输入输出格式
4. **原型开发**：为更大的项目提供后端逻辑原型

## 📝 注意事项

- 确保Apify API Token有效且有足够的配额
- 网络连接稳定，某些Actor运行时间较长
- 大量数据处理时注意磁盘空间
- 定期清理日志文件和临时数据

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

MIT License