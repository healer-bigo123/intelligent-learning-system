"""
视频搜索与智能匹配服务

该模块负责：
1. 从 B 站等视频平台搜索教育资源
2. 根据学习资料智能匹配相关视频
3. 提供视频缓存机制减少 API 调用
"""
import asyncio
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import hashlib
import json
import concurrent.futures


# ================ 数据模型 ================

@dataclass
class VideoInfo:
    """视频信息"""
    title: str
    author: str
    bvid: str
    url: str
    cover: str
    duration: str
    play_count: int
    description: str
    source: str = "bilibili"
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "title": self.title,
            "author": self.author,
            "bvid": self.bvid,
            "url": self.url,
            "cover": self.cover,
            "duration": self.duration,
            "play_count": self.play_count,
            "description": self.description,
            "source": self.source
        }


@dataclass
class CacheEntry:
    """缓存条目"""
    data: List[Dict]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def is_expired(self, ttl_seconds: int = 3600) -> bool:
        """检查缓存是否过期"""
        return (datetime.utcnow() - self.timestamp).total_seconds() > ttl_seconds


# ================ B 站搜索服务 ================

class BilibiliSearchService:
    """B 站视频搜索服务"""
    
    BILIBILI_SEARCH_URL = "https://api.bilibili.com/x/web-interface/search/type"
    
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_ttl = 3600  # 缓存 1 小时
    
    def _generate_cache_key(self, keyword: str, page: int = 1) -> str:
        """生成缓存键"""
        key_str = f"bilibili:{keyword}:{page}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[List[Dict]]:
        """从缓存获取数据"""
        if key in self.cache:
            entry = self.cache[key]
            if not entry.is_expired(self.cache_ttl):
                return entry.data
            else:
                del self.cache[key]
        return None
    
    def _set_to_cache(self, key: str, data: List[Dict]):
        """设置缓存数据"""
        self.cache[key] = CacheEntry(data=data)
    
    def _parse_search_result(self, data: Dict) -> List[Dict]:
        """解析搜索结果"""
        results = []
        result_list = data.get("data", {}).get("result", [])
        
        for item in result_list:
            title = item.get("title", "")
            title = title.replace("<em class=\"keyword\">", "").replace("</em>", "")
            
            # B站封面URL是 //i0.hdslb.com/... 格式，需要补全 https:
            cover_url = item.get("pic", "")
            if cover_url and cover_url.startswith("//"):
                cover_url = "https:" + cover_url
            
            video = VideoInfo(
                title=title,
                author=item.get("author", "未知"),
                bvid=item.get("bvid", ""),
                url=f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                cover=cover_url,
                duration=item.get("duration", "0:00"),
                play_count=item.get("play", 0),
                description=item.get("description", "")[:200],
                source="bilibili"
            )
            results.append(video.to_dict())
        
        return results
    
    def _sync_search(self, keyword: str, page: int, page_size: int) -> Dict:
        """同步搜索（requests 库对 B 站 API 兼容性更好）"""
        import time
        params = {
            "search_type": "video",
            "keyword": keyword,
            "page": page,
            "page_size": page_size
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
        }
        
        # 最多重试 2 次，间隔递增（应对 B 站限流）
        for attempt in range(3):
            try:
                resp = requests.get(
                    self.BILIBILI_SEARCH_URL,
                    params=params,
                    headers=headers,
                    timeout=10.0,
                )
                if resp.status_code == 412:
                    wait = (attempt + 1) * 2
                    print(f"B 站限流(412)，{wait}秒后重试...")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException:
                if attempt < 2:
                    time.sleep(2)
                    continue
                raise
        return {"code": -1, "message": "retry exhausted"}
    
    async def search_videos(self, keyword: str, page: int = 1, page_size: int = 10) -> List[Dict]:
        """
        根据关键词搜索 B 站视频
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            视频列表
        """
        # 检查缓存
        cache_key = self._generate_cache_key(keyword, page)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            # 使用线程池执行同步请求（B站API对同步httpx更友好）
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                data = await loop.run_in_executor(
                    pool, self._sync_search, keyword, page, page_size
                )
            
            if data.get("code") != 0:
                print(f"B 站搜索返回错误码: {data.get('code')} - {data.get('message')}")
                return []
            
            results = self._parse_search_result(data)
            
            # 存入缓存
            if results:
                self._set_to_cache(cache_key, results)
            
            return results
            
        except requests.RequestException as e:
            print(f"B 站搜索 HTTP 错误: {e}")
            return []
        except Exception as e:
            print(f"B 站搜索异常: {e}")
            return []
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()


