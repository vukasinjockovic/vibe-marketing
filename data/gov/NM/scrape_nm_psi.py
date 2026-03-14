#!/usr/bin/env python3
"""
Scrape New Mexico CID contractor licenses from PSI Exams portal.

Source: https://public.psiexams.com/search.jsp?cid=445
Target: CSV at data/gov/NM/raw/nm_psi_all.csv

Strategy:
  1. Create N parallel sessions, solve CAPTCHA once per session (manual)
  2. Build a prefix tree of license-number prefixes (3-digit or 4-digit)
     where no single prefix returns >= 300 records (the server cap)
  3. For each prefix, paginate through search results (20 per page)
  4. For each result row, fetch the detail page for full data
  5. Write all records to CSV with checkpoint tracking

CAPTCHA handling:
  - On startup, creates sessions, downloads CAPTCHAs to data/gov/NM/captcha_*.jpg
  - Waits for user to provide answers via --captcha-answers "ans1,ans2,..."
  - Or tries OCR automatically with --auto-ocr

Usage:
  # Step 1: Generate CAPTCHA images (interactive)
  python3 scrape_nm_psi.py --prepare-sessions 5

  # Step 2: Run with manually solved CAPTCHAs
  python3 scrape_nm_psi.py --captcha-answers "abc12,def34,ghi56,jkl78,mno90"

  # Step 3: Resume from checkpoint
  python3 scrape_nm_psi.py --resume

  # Quick test with one session and limited prefixes
  python3 scrape_nm_psi.py --captcha-answers "abc12" --limit-prefixes 10
"""

import argparse
import asyncio
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
RAW_DIR = SCRIPT_DIR / "raw"
OUTPUT_CSV = RAW_DIR / "nm_psi_all.csv"
CHECKPOINT_FILE = SCRIPT_DIR / "scrape_checkpoint.json"
CAPTCHA_DIR = SCRIPT_DIR

BASE_URL = "https://public.psiexams.com"
SEARCH_URL = f"{BASE_URL}/searchLicensee.do"
DETAIL_URL = f"{BASE_URL}/licensee/showBusinessLicensee.do"
CAPTCHA_URL = f"{BASE_URL}/simplecaptcha.jpg"
SEARCH_PAGE_URL = f"{BASE_URL}/search.jsp?cid=445"

COMPANY_TYPE = "445"  # Contractor
RECORDS_PER_PAGE = 20
MAX_RESULTS_CAP = 300  # Server-side result limit

# Concurrency settings
MAX_CONCURRENT_SEARCHES = 8
MAX_CONCURRENT_DETAILS = 15
DETAIL_SEMAPHORE_PER_SESSION = 5

# Retry settings
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0

# Rate limiting
SEARCH_DELAY = 0.05  # seconds between searches per session
DETAIL_DELAY = 0.02  # seconds between detail fetches

# CSV columns
CSV_COLUMNS = [
    "license_number", "company_name", "phone", "license_status",
    "issue_date", "expiry_date", "volume",
    "street", "city", "state", "zip_code",
    "qp_name", "qp_certificate_no", "qp_classification",
    "qp_attach_date", "qp_status",
    "license_id", "license_application_id", "company_id",
]


# ---------------------------------------------------------------------------
# Prefix tree builder
# ---------------------------------------------------------------------------

