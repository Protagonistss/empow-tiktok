"""简单的Apify数据爬取脚本

使用ApifyClient主动运行Actor并获取数据。"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 导入ApifyClient
from apify_client import ApifyClient


class ApifyDataScraper:
    """Apify数据爬取器"""
    
    def __init__(self):
        self.api_token = os.getenv('APIFY_API_TOKEN')
        self.timeout = int(os.getenv('APIFY_TIMEOUT', 30))
        self.data_dir = Path(os.getenv('APP_DATA_DIR', './data'))
        
        # 确保数据目录存在
        self.data_dir.mkdir(exist_ok=True)
        
        if not self.api_token:
            raise ValueError("APIFY_API_TOKEN 未配置")
        
        # 初始化ApifyClient
        self.client = ApifyClient(self.api_token)
    
    def run_actor(self, actor_id: str, run_input: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """运行指定的Actor"""
        try:
            print(f"🚀 开始运行Actor: {actor_id}")
            print(f"📋 输入参数: {json.dumps(run_input, ensure_ascii=False, indent=2)}")
            
            # 运行Actor并等待完成
            run = self.client.actor(actor_id).call(run_input=run_input)
            
            print(f"✅ Actor运行完成")
            print(f"📋 Run ID: {run.get('id')}")
            print(f"📊 状态: {run.get('status')}")
            print(f"⏱️ 运行时间: {run.get('stats', {}).get('runTimeSecs', 0)} 秒")
            
            return run
        except Exception as e:
            print(f"运行Actor失败: {e}")
            return None
    
    def get_dataset_data(self, dataset_id: str, limit: int = 1000, max_retries: int = 3) -> List[Dict[str, Any]]:
        """从数据集获取数据"""
        import time
        
        for retry in range(max_retries):
            try:
                print(f"📁 从数据集获取数据: {dataset_id} (尝试 {retry + 1}/{max_retries})")
                
                # 使用ApifyClient获取数据集数据
                items = []
                for item in self.client.dataset(dataset_id).iterate_items():
                    items.append(item)
                    if len(items) >= limit:
                        break
                
                if items:
                    return items
                else:
                    print(f"⚠️ 数据集为空，等待 {(retry + 1) * 5} 秒后重试...")
                    time.sleep((retry + 1) * 5)  # 递增等待时间
                    
            except Exception as e:
                print(f"获取数据集数据失败 (尝试 {retry + 1}): {e}")
                if retry < max_retries - 1:
                    time.sleep((retry + 1) * 3)
        
        return []
    
    def save_data(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """保存数据到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"apify_data_{timestamp}.json"
        
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def scrape_data(self, actor_id: str = "QwlnuM1ok9nxykQjF", 
                   start_url: str = "https://www.tiktok.com/shop/pdp/2025-2026-daily-planner-by-the-dailee-goal-setting-scheduling-to-do-lists/1731200046599410414?source=ecommerce_mall&enter_from=ecommerce_mall&enter_method=homepage_product_feed_savings",
                   max_items: int = 100,
                   use_test_mode: bool = False) -> Dict[str, Any]:
        """执行数据爬取"""
        if use_test_mode:
            print("🧪 使用测试模式 - 爬取网页内容...")
            # 使用通用网页爬虫进行测试
            actor_id = "apify/web-scraper"
            run_input = {
                "startUrls": [{"url": "https://apify.com/store"}],
                "linkSelector": "a[href]",
                "pageFunction": "async function pageFunction(context) { const { page, request } = context; const title = await page.title(); return { url: request.url, title }; }",
                "maxRequestsPerCrawl": min(max_items, 10)
            }
        else:
            print("🚀 开始爬取TikTok商品数据...")
            # 准备TikTok Actor输入参数
            run_input = {
                "start_urls": [{"url": start_url}],
                "max_items": max_items,
            }
        
        # 运行Actor
        run_result = self.run_actor(actor_id, run_input)
        if not run_result:
            return {"success": False, "message": "Actor运行失败"}
        
        # 获取数据集ID
        dataset_id = run_result.get('defaultDatasetId')
        if not dataset_id:
            return {"success": False, "message": "未找到数据集ID"}
        
        print(f"📁 数据集ID: {dataset_id}")
        
        # 获取数据 (增加重试机制)
        data = self.get_dataset_data(dataset_id, max_items, max_retries=5)
        if not data:
            # 尝试直接从API获取数据集信息
            try:
                dataset_info = self.client.dataset(dataset_id).get()
                print(f"📊 数据集信息: {dataset_info}")
                return {"success": False, "message": f"未获取到数据，数据集可能为空。数据集信息: {dataset_info}"}
            except Exception as e:
                return {"success": False, "message": f"未获取到数据且无法获取数据集信息: {e}"}
        
        print(f"📦 获取到 {len(data)} 条数据")
        
        # 保存数据
        filepath = self.save_data(data)
        print(f"💾 数据已保存到: {filepath}")
        
        # 显示数据预览
        if data:
            print("\n📋 数据预览 (前3条):")
            for i, item in enumerate(data[:3], 1):
                print(f"  {i}. {json.dumps(item, ensure_ascii=False)[:100]}...")
        
        return {
            "success": True,
            "run_id": run_result.get('id'),
            "dataset_id": dataset_id,
            "data_count": len(data),
            "file_path": filepath,
            "run_info": run_result
        }


def main():
    """主函数"""
    import sys
    
    try:
        scraper = ApifyDataScraper()
        
        # 检查命令行参数
        use_test_mode = len(sys.argv) > 1 and sys.argv[1] == "--test"
        
        if use_test_mode:
            print("🧪 运行测试模式...")
            result = scraper.scrape_data(use_test_mode=True)
        else:
            print("🚀 运行TikTok爬取模式...")
            print("💡 提示: 使用 'python scraper.py --test' 运行测试模式")
            result = scraper.scrape_data()
        
        if result["success"]:
            print("\n✅ 数据爬取完成！")
            print(f"📊 共获取 {result['data_count']} 条数据")
            print(f"📁 文件路径: {result['file_path']}")
        else:
            print(f"\n❌ 数据爬取失败: {result['message']}")
            if not use_test_mode:
                print("\n💡 建议: 尝试运行测试模式 'python scraper.py --test'")
    
    except Exception as e:
        print(f"\n💥 程序执行失败: {e}")
        print("\n💡 建议: 检查API Token配置和网络连接")


if __name__ == "__main__":
    main()