# ================ 视频智能匹配服务 ================

class VideoMatchService:
    """视频智能匹配服务"""
    
    def __init__(self):
        self.bilibili = BilibiliSearchService()
    
    async def match_videos(
        self,
        material: Dict,
        max_results: int = 20
    ) -> List[Dict]:
        """
        根据学习资料智能匹配视频
        
        匹配策略（优先级从高到低）：
        1. 知识点精确匹配
        2. 标题 + 学科组合搜索
        3. 标签搜索
        
        Args:
            material: 学习资料信息，包含 title, subject, knowledge_point, tags 等
            max_results: 最大返回结果数
            
        Returns:
            匹配的视频列表
        """
        all_videos = []
        search_queries = []
        
        subject = material.get("subject", "")
        title = material.get("title", "")
        knowledge_point = material.get("knowledge_point", "")
        tags = material.get("tags", "")
        
        # 策略 1：用知识点搜索（最精确）
        if knowledge_point:
            search_queries.append(f"{subject} {knowledge_point}")
        
        # 策略 2：用标题搜索
        if title:
            search_queries.append(f"{subject} {title}")
        
        # 策略 3：用标签搜索
        if tags:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()][:2]
            if tag_list:
                search_queries.append(f"{subject} {' '.join(tag_list)}")
        
        # 兜底策略：如果以上策略都没有生成搜索词，至少用学科搜索
        if not search_queries and subject:
            search_queries.append(subject)
        
        # 去重搜索
        import time
        seen_bvids = set()
        
        for idx, query in enumerate(search_queries):
            try:
                # 多次搜索之间加间隔，避免触发限流
                if idx > 0:
                    time.sleep(1)
                videos = await self.bilibili.search_videos(query, page_size=5)
                
                for v in videos:
                    bvid = v.get("bvid")
                    if bvid and bvid not in seen_bvids:
                        seen_bvids.add(bvid)
                        all_videos.append(v)
                        
                        if len(all_videos) >= max_results:
                            break
            except Exception as e:
                print(f"搜索查询 '{query}' 失败: {e}")
                continue
        
        # 按播放量排序（优先推荐热门视频）
        all_videos.sort(key=lambda x: x.get("play_count", 0), reverse=True)
        
        return all_videos[:max_results]
    
    async def search_by_keywords(
        self,
        keywords: List[str],
        max_results: int = 10
    ) -> List[Dict]:
        """
        根据关键词列表搜索视频
        
        Args:
            keywords: 关键词列表
            max_results: 最大返回结果数
            
        Returns:
            视频列表
        """
        all_videos = []
        seen_bvids = set()
        
        for keyword in keywords:
            try:
                videos = await self.bilibili.search_videos(keyword, page_size=5)
                
                for v in videos:
                    bvid = v.get("bvid")
                    if bvid and bvid not in seen_bvids:
                        seen_bvids.add(bvid)
                        all_videos.append(v)
                        
                        if len(all_videos) >= max_results:
                            break
            except Exception as e:
                print(f"搜索关键词 '{keyword}' 失败: {e}")
                continue
        
        return all_videos[:max_results]


# 全局实例
video_match_service = VideoMatchService()
