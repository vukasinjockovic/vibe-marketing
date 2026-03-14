#!/usr/bin/env python3
"""
Run NM PSI scrape with a pre-created session.

Usage:
  python3 run_scrape.py <JSESSIONID> <CAPTCHA_ANSWER> [--limit N] [--resume]
"""
import asyncio
import csv
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scrape_nm_psi import (
    PSISession, CSV_COLUMNS, RAW_DIR, OUTPUT_CSV, CHECKPOINT_FILE,
    build_prefix_list, Checkpoint, worker,
)


async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("jsessionid", help="JSESSIONID cookie value")
    parser.add_argument("captcha", help="CAPTCHA answer")
    parser.add_argument("--limit", type=int, default=0, help="Limit prefixes")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    session = PSISession(0)
    await session.create(reuse_jsessionid=args.jsessionid)
    session.set_captcha(args.captcha)

    ok = await session.authenticate()
    if not ok:
        print("CAPTCHA FAILED!", flush=True)
        await session.close()
        return

    print(f"Authenticated! Session: {args.jsessionid[:16]}...", flush=True)

    all_prefixes = build_prefix_list()
    checkpoint = Checkpoint(CHECKPOINT_FILE)
    if args.resume:
        checkpoint.load()
        print(f"Resuming: {len(checkpoint.completed_prefixes)} done", flush=True)

    remaining = [p for p in all_prefixes if p not in checkpoint.completed_prefixes]
    if args.limit > 0:
        remaining = remaining[:args.limit]
    print(f"Prefixes to process: {len(remaining)}", flush=True)

    if not remaining:
        print("Nothing to do!")
        await session.close()
        return

    if not checkpoint.started_at:
        checkpoint.started_at = datetime.now().isoformat()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    file_mode = "a" if args.resume and OUTPUT_CSV.exists() else "w"
    csv_file = open(OUTPUT_CSV, file_mode, newline="", encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    if file_mode == "w":
        csv_writer.writerow(CSV_COLUMNS)
    writer_lock = asyncio.Lock()
    detail_sem = asyncio.Semaphore(5)

    prefix_queue = asyncio.Queue()
    for p in remaining:
        prefix_queue.put_nowait(p)

    stats = {
        "start_time": time.time(),
        "prefixes_done": 0,
        "details_fetched": 0,
        "total_prefixes": len(remaining),
    }

    await worker(0, session, prefix_queue, writer_lock, csv_writer,
                 csv_file, detail_sem, checkpoint, stats)

    checkpoint.save()
    csv_file.close()

    elapsed = time.time() - stats["start_time"]
    print(f"\nComplete! {stats['details_fetched']} records in {elapsed:.0f}s", flush=True)
    print(f"Output: {OUTPUT_CSV}", flush=True)
    await session.close()


if __name__ == "__main__":
    asyncio.run(main())
