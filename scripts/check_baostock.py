"""Local BaoStock A-share basic list check.

Run on your Windows machine:
    python scripts/check_baostock.py
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import pandas as pd


def _fetch_baostock(limit: int):
    import baostock as bs

    rows = []
    login = bs.login()
    try:
        if getattr(login, "error_code", "1") != "0":
            return pd.DataFrame(), f"login failed: {getattr(login, 'error_msg', '')}"

        result = bs.query_stock_basic()
        if getattr(result, "error_code", "1") != "0":
            return pd.DataFrame(), f"query_stock_basic failed: {getattr(result, 'error_msg', '')}"

        while result.next() and len(rows) < limit:
            item = result.get_row_data()
            rows.append(
                {
                    "code": item[0] if len(item) > 0 else "",
                    "name": item[1] if len(item) > 1 else "",
                    "ipoDate": item[2] if len(item) > 2 else "",
                    "outDate": item[3] if len(item) > 3 else "",
                    "type": item[4] if len(item) > 4 else "",
                    "status": item[5] if len(item) > 5 else "",
                }
            )
        return pd.DataFrame(rows), ""
    finally:
        try:
            bs.logout()
        except Exception:
            pass


def _run_with_timeout(timeout: int, limit: int):
    started = time.perf_counter()
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(_fetch_baostock, limit)
    try:
        frame, error = future.result(timeout=timeout)
        return frame, time.perf_counter() - started, error
    except TimeoutError:
        future.cancel()
        return None, time.perf_counter() - started, f"timeout after {timeout}s"
    except Exception as exc:
        return None, time.perf_counter() - started, repr(exc)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    frame, elapsed, error = _run_with_timeout(args.timeout, args.limit)
    print("data_source=BaoStock")
    print(f"data_status={'Live' if frame is not None and not frame.empty else 'Error'}")
    print(f"load_time={elapsed:.2f}s")
    if error:
        print(f"last_error={error}")
    if frame is None:
        print("rows=0")
        return 1

    print(f"rows={len(frame)}")
    print(f"columns={list(frame.columns)}")
    print(frame.head().to_string(index=False))
    return 0 if not frame.empty else 1


if __name__ == "__main__":
    sys.exit(main())
