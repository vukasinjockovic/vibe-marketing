#!/usr/bin/env python3
"""
Single-process NM PSI scraper.
Creates session, solves captcha inline, and scrapes.

Usage:
  python3 go_scrape.py <captcha_answer> [--limit N] [--resume]

Workflow:
  1. python3 -c "..." to create session + download captcha
  2. Read captcha image
  3. python3 go_scrape.py <answer> --limit 5  (test)
  4. python3 go_scrape.py <answer>  (full run)
"""
import argparse
import asyncio
import csv
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scrape_nm_psi import (
    PSISession, CSV_COLUMNS, RAW_DIR, OUTPUT_CSV, CHECKPOINT_FILE,
    build_prefix_list, Checkpoint, worker, CAPTCHA_DIR,
)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("captcha", help="CAPTCHA answer")
    parser.add_argument("--jsessionid", "-j", help="Reuse existing JSESSIONID")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    session = PSISession(0)
    if args.jsessionid:
        # Reuse existing session
        await session.create(reuse_jsessionid=args.jsessionid)
        print(f"Reusing session: {args.jsessionid[:16]}...", flush=True)
    else:
        # Create fresh session
        await session.create()
        print(f"New session: {session.jsessionid}", flush=True)
        captcha_path = CAPTCHA_DIR / "captcha_verify.jpg"
        await session.download_captcha(captcha_path)

    # Set and verify captcha
    session.set_captcha(args.captcha)
    ok = await session.authenticate()
    if not ok:
        print("CAPTCHA FAILED! Session may have expired.", flush=True)
        print("Re-run: create session + get captcha, solve, then run immediately.", flush=True)
        await session.close()
        sys.exit(1)

    print("Authenticated!", flush=True)

    # Build work list
    all_prefixes = build_prefix_list()
    checkpoint = Checkpoint(CHECKPOINT_FILE)
    if args.resume:
        checkpoint.load()
        print(f"Resuming: {len(checkpoint.completed_prefixes)} prefixes done", flush=True)

    remaining = [p for p in all_prefixes if p not in checkpoint.completed_prefixes]
    if args.limit > 0:
        remaining = remaining[:args.limit]
    print(f"Prefixes to process: {len(remaining)}", flush=True)

    if not remaining:
        print("Nothing to do!", flush=True)
        await session.close()
        return

    if not checkpoint.started_at:
        checkpoint.started_at = datetime.now().isoformat()

    # Set up CSV output
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

    # Run the worker
    await worker(0, session, prefix_queue, writer_lock, csv_writer,
                 csv_file, detail_sem, checkpoint, stats)

    checkpoint.save()
    csv_file.close()

    elapsed = time.time() - stats["start_time"]
    print(f"\nComplete!", flush=True)
    print(f"  Records: {stats['details_fetched']}", flush=True)
    print(f"  Duration: {elapsed:.0f}s ({elapsed/3600:.1f}h)", flush=True)
    print(f"  Rate: {stats['details_fetched']/elapsed:.1f}/s", flush=True)
    print(f"  Output: {OUTPUT_CSV}", flush=True)

    await session.close()


if __name__ == "__main__":
    asyncio.run(main())
