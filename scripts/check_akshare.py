"""Local AkShare A-share realtime data check.

Run on your Windows machine:
    python scripts/check_akshare.py
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError


def _run_with_timeout(timeout: int):
    def fetch():
        import akshare as ak

        return ak.stock_zh_a_spot_em()

    started = time.perf_counter()
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(fetch)
    try:
        frame = future.result(timeout=timeout)
        elapsed = time.perf_counter() - started
        return frame, elapsed, ""
    except TimeoutError:
        future.cancel()
        return None, time.perf_counter() - started, f"timeout after {timeout}s"
    except Exception as exc:
        return None, time.perf_counter() - started, repr(exc)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    frame, elapsed, error = _run_with_timeout(args.timeout)
    print(f"data_source=AkShare")
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
