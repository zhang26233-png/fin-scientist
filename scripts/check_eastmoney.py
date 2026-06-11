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
    print(f"data_source={frame.attrs.get('data_source', 'EastMoney Direct')}")
    print(f"data_status={frame.attrs.get('data_status', 'Error')}")
    print(f"load_time={frame.attrs.get('load_time', 0):.2f}s")
    print(f"last_error={frame.attrs.get('last_error', '')}")
    print(f"updated_at={frame.attrs.get('updated_at', '')}")
    print(f"rows={len(frame)}")
    print(f"columns={list(frame.columns)}")
    print(frame.head().to_string(index=False))
    return 0 if len(frame) > 1000 else 1


if __name__ == "__main__":
    sys.exit(main())
