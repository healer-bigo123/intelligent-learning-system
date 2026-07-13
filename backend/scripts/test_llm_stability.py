"""
LLM 稳定性测试脚本
连续调用 LLM 10 次，记录响应时间、成功率、内容摘要
输出统计报告到控制台和 CSV 文件

使用方法：
    cd backend
    venv\Scripts\activate
    python scripts/test_llm_stability.py
"""
import sys
import os
import time
import csv
from datetime import datetime

# 确保 backend 目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.llm_client import (
    LLMConfig, ModelProvider, ArkClient, Message, LLMResponse
)
from app.core.config import settings

TEST_QUESTION = "请用一句话介绍勾股定理"
CALL_COUNT = 10
CSV_OUTPUT = os.path.join(os.path.dirname(__file__), "llm_stability_report.csv")


def main():
    print("=" * 60)
    print("  LLM 稳定性测试")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  模型: {settings.VOLCES_MODEL}")
    print(f"  测试次数: {CALL_COUNT}")
    print(f"  测试问题: {TEST_QUESTION}")
    print("=" * 60)

    # 初始化 LLM 客户端
    if not settings.VOLCES_API_KEY:
        print("\n[ERROR] 未配置 VOLCES_API_KEY，请检查 .env 文件")
        sys.exit(1)

    config = LLMConfig(
        provider=ModelProvider.VOLCES,
        api_key=settings.VOLCES_API_KEY,
        base_url=settings.VOLCES_BASE_URL,
        model_name=settings.VOLCES_MODEL,
        temperature=0.7,
        max_tokens=2048,
        timeout=30,
    )
    client = ArkClient(config)

    results = []
    success_count = 0
    fail_count = 0
    response_times = []

    print(f"\n{'序号':<6} {'状态':<8} {'响应时间(ms)':<16} {'内容前50字符'}")
    print("-" * 60)

    for i in range(1, CALL_COUNT + 1):
        start_time = time.time()
        try:
            response = client.generate(
                [Message(role="user", content=TEST_QUESTION)]
            )
            elapsed = (time.time() - start_time) * 1000  # 转换为毫秒

            if response.error:
                status = "失败"
                fail_count += 1
                content_preview = f"[错误] {response.error}"
                status_code = "FAIL"
            else:
                status = "成功"
                success_count += 1
                response_times.append(elapsed)
                content_preview = response.content[:50].replace("\n", " ")
                status_code = "OK"

            print(f"{i:<6} {status:<8} {elapsed:<16.0f} {content_preview}")

            results.append({
                "序号": i,
                "状态": status_code,
                "响应时间_ms": round(elapsed, 0),
                "内容前50字符": content_preview,
                "错误信息": response.error or "",
            })

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            fail_count += 1
            status = "失败"
            error_msg = str(e)
            print(f"{i:<6} {status:<8} {elapsed:<16.0f} [异常] {error_msg[:50]}")

            results.append({
                "序号": i,
                "状态": "FAIL",
                "响应时间_ms": round(elapsed, 0),
                "内容前50字符": f"[异常] {error_msg[:50]}",
                "错误信息": error_msg,
            })

    # 统计汇总
    print("\n" + "=" * 60)
    print("  统计汇总")
    print("=" * 60)
    print(f"  成功率:       {success_count}/{CALL_COUNT} ({success_count/CALL_COUNT*100:.0f}%)")
    if response_times:
        print(f"  平均响应时间: {sum(response_times)/len(response_times):.0f} ms")
        print(f"  最长响应时间: {max(response_times):.0f} ms")
        print(f"  最短响应时间: {min(response_times):.0f} ms")
    print(f"  成功次数:     {success_count}")
    print(f"  失败次数:     {fail_count}")

    if fail_count > 0:
        print(f"\n  失败原因汇总:")
        for r in results:
            if r["错误信息"]:
                print(f"    第{r['序号']}次: {r['错误信息'][:100]}")

    # 保存 CSV
    with open(CSV_OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["序号", "状态", "响应时间_ms", "内容前50字符", "错误信息"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n  CSV 报告已保存: {CSV_OUTPUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()