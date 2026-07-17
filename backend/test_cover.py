import sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
import requests

time.sleep(3)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

r = requests.get(
    "https://api.bilibili.com/x/web-interface/search/type",
    params={"search_type": "video", "keyword": "数学", "page": 1, "page_size": 2},
    headers=headers,
    timeout=10
)

with open("cover_test.txt", "w", encoding="utf-8") as f:
    f.write(f"status: {r.status_code}\n")
    f.write(f"content-type: {r.headers.get('content-type', 'N/A')}\n")
    f.write(f"body first 500: {r.text[:500]}\n")
    
    if r.status_code == 200 and "json" in r.headers.get("content-type", ""):
        d = r.json()
        f.write(f"code: {d.get('code')}\n")
        results = d.get("data", {}).get("result", [])
        f.write(f"results count: {len(results)}\n")
        for item in results[:2]:
            pic = item.get("pic", "")
            title = item.get("title", "")
            full = "https:" + pic if pic.startswith("//") else pic
            f.write(f"title: {title[:80]}\n")
            f.write(f"pic: {pic}\n")
            f.write(f"full: {full}\n")
            f.write("---\n")

print("done")
