# Trump Truth Social Keyword Export

This repository includes a Python script, `fetch_trump_posts_by_keyword.py`, that exports `@realDonaldTrump` Truth Social posts for:

- a UTC date range that you choose at runtime
- a keyword that you choose at runtime

Matching posts are saved as text files in an `exports/` folder.

## What this script does

When you run `fetch_trump_posts_by_keyword.py`, it:

1. Prompts for a start date, end date, and keyword.
2. Pulls posts from `@realDonaldTrump` using the Truthbrush API client.
3. Converts post HTML content into clean plain text.
4. Filters posts to your requested date range and keyword.
5. Writes one `.txt` file per match (with metadata + post text).

Each output file includes:

- post ID
- UTC timestamp
- post URL
- URI
- cleaned post text

## How Truthbrush is used

This project uses the `truthbrush` Python package as the data access layer for Truth Social.  
In this script, `truthbrush.Api()` is used to call `pull_statuses(...)` and page through posts from newest to oldest.

Truthbrush handles authentication using environment variables (or `.env`) and provides structured post data that this script filters and exports.

## Prerequisites

- Python 3.10+
- A Truth Social account (your own credentials are required)

## Setup

### 1) Clone and enter the repo

```bash
git clone <your-repo-url>
cd Truth-Social-Query
```

### 2) Install dependencies

Use Poetry (recommended):

```bash
poetry install
```

Or use pip:

```bash
pip install -e .
```

### 3) Update `.env` with your own credentials

Open `.env` and set both values:

```env
TRUTHSOCIAL_USERNAME=your_truthsocial_username
TRUTHSOCIAL_PASSWORD=your_truthsocial_password
```

Every user must provide their own Truth Social username and password in `.env` before running the script.

## Run the script

With Poetry:

```bash
poetry run python fetch_trump_posts_by_keyword.py
```

Without Poetry:

```bash
python fetch_trump_posts_by_keyword.py
```

You will be prompted for:

- `Start date (YYYY-MM-DD, UTC)`
- `End date (YYYY-MM-DD, UTC)`
- `Keyword to match in post text`
- optional output folder path (press Enter to accept default)

## Output behavior

- Default output folder format:
  - `exports/trump_<start-date>_<end-date>_<keyword>/`
- One text file is written per matching post.
- The script prints:
  - how many posts were scanned
  - how many matching posts were saved
  - the final output folder path

## Notes and troubleshooting

- Date inputs must use `YYYY-MM-DD`.
- End date must be the same as or after start date.
- If login/access fails, verify `.env` values first.
- Paging is newest-to-oldest, so large or older ranges can take longer.