def build_prefix_list() -> list[str]:
    """Build the list of license-number prefixes to search.

    Uses survey data to determine which prefixes need drill-down.
    Non-capped 2-digit prefixes are used directly.
    Capped 2-digit prefixes drill into 3-digit.
    Capped 3-digit prefixes drill into 4-digit.
    Ranges with no data are skipped.
    """
    # 2-digit prefixes that are NOT capped (< 300 results each)
    uncapped_2d = [
        10, 11, 12, 13, 15, 16, 17,  # 14,18,19 are capped
        44, 48, 49,  # sparse mid-range
        62, 63, 64, 65, 66, 67, 68, 69,
        70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
        95, 96, 97, 98, 99,
    ]

    # 3-digit prefixes that are NOT capped (from capped 2-digit parents)
    # These are ALL 3-digit prefixes from the survey that had < 300 results.
    # We enumerate them programmatically from known capped 2-digit parents.
    capped_2d = [
        14, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
        30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
        40, 41, 42,
        50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61,
        80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
        90, 91, 92, 93, 94,
    ]

    # 3-digit prefixes that ARE capped (need 4-digit drill-down)
    capped_3d = [
        350, 351, 352, 353, 354, 355, 356, 357, 358, 359,
        360, 362, 363, 365, 366, 367,
        376, 377, 378,
        380, 381, 382, 383, 384, 385, 386, 387, 388, 389,
        390, 391, 392, 397, 399,
        401, 402, 406, 421,
    ]
    capped_3d_set = set(capped_3d)

    prefixes = []

    # Add uncapped 2-digit prefixes
    for p in uncapped_2d:
        prefixes.append(str(p))

    # Add 3-digit prefixes for capped 2-digit parents
    for parent in capped_2d:
        for d in range(10):
            p3 = parent * 10 + d
            if p3 in capped_3d_set:
                # This 3-digit is capped, drill to 4-digit
                for dd in range(10):
                    prefixes.append(str(p3 * 10 + dd))
            else:
                prefixes.append(str(p3))

    return prefixes


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

