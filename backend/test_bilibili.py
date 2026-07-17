import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
import time

# 等待几秒让B站限流解除
print("等待5秒...")
time.sleep(5)

from app.core.video_search import video_match_service

async def test():
    result = await video_match_service.match_videos(
        {"title": "函数", "subject": "数学", "knowledge_point": "函数", "tags": ""},
        max_results=3
    )
    print(f"匹配到 {len(result)} 个视频:")
    for v in result:
        print(f"  - {v['title'][:50]} | {v['bvid']} | play:{v['play_count']}")

asyncio.run(test())
