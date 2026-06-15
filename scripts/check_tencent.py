"""Local Tencent realtime A-share data check.

Run on your Windows machine:
    python scripts/check_tencent.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.tencent_loader import load_tencent_a_share_spot


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=10)
    args = parser.parse_args()

    frame = load_tencent_a_share_spot(timeout=args.timeout)
    print(f"rows={len(frame)}")
    print(f"source={frame.attrs.get('data_source', 'Tencent Realtime')}")
    print(f"status={frame.attrs.get('data_status', 'Error')}")
    print(f"load_time={frame.attrs.get('load_time', 0):.2f}s")
    print(f"last_error={frame.attrs.get('last_error', '')}")
    print(f"endpoint_attempts={frame.attrs.get('endpoint_attempts', [])}")
    print(f"columns={list(frame.columns)}")
    print(frame.head().to_string(index=False))
    return 0 if len(frame) > 1000 else 1


if __name__ == "__main__":
    sys.exit(main())
