"""Local EastMoney Direct A-share realtime data check.

Run on your Windows machine:
    python scripts/check_eastmoney.py
"""

from __future__ import annotations

import argparse
import sys

from data.eastmoney_loader import load_eastmoney_a_share_spot


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    frame = load_eastmoney_a_share_spot(timeout=args.timeout)
    print(f"rows={len(frame)}")
    print(f"source={frame.attrs.get('data_source', 'EastMoney Direct')}")
    print(f"status={frame.attrs.get('data_status', 'Error')}")
    print(f"load_time={frame.attrs.get('load_time', 0):.2f}s")
    print(f"last_error={frame.attrs.get('last_error', '')}")
    print(f"request_url={frame.attrs.get('request_url', '')}")
    print(f"http_status={frame.attrs.get('http_status', '')}")
    print(f"raw_preview={frame.attrs.get('raw_preview', '')}")
    print(f"json_keys={frame.attrs.get('json_keys', [])}")
    print(f"diff_exists={frame.attrs.get('diff_exists', False)}")
    print(f"diff_length={frame.attrs.get('diff_length', 0)}")
    print(f"columns={list(frame.columns)}")
    print(frame.head().to_string(index=False))
    return 0 if len(frame) > 1000 else 1


if __name__ == "__main__":
    sys.exit(main())
