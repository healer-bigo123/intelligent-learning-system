import sys
sys.stdout.reconfigure(encoding='utf-8')
import httpx

r = httpx.get(
    'http://localhost:8000/api/v1/study-materials/image-proxy?url=https://i0.hdslb.com/bfs/archive/2b0bd72359e4e129f0ad3452fb37b6befc08e064.jpg',
    timeout=10
)
with open("proxy_test.txt", "w", encoding="utf-8") as f:
    f.write(f"status: {r.status_code}\n")
    f.write(f"content-type: {r.headers.get('content-type')}\n")
    f.write(f"size: {len(r.content)}\n")
    f.write(f"body[:200]: {r.text[:200]}\n")
print("done")