class PSISession:
    """Manages a single authenticated session to PSI Exams."""

    def __init__(self, session_id: int):
        self.session_id = session_id
        self.jsessionid: Optional[str] = None
        self.captcha_answer: Optional[str] = None
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.authenticated = False
        self.search_count = 0
        self.detail_count = 0
        self._last_num_records = 300  # Default for pagination

    async def create(self, reuse_jsessionid: Optional[str] = None):
        """Create HTTP session and get JSESSIONID.

        If reuse_jsessionid is provided, sets that cookie instead of
        creating a fresh session. This allows reusing a session where
        the CAPTCHA was already downloaded.
        """
        jar = aiohttp.CookieJar()
        self.http_session = aiohttp.ClientSession(cookie_jar=jar)

        if reuse_jsessionid:
            # Reuse existing session - set cookie manually
            from http.cookies import Morsel
            from yarl import URL
            jar.update_cookies(
                {"JSESSIONID": reuse_jsessionid},
                URL(BASE_URL)
            )
            self.jsessionid = reuse_jsessionid
        else:
            # Hit search page to get session cookie
            async with self.http_session.get(SEARCH_PAGE_URL) as resp:
                pass  # Cookie is set automatically

            # Extract JSESSIONID
            for cookie in self.http_session.cookie_jar:
                if cookie.key == "JSESSIONID":
                    self.jsessionid = cookie.value
                    break

            if not self.jsessionid:
                raise RuntimeError(f"Session {self.session_id}: Failed to get JSESSIONID")

    async def download_captcha(self, save_path: Path) -> bytes:
        """Download CAPTCHA image."""
        async with self.http_session.get(CAPTCHA_URL) as resp:
            data = await resp.read()
            save_path.write_bytes(data)
            return data

    def set_captcha(self, answer: str):
        """Set the solved CAPTCHA answer."""
        self.captcha_answer = answer

    async def authenticate(self) -> bool:
        """Verify CAPTCHA works by performing a test search.

        Uses the same form structure as a real search to verify the
        captcha answer works. Returns True if the server accepted the
        CAPTCHA (regardless of whether results were found).

        Detection: If the response does NOT contain the CAPTCHA form
        fields (captchaAnswer, Submit2), the CAPTCHA was accepted.
        A wrong CAPTCHA redirects back to the search form.
        """
        if not self.captcha_answer:
            return False

        data = {
            "isCompany": "individual",
            "requestType": "2",
            "individualOrCompany": "NO",
            "companyType": COMPANY_TYPE,
            "busLicenseNumber": "99",
            "businessName": "",
            "businessCity": "",
            "businessZipCode": "",
            "captchaAnswer": self.captcha_answer,
            "Submit2": "Search",
        }
        try:
            async with self.http_session.post(SEARCH_URL, data=data,
                                              timeout=aiohttp.ClientTimeout(total=30)) as resp:
                text = await resp.text()
                # Primary check: results page with records
                if "Displaying" in text and "records" in text:
                    self.authenticated = True
                    return True
                # Secondary: 0-result page (says "No Records Found for [...]")
                if "No Records Found" in text or "No record found" in text:
                    self.authenticated = True
                    return True
                # Tertiary: if the CAPTCHA form is NOT in the response,
                # the server accepted our search (just returned unexpected format)
                if "captchaAnswer" not in text and "Submit2" not in text:
                    self.authenticated = True
                    return True
        except Exception:
            pass
        return False

    async def search(self, prefix: str, start: int = 1) -> tuple[int, list[dict]]:
        """Search for contractors by license number prefix.

        Returns (total_count, list_of_result_dicts).
        Each dict has: license_number, company_name, address, city_zip,
                       expiry_date, status, license_id, license_application_id

        IMPORTANT: The PSI server treats requests differently:
          - First page (start=1): Must include full search params + captchaAnswer
            but NOT start/RecordPerPage (those trigger pagination mode)
          - Subsequent pages (start>1): Must include start/RecordPerPage/NumOfRecords
            but NOT the search params (server uses cached search context)
        """
        if start <= 1:
            # New search - include full form data, NO start/RecordPerPage
            data = {
                "isCompany": "individual",
                "requestType": "2",
                "individualOrCompany": "NO",
                "companyType": COMPANY_TYPE,
                "busLicenseNumber": prefix,
                "businessName": "",
                "businessCity": "",
                "businessZipCode": "",
                "captchaAnswer": self.captcha_answer,
                "Submit2": "Search",
            }
        else:
            # Pagination - include start/RecordPerPage, minimal params
            data = {
                "requestType": "2",
                "individualOrCompany": "NO",
                "start": str(start),
                "RecordPerPage": str(RECORDS_PER_PAGE),
                "NumOfRecords": str(self._last_num_records or 300),
            }

        for attempt in range(MAX_RETRIES):
            try:
                async with self.http_session.post(SEARCH_URL, data=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    text = await resp.text()
                    self.search_count += 1
                    total, results = self._parse_search_results(text)
                    # Cache NumOfRecords for pagination
                    if start <= 1 and total > 0:
                        self._last_num_records = total
                    return total, results
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    print(f"  [S{self.session_id}] Search failed prefix={prefix} start={start}: {e}")
                    return 0, []

    def _parse_search_results(self, html: str) -> tuple[int, list[dict]]:
        """Parse search results HTML into structured data."""
        soup = BeautifulSoup(html, "lxml")

        # Extract total count
        total = 0
        m = re.search(r"Displaying\s+\d+\s+to\s+\d+\s+of\s+(\d+)\s+records", html)
        if m:
            total = int(m.group(1))
        else:
            return 0, []

        results = []
        rows = soup.find_all("tr", class_="rowalt")
        for row in rows:
            tds = row.find_all("td")
            if len(tds) < 7:
                continue

            # Extract license_id and license_application_id from onclick
            license_id = ""
            license_app_id = ""
            link = tds[2].find("a")
            if link and link.get("onclick"):
                onclick = link["onclick"]
                id_match = re.search(r'licenseId:\s*"(\d+)"', onclick)
                app_match = re.search(r'licenseApplicationId:\s*"(\d+)"', onclick)
                if id_match:
                    license_id = id_match.group(1)
                if app_match:
                    license_app_id = app_match.group(1)

            company_name = link.text.strip() if link else tds[2].get_text(strip=True)

            results.append({
                "license_number": tds[1].get_text(strip=True),
                "company_name": company_name,
                "address": tds[3].get_text(strip=True),
                "city_zip": tds[4].get_text(strip=True),
                "expiry_date": tds[5].get_text(strip=True),
                "status": tds[6].get_text(strip=True),
                "license_id": license_id,
                "license_application_id": license_app_id,
            })

        return total, results

    async def fetch_detail(self, license_id: str, license_app_id: str) -> Optional[dict]:
        """Fetch detail page for a single contractor.

        Returns dict with: company_name, license_number, phone, status,
                          issue_date, expiry_date, volume, street, city,
                          state, zip_code, qp_* fields, company_id
        """
        data = {
            "licenseId": license_id,
            "licenseApplicationId": license_app_id,
        }

        for attempt in range(MAX_RETRIES):
            try:
                async with self.http_session.post(DETAIL_URL, data=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    text = await resp.text()
                    self.detail_count += 1
                    return self._parse_detail(text, license_id)
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    print(f"  [S{self.session_id}] Detail failed id={license_id}: {e}")
                    return None

    def _parse_detail(self, html: str, license_id: str) -> Optional[dict]:
        """Parse detail page HTML."""
        soup = BeautifulSoup(html, "lxml")

        # Find "Company Details" section
        result = {
            "company_name": "",
            "license_number": "",
            "phone": "",
            "license_status": "",
            "issue_date": "",
            "expiry_date": "",
            "volume": "",
            "street": "",
            "city": "",
            "state": "",
            "zip_code": "",
            "company_id": "",
            "qp_name": "",
            "qp_certificate_no": "",
            "qp_classification": "",
            "qp_attach_date": "",
            "qp_status": "",
        }

        # Extract from hidden form fields (most reliable)
        hidden_form = soup.find("form", {"name": "hiddenform"})
        if hidden_form:
            for inp in hidden_form.find_all("input", {"type": "hidden"}):
                name = inp.get("name", "")
                val = inp.get("value", "").strip()
                if name == "businessNm":
                    result["company_name"] = val
                elif name == "licenseNumber":
                    result["license_number"] = val
                elif name == "street":
                    result["street"] = val
                elif name == "city":
                    result["city"] = val
                elif name == "state":
                    result["state"] = val
                elif name == "zipCode":
                    result["zip_code"] = val
                elif name == "companyId":
                    result["company_id"] = val

        # Parse the visible table for phone, dates, volume, status
        # The detail table has rows with label/value pairs
        all_tds = soup.find_all("td", class_="fieldlabel")
        for i, td in enumerate(all_tds):
            text = td.get_text(strip=True)

            if text == "Phone Number" and i + 1 < len(all_tds):
                result["phone"] = all_tds[i + 1].get_text(strip=True)
            elif text == "License Status" and i + 1 < len(all_tds):
                # Status is in the next <td> which may not have class fieldlabel
                next_td = td.find_next_sibling("td")
                if next_td:
                    result["license_status"] = next_td.get_text(strip=True)
            elif text == "Issue Date" and i + 1 < len(all_tds):
                result["issue_date"] = all_tds[i + 1].get_text(strip=True)
            elif text == "Expiry Date":
                next_td = td.find_next_sibling("td")
                if next_td:
                    result["expiry_date"] = next_td.get_text(strip=True)
            elif text == "Volume" and i + 1 < len(all_tds):
                result["volume"] = all_tds[i + 1].get_text(strip=True)

        # Fallback: parse Company Name from visible table
        if not result["company_name"]:
            for td in all_tds:
                if td.get_text(strip=True) == "Company Name":
                    next_td = td.find_next_sibling("td")
                    if next_td:
                        result["company_name"] = next_td.get_text(strip=True)
                        break

        # Fallback: parse License Number from visible table
        if not result["license_number"]:
            for td in all_tds:
                if td.get_text(strip=True) == "License Number":
                    next_td = td.find_next_sibling("td")
                    if next_td:
                        result["license_number"] = next_td.get_text(strip=True)
                        break

        # Parse QP (Qualifying Party) details
        # QP table has headers: Name, Certificate No, Classification, Attach Date, Status
        qp_heading = soup.find(string=re.compile(r"QP Details"))
        if qp_heading:
            # Find the QP table rows
            qp_section = qp_heading.find_parent("tr")
            if qp_section:
                qp_table_row = qp_section.find_next_sibling("tr")
                if qp_table_row:
                    qp_table = qp_table_row.find("table")
                    if qp_table:
                        qp_data_rows = qp_table.find_all("tr", style=True)
                        if qp_data_rows:
                            # Take the first QP (there may be multiple)
                            qp_row = qp_data_rows[0]
                            qp_tds = qp_row.find_all("td")
                            if len(qp_tds) >= 5:
                                qp_link = qp_tds[0].find("a")
                                result["qp_name"] = qp_link.text.strip() if qp_link else qp_tds[0].get_text(strip=True)
                                result["qp_certificate_no"] = qp_tds[1].get_text(strip=True)
                                result["qp_classification"] = qp_tds[2].get_text(strip=True)
                                result["qp_attach_date"] = qp_tds[3].get_text(strip=True)
                                result["qp_status"] = qp_tds[4].get_text(strip=True)

        return result

    async def close(self):
        """Close the HTTP session."""
        if self.http_session:
            await self.http_session.close()


# ---------------------------------------------------------------------------
# Checkpoint management
# ---------------------------------------------------------------------------

class Checkpoint:
    """Track scraping progress for resume capability."""

    def __init__(self, path: Path):
        self.path = path
        self.completed_prefixes: set[str] = set()
        self.total_records = 0
        self.total_details = 0
        self.started_at = ""

    def load(self):
        if self.path.exists():
            data = json.loads(self.path.read_text())
            self.completed_prefixes = set(data.get("completed_prefixes", []))
            self.total_records = data.get("total_records", 0)
            self.total_details = data.get("total_details", 0)
            self.started_at = data.get("started_at", "")

    def save(self):
        data = {
            "completed_prefixes": sorted(self.completed_prefixes),
            "total_records": self.total_records,
            "total_details": self.total_details,
            "started_at": self.started_at,
            "last_saved": datetime.now().isoformat(),
        }
        self.path.write_text(json.dumps(data, indent=2))

    def mark_complete(self, prefix: str, detail_count: int):
        self.completed_prefixes.add(prefix)
        self.total_details += detail_count
        # Save periodically
        if len(self.completed_prefixes) % 10 == 0:
            self.save()


# ---------------------------------------------------------------------------
# Main scraping logic
# ---------------------------------------------------------------------------

async def scrape_prefix(session: PSISession, prefix: str,
                        writer_lock: asyncio.Lock, csv_writer,
                        detail_sem: asyncio.Semaphore,
                        checkpoint: Checkpoint) -> int:
    """Scrape all records for a single license number prefix.

    Returns number of detail records fetched.
    """
    # First search to get total count
    total, results = await session.search(prefix, start=1)
    if total == 0:
        checkpoint.mark_complete(prefix, 0)
        return 0

    all_results = list(results)

    # Paginate if needed (sequential to preserve server-side search context)
    if total > RECORDS_PER_PAGE:
        pages = (total + RECORDS_PER_PAGE - 1) // RECORDS_PER_PAGE
        for page in range(1, pages):  # page 0 already fetched
            start = page * RECORDS_PER_PAGE + 1
            await asyncio.sleep(SEARCH_DELAY)
            page_total, page_results = await session.search(prefix, start=start)
            if not page_results:
                break  # No more results
            all_results.extend(page_results)

    # Dedup by license_id
    seen_ids = set()
    unique_results = []
    for r in all_results:
        lid = r.get("license_id")
        if lid and lid not in seen_ids:
            seen_ids.add(lid)
            unique_results.append(r)

    # Fetch details for each result
    detail_count = 0
    for search_row in unique_results:
        lid = search_row.get("license_id", "")
        laid = search_row.get("license_application_id", "")
        if not lid:
            continue

        async with detail_sem:
            await asyncio.sleep(DETAIL_DELAY)
            detail = await session.fetch_detail(lid, laid)

        if detail:
            # Merge search row data as fallback
            if not detail.get("license_number"):
                detail["license_number"] = search_row.get("license_number", "")
            if not detail.get("company_name"):
                detail["company_name"] = search_row.get("company_name", "")
            if not detail.get("license_status"):
                detail["license_status"] = search_row.get("status", "")
            if not detail.get("expiry_date"):
                detail["expiry_date"] = search_row.get("expiry_date", "")

            detail["license_id"] = lid
            detail["license_application_id"] = laid

            # Write to CSV
            async with writer_lock:
                row = [detail.get(col, "") for col in CSV_COLUMNS]
                csv_writer.writerow(row)

            detail_count += 1

    checkpoint.mark_complete(prefix, detail_count)
    return detail_count


async def worker(worker_id: int, session: PSISession,
                 prefix_queue: asyncio.Queue,
                 writer_lock: asyncio.Lock, csv_writer,
                 csv_file,
                 detail_sem: asyncio.Semaphore,
                 checkpoint: Checkpoint,
                 stats: dict):
    """Worker that processes prefixes from the queue."""
    while True:
        try:
            prefix = prefix_queue.get_nowait()
        except asyncio.QueueEmpty:
            break

        try:
            count = await scrape_prefix(
                session, prefix, writer_lock, csv_writer,
                detail_sem, checkpoint
            )
            stats["prefixes_done"] += 1
            stats["details_fetched"] += count

            # Flush CSV to disk every 10 prefixes
            if stats["prefixes_done"] % 10 == 0:
                async with writer_lock:
                    csv_file.flush()

            # Progress
            elapsed = time.time() - stats["start_time"]
            rate = stats["details_fetched"] / elapsed if elapsed > 0 else 0
            pct = stats["prefixes_done"] / stats["total_prefixes"] * 100
            print(f"  [W{worker_id}] Prefix {prefix}: {count} details | "
                  f"Progress: {stats['prefixes_done']}/{stats['total_prefixes']} ({pct:.1f}%) | "
                  f"Total: {stats['details_fetched']} @ {rate:.1f}/s",
                  flush=True)

        except Exception as e:
            print(f"  [W{worker_id}] ERROR on prefix {prefix}: {e}", flush=True)

        prefix_queue.task_done()


async def prepare_sessions(num_sessions: int):
    """Create sessions and download CAPTCHAs for manual solving."""
    sessions = []
    for i in range(num_sessions):
        s = PSISession(i)
        await s.create()
        captcha_path = CAPTCHA_DIR / f"captcha_{i}.jpg"
        await s.download_captcha(captcha_path)
        sessions.append(s)
        print(f"  Session {i}: JSESSIONID={s.jsessionid}, captcha saved to {captcha_path}")

    # Save session info for later use
    session_info = []
    for s in sessions:
        session_info.append({
            "session_id": s.session_id,
            "jsessionid": s.jsessionid,
        })
    info_path = SCRIPT_DIR / "session_info.json"
    info_path.write_text(json.dumps(session_info, indent=2))
    print(f"\n  Session info saved to {info_path}")
    print(f"  Solve the CAPTCHAs in {CAPTCHA_DIR}/captcha_*.jpg")
    print(f"  Then run with: --captcha-answers 'answer0,answer1,...'")

    for s in sessions:
        await s.close()


async def run_scrape(captcha_answers: list[str], limit_prefixes: int = 0,
                     resume: bool = False):
    """Main scraping entry point."""
    num_sessions = len(captcha_answers)
    print(f"=== NM PSI Contractor Scraper ===")
    print(f"  Sessions: {num_sessions}")

    # Load session info (from --prepare-sessions)
    info_path = SCRIPT_DIR / "session_info.json"
    if info_path.exists():
        session_info = json.loads(info_path.read_text())
        print(f"  Reusing {len(session_info)} prepared sessions")
        sessions = []
        for i, info in enumerate(session_info[:num_sessions]):
            s = PSISession(i)
            await s.create(reuse_jsessionid=info["jsessionid"])
            s.set_captcha(captcha_answers[i])
            sessions.append(s)
    else:
        # Create fresh sessions (download captcha per session)
        print("  Creating fresh sessions...")
        sessions = []
        for i in range(num_sessions):
            s = PSISession(i)
            await s.create()
            captcha_path = CAPTCHA_DIR / f"captcha_{i}.jpg"
            await s.download_captcha(captcha_path)
            s.set_captcha(captcha_answers[i])
            sessions.append(s)

    # Authenticate sessions sequentially with delay to avoid server overload
    print("  Authenticating sessions (sequential)...")
    valid_sessions = []
    for s in sessions:
        ok = await s.authenticate()
        if ok:
            print(f"    Session {s.session_id}: OK")
            valid_sessions.append(s)
        else:
            print(f"    Session {s.session_id}: FAILED (captcha may be wrong)")
            await s.close()
        await asyncio.sleep(1.0)  # Delay between auth requests

    sessions = valid_sessions
    if not sessions:
        print("  ERROR: No authenticated sessions. Check CAPTCHA answers.")
        return

    # Build prefix list
    all_prefixes = build_prefix_list()
    print(f"  Total prefixes to search: {len(all_prefixes)}")

    # Load checkpoint
    checkpoint = Checkpoint(CHECKPOINT_FILE)
    if resume:
        checkpoint.load()
        print(f"  Resuming: {len(checkpoint.completed_prefixes)} prefixes already done")

    # Filter out completed prefixes
    remaining = [p for p in all_prefixes if p not in checkpoint.completed_prefixes]
    if limit_prefixes > 0:
        remaining = remaining[:limit_prefixes]
    print(f"  Prefixes to process: {len(remaining)}")

    if not remaining:
        print("  Nothing to do!")
        for s in sessions:
            await s.close()
        return

    if not checkpoint.started_at:
        checkpoint.started_at = datetime.now().isoformat()

    # Set up CSV
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    file_mode = "a" if resume and OUTPUT_CSV.exists() else "w"
    csv_file = open(OUTPUT_CSV, file_mode, newline="", encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    if file_mode == "w":
        csv_writer.writerow(CSV_COLUMNS)
    writer_lock = asyncio.Lock()

    # Set up queues and semaphores
    prefix_queue = asyncio.Queue()
    for p in remaining:
        prefix_queue.put_nowait(p)

    detail_sem = asyncio.Semaphore(MAX_CONCURRENT_DETAILS)

    stats = {
        "start_time": time.time(),
        "prefixes_done": 0,
        "details_fetched": 0,
        "total_prefixes": len(remaining),
    }

    # Launch workers - one per session
    tasks = []
    for i, session in enumerate(sessions):
        t = asyncio.create_task(
            worker(i, session, prefix_queue, writer_lock, csv_writer,
                   csv_file, detail_sem, checkpoint, stats)
        )
        tasks.append(t)

    await asyncio.gather(*tasks)

    # Final save
    checkpoint.save()
    csv_file.close()

    elapsed = time.time() - stats["start_time"]
    print(f"\n=== Scraping Complete ===")
    print(f"  Duration: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"  Prefixes processed: {stats['prefixes_done']}")
    print(f"  Detail records: {stats['details_fetched']}")
    print(f"  Output: {OUTPUT_CSV}")

    # Session stats
    for s in sessions:
        print(f"  Session {s.session_id}: {s.search_count} searches, {s.detail_count} details")
        await s.close()


async def single_session_scrape(captcha_answers: list[str],
                                limit_prefixes: int = 0,
                                resume: bool = False):
    """Scrape using a single interactive session (simplest mode).

    If session_info.json exists from --prepare-sessions, reuses that session.
    Otherwise creates a new session.
    """
    print("=== NM PSI Contractor Scraper (Single Session) ===")

    session = PSISession(0)

    # Always create a fresh session (JSESSIONID reuse across processes is unreliable)
    await session.create()
    print(f"  JSESSIONID: {session.jsessionid}")

    # Download CAPTCHA
    captcha_path = CAPTCHA_DIR / "captcha.jpg"
    await session.download_captcha(captcha_path)
    print(f"  CAPTCHA saved to: {captcha_path}")

    if captcha_answers:
        session.set_captcha(captcha_answers[0])
    else:
        answer = input("  Enter CAPTCHA answer: ").strip()
        session.set_captcha(answer)

    ok = await session.authenticate()
    if not ok:
        print("  CAPTCHA verification failed!")
        await session.close()
        return

    print("  Session authenticated!")

    # Run single-session scrape
    all_prefixes = build_prefix_list()

    checkpoint = Checkpoint(CHECKPOINT_FILE)
    if resume:
        checkpoint.load()
        print(f"  Resuming from checkpoint: {len(checkpoint.completed_prefixes)} done")

    remaining = [p for p in all_prefixes if p not in checkpoint.completed_prefixes]
    if limit_prefixes > 0:
        remaining = remaining[:limit_prefixes]

    print(f"  Prefixes to process: {len(remaining)}")

    if not checkpoint.started_at:
        checkpoint.started_at = datetime.now().isoformat()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    file_mode = "a" if resume and OUTPUT_CSV.exists() else "w"
    csv_file = open(OUTPUT_CSV, file_mode, newline="", encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    if file_mode == "w":
        csv_writer.writerow(CSV_COLUMNS)
    writer_lock = asyncio.Lock()
    detail_sem = asyncio.Semaphore(DETAIL_SEMAPHORE_PER_SESSION)

    stats = {
        "start_time": time.time(),
        "prefixes_done": 0,
        "details_fetched": 0,
        "total_prefixes": len(remaining),
    }

    prefix_queue = asyncio.Queue()
    for p in remaining:
        prefix_queue.put_nowait(p)

    await worker(0, session, prefix_queue, writer_lock, csv_writer,
                 csv_file, detail_sem, checkpoint, stats)

    checkpoint.save()
    csv_file.close()
    await session.close()

    elapsed = time.time() - stats["start_time"]
    print(f"\n=== Complete ===")
    print(f"  Duration: {elapsed:.0f}s")
    print(f"  Records: {stats['details_fetched']}")
    print(f"  Output: {OUTPUT_CSV}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape NM CID contractors from PSI Exams")
    parser.add_argument("--prepare-sessions", type=int, metavar="N",
                        help="Create N sessions and download CAPTCHAs")
    parser.add_argument("--captcha-answers", type=str,
                        help="Comma-separated CAPTCHA answers for each session")
    parser.add_argument("--limit-prefixes", type=int, default=0,
                        help="Limit number of prefixes to process (for testing)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from checkpoint")
    parser.add_argument("--single", action="store_true",
                        help="Use single interactive session")
    parser.add_argument("--status", action="store_true",
                        help="Show checkpoint status")
    args = parser.parse_args()

    if args.status:
        cp = Checkpoint(CHECKPOINT_FILE)
        cp.load()
        all_prefixes = build_prefix_list()
        print(f"Total prefixes: {len(all_prefixes)}")
        print(f"Completed: {len(cp.completed_prefixes)}")
        print(f"Remaining: {len(all_prefixes) - len(cp.completed_prefixes)}")
        print(f"Details fetched: {cp.total_details}")
        print(f"Started: {cp.started_at}")
        if OUTPUT_CSV.exists():
            # Count lines
            with open(OUTPUT_CSV) as f:
                lines = sum(1 for _ in f) - 1  # exclude header
            print(f"CSV rows: {lines}")
        return

    if args.prepare_sessions:
        asyncio.run(prepare_sessions(args.prepare_sessions))
        return

    answers = []
    if args.captcha_answers:
        answers = [a.strip() for a in args.captcha_answers.split(",")]

    if args.single or len(answers) <= 1:
        asyncio.run(single_session_scrape(
            answers, args.limit_prefixes, args.resume
        ))
    else:
        asyncio.run(run_scrape(
            answers, args.limit_prefixes, args.resume
        ))


if __name__ == "__main__":
    main()
