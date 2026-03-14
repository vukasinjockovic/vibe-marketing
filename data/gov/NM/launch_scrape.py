#!/usr/bin/env python3
"""
Self-contained NM PSI scraper with file-based CAPTCHA solving.

Workflow:
  1. Creates an aiohttp session (gets JSESSIONID)
  2. Downloads CAPTCHA to captcha_solve.jpg
  3. Polls for answer in captcha_answer.txt (written externally)
  4. Authenticates and starts full scrape

This keeps the HTTP session alive throughout the entire process,
solving the session expiration problem.

Usage:
  # Start the scraper (it will wait for CAPTCHA answer)
  python3 launch_scrape.py [--limit N] [--resume]

  # In another terminal/process, write the CAPTCHA answer:
  echo "abc12" > data/gov/NM/captcha_answer.txt

  # The scraper will pick it up and start scraping automatically.
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
    CAPTCHA_DIR, build_prefix_list, Checkpoint, worker,
)

ANSWER_FILE = Path(__file__).parent / "captcha_answer.txt"
CAPTCHA_FILE = Path(__file__).parent / "captcha_solve.jpg"
READY_FILE = Path(__file__).parent / "captcha_ready.flag"


async def wait_for_answer(timeout: int = 300) -> str:
    """Poll for captcha_answer.txt to appear. Returns the answer string."""
    print(f"  Waiting for CAPTCHA answer in: {ANSWER_FILE}", flush=True)
    print(f"  Write the answer: echo 'xxxxx' > {ANSWER_FILE}", flush=True)
    print(f"  Timeout: {timeout}s", flush=True)

    start = time.time()
    while time.time() - start < timeout:
        if ANSWER_FILE.exists():
            answer = ANSWER_FILE.read_text().strip()
            if answer:
                # Delete the file so it doesn't get reused
                ANSWER_FILE.unlink()
                return answer
        await asyncio.sleep(1)

    raise TimeoutError(f"No CAPTCHA answer received within {timeout}s")


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="NM PSI Scraper with file-based CAPTCHA")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of prefixes")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--timeout", type=int, default=300, help="CAPTCHA answer timeout (seconds)")
    parser.add_argument("--answer", type=str, default="", help="Provide CAPTCHA answer directly (skip file polling)")
    args = parser.parse_args()

    # Clean up stale answer file
    if ANSWER_FILE.exists():
        ANSWER_FILE.unlink()
    if READY_FILE.exists():
        READY_FILE.unlink()

    print("=== NM PSI Contractor Scraper (Launch Mode) ===", flush=True)

    # Step 1: Create session
    session = PSISession(0)
    await session.create()
    print(f"  JSESSIONID: {session.jsessionid}", flush=True)

    # Step 2: Download CAPTCHA
    await session.download_captcha(CAPTCHA_FILE)
    print(f"  CAPTCHA saved to: {CAPTCHA_FILE}", flush=True)

    # Write ready flag so external process knows captcha is available
    READY_FILE.write_text(f"jsessionid={session.jsessionid}\ncaptcha={CAPTCHA_FILE}\n")
    print(f"  Ready flag written to: {READY_FILE}", flush=True)

    # Step 3: Get CAPTCHA answer
    if args.answer:
        answer = args.answer
        print(f"  Using provided answer: {answer}", flush=True)
    else:
        try:
            answer = await wait_for_answer(args.timeout)
        except TimeoutError as e:
            print(f"  ERROR: {e}", flush=True)
            await session.close()
            sys.exit(1)

    print(f"  Got CAPTCHA answer: {answer}", flush=True)

    # Step 4: Authenticate
    session.set_captcha(answer)
    ok = await session.authenticate()
    if not ok:
        print("  CAPTCHA verification FAILED!", flush=True)
        print("  The answer may be wrong or the session expired.", flush=True)
        await session.close()
        sys.exit(1)

    print("  Authenticated successfully!", flush=True)

    # Step 5: Build work list
    all_prefixes = build_prefix_list()
    checkpoint = Checkpoint(CHECKPOINT_FILE)
    if args.resume:
        checkpoint.load()
        print(f"  Resuming: {len(checkpoint.completed_prefixes)} prefixes already done", flush=True)

    remaining = [p for p in all_prefixes if p not in checkpoint.completed_prefixes]
    if args.limit > 0:
        remaining = remaining[:args.limit]
    print(f"  Total prefixes: {len(all_prefixes)}", flush=True)
    print(f"  Prefixes to process: {len(remaining)}", flush=True)

    if not remaining:
        print("  Nothing to do!", flush=True)
        await session.close()
        return

    if not checkpoint.started_at:
        checkpoint.started_at = datetime.now().isoformat()

    # Step 6: Set up CSV output
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

    # Step 7: Run the scraper
    print(f"\n  Starting scrape...", flush=True)
    await worker(0, session, prefix_queue, writer_lock, csv_writer,
                 csv_file, detail_sem, checkpoint, stats)

    # Step 8: Finalize
    checkpoint.save()
    csv_file.close()

    elapsed = time.time() - stats["start_time"]
    print(f"\n=== Scraping Complete ===", flush=True)
    print(f"  Records: {stats['details_fetched']}", flush=True)
    print(f"  Duration: {elapsed:.0f}s ({elapsed/3600:.1f}h)", flush=True)
    if elapsed > 0:
        print(f"  Rate: {stats['details_fetched']/elapsed:.1f}/s", flush=True)
    print(f"  Output: {OUTPUT_CSV}", flush=True)

    await session.close()

    # Clean up flag
    if READY_FILE.exists():
        READY_FILE.unlink()


if __name__ == "__main__":
    asyncio.run(main())
