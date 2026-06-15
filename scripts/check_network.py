"""Local network reachability check for free A-share data sources.

Run on your Windows machine:
    python scripts/check_network.py
"""

from __future__ import annotations

import socket
import sys
import time
import urllib.request


HTTP_TARGETS = [
    "https://web.ifzq.gtimg.cn",
    "https://qt.gtimg.cn",
    "https://vip.stock.finance.sina.com.cn",
    "https://hq.sinajs.cn",
    "https://push2.eastmoney.com",
    "https://quote.eastmoney.com",
    "https://www.baidu.com",
]

TCP_TARGETS = [
    ("web.ifzq.gtimg.cn", 443),
    ("qt.gtimg.cn", 443),
    ("vip.stock.finance.sina.com.cn", 443),
    ("hq.sinajs.cn", 443),
    ("push2.eastmoney.com", 443),
    ("quote.eastmoney.com", 443),
    ("baostock.com", 80),
]


def check_http(url: str, timeout: int = 5) -> tuple[bool, str, float]:
    started = time.perf_counter()
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "FinScientistNetworkCheck/1.0"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return True, f"HTTP {response.status}", time.perf_counter() - started
    except Exception as exc:
        return False, repr(exc), time.perf_counter() - started


def check_tcp(host: str, port: int, timeout: int = 5) -> tuple[bool, str, float]:
    started = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "connected", time.perf_counter() - started
    except Exception as exc:
        return False, repr(exc), time.perf_counter() - started


def main() -> int:
    ok_count = 0
    total = 0

    print("HTTP checks")
    for url in HTTP_TARGETS:
        ok, message, elapsed = check_http(url)
        total += 1
        ok_count += int(ok)
        print(f"{url} | ok={ok} | time={elapsed:.2f}s | {message}")

    print("\nTCP checks")
    for host, port in TCP_TARGETS:
        ok, message, elapsed = check_tcp(host, port)
        total += 1
        ok_count += int(ok)
        print(f"{host}:{port} | ok={ok} | time={elapsed:.2f}s | {message}")

    print(f"\nsummary={ok_count}/{total} reachable")
    return 0 if ok_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
