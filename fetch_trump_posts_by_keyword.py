from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

from dateutil import parser as date_parse

from truthbrush import Api, CFBlockException, GeoblockException, LoginErrorException


class _HtmlTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def text(self) -> str:
        return "".join(self._parts)


def strip_html(html_content: str) -> str:
    parser = _HtmlTextExtractor()
    parser.feed(html_content or "")
    parser.close()
    clean = unescape(parser.text())
    return re.sub(r"\s+", " ", clean).strip()


def prompt_date(prompt_label: str) -> date:
    while True:
        raw = input(f"{prompt_label} (YYYY-MM-DD, UTC): ").strip()
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please enter a date like 2026-03-15.")


def prompt_keyword() -> str:
    while True:
        keyword = input("Keyword to match in post text: ").strip()
        if keyword:
            return keyword
        print("Keyword cannot be empty.")


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    safe = re.sub(r"[^a-z0-9]+", "_", lowered)
    return safe.strip("_") or "keyword"


def prompt_output_dir(default_dir: Path) -> Path:
    raw = input(f"Output folder [{default_dir}]: ").strip()
    return Path(raw).expanduser() if raw else default_dir


def to_utc(dt_str: str) -> datetime:
    dt = date_parse.parse(dt_str)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def write_post_file(post: dict, text_body: str, created_at_utc: datetime, out_dir: Path) -> Path:
    stamp = created_at_utc.strftime("%Y%m%dT%H%M%SZ")
    post_id = post.get("id", "unknown")
    filename = f"{stamp}_{post_id}.txt"
    file_path = out_dir / filename

    url = post.get("url") or f"https://truthsocial.com/@realDonaldTrump/posts/{post_id}"
    uri = post.get("uri", "")

    content = (
        f"id: {post_id}\n"
        f"created_at_utc: {created_at_utc.isoformat()}\n"
        f"url: {url}\n"
        f"uri: {uri}\n\n"
        f"{text_body}\n"
    )
    file_path.write_text(content, encoding="utf-8")
    return file_path


def main() -> int:
    print("Export @realDonaldTrump Truth Social posts by UTC date range and keyword.")
    print("Note: results are paged from newest to oldest, so older ranges can take longer.\n")

    start_date = prompt_date("Start date")
    end_date = prompt_date("End date")
    if end_date < start_date:
        print("End date must be on or after start date.")
        return 1

    keyword = prompt_keyword()
    keyword_lc = keyword.lower()

    default_dir = Path("exports") / (
        f"trump_{start_date.isoformat()}_{end_date.isoformat()}_{slugify(keyword)}"
    )
    output_dir = prompt_output_dir(default_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
    created_after = start_dt - timedelta(microseconds=1)

    api = Api()
    scanned = 0
    saved = 0

    try:
        for post in api.pull_statuses(
            username="realDonaldTrump",
            created_after=created_after,
            replies=False,
        ):
            scanned += 1
            created_at = to_utc(post["created_at"])

            if created_at > end_dt:
                continue

            text_body = strip_html(post.get("content", ""))
            if keyword_lc not in text_body.lower():
                continue

            write_post_file(post, text_body, created_at, output_dir)
            saved += 1

    except (LoginErrorException, GeoblockException, CFBlockException) as exc:
        print(f"Authentication or access error: {exc}")
        print(
            "Set TRUTHSOCIAL_TOKEN or TRUTHSOCIAL_USERNAME/TRUTHSOCIAL_PASSWORD "
            "in your environment or a .env file."
        )
        return 1
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        return 130

    print(f"\nScanned posts in range window: {scanned}")
    print(f"Saved matching posts: {saved}")
    print(f"Output folder: {output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
