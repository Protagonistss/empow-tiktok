# Apify数据爬取脚本使用说明

这是一个简单的Apify数据爬取脚本，可以直接从指定的Apify actor run获取数据，无需交互式命令行操作。

## 功能特点

- 🚀 **简单直接**: 运行脚本即可自动爬取数据
- 📊 **数据保存**: 自动将数据保存为JSON格式
- 📋 **数据预览**: 显示爬取的数据概览
- ⚙️ **配置灵活**: 通过.env文件配置API参数

## 快速开始

### 1. 配置环境变量

确保`.env`文件中包含以下配置：

```env
# Apify配置
APIFY_API_TOKEN=your_api_token_here
APIFY_BASE_URL=https://api.apify.com/v2/actor-runs/your_run_id
APIFY_TIMEOUT=30

# 应用配置
APP_DATA_DIR=./data
```

### 2. 安装依赖

```bash
pip install python-dotenv requests
```

### 3. 运行脚本

```bash
python scraper.py
```

## 输出示例

```
🚀 开始爬取Apify数据...
📋 Run ID: K58ugcdn2TLtuJN8G
📊 状态: SUCCEEDED
⏱️ 运行时间: 29.092 秒
📁 数据集ID: wis8qmlFuQqYXDHQy
📦 获取到 58 条数据
💾 数据已保存到: data\apify_data_20250726_103727.json

📋 数据预览 (前3条):
  1. {"img": "https://...", "title": "...", "price": "..."}
  2. {"img": "https://...", "title": "...", "price": "..."}
  3. {"img": "https://...", "title": "...", "price": "..."}

✅ 数据爬取完成！
📊 共获取 58 条数据
📁 文件路径: data\apify_data_20250726_103727.json
```

## 数据格式

爬取的数据会保存为JSON格式，包含以下字段（以TikTok商品数据为例）：

```json
[
  {
    "img": "商品图片URL",
    "link": "商品链接",
    "title": "商品标题",
    "score": "评分",
    "sold": "销量",
    "origin_price": "原价",
    "sale_price": "售价"
  }
]
```

## 脚本结构

- `ApifyDataScraper`: 主要的数据爬取类
  - `get_run_info()`: 获取actor run的基本信息
  - `get_dataset_data()`: 从数据集获取数据
  - `save_data()`: 保存数据到文件
  - `scrape_data()`: 执行完整的数据爬取流程

## 自定义配置

### 修改数据获取数量

在`scraper.py`中修改`limit`参数：

```python
data = self.get_dataset_data(dataset_id, limit=2000)  # 获取更多数据
```

### 修改保存路径

在`.env`文件中修改`APP_DATA_DIR`：

```env
APP_DATA_DIR=./my_custom_data_folder
```

## 错误处理

脚本包含完整的错误处理机制：

- API连接失败
- 数据集不存在
- 网络超时
- 文件保存失败

## 与原有系统的区别

| 特性 | 原有系统 | 数据爬取脚本 |
|------|----------|-------------|
| 使用方式 | 交互式命令行 | 直接运行脚本 |
| 复杂度 | 高（任务管理、状态跟踪） | 低（直接获取数据） |
| 适用场景 | 复杂的数据集成项目 | 简单的数据爬取需求 |
| 学习成本 | 高 | 低 |

## 注意事项

1. 确保API Token有效且有足够的权限
2. 检查网络连接稳定性
3. 大量数据爬取时注意API限制
4. 定期清理数据文件夹避免占用过多空间

## 扩展功能

可以根据需要扩展以下功能：

- 数据过滤和清洗
- 多种输出格式（CSV、Excel等）
- 定时自动爬取
- 数据去重
- 错误重试机制