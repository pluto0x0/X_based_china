# BFS scraper for X accounts based in China

Online Demo: <https://pluto0x0.github.io/X_based_china/>

## Run

### 1. Install Requirements

```shell
pip install aiohttp_client_cache loguru aiolimiter
```

### 2. API Key

You will need your own key for the following API's from RapidAPI:

- [Twttr API](https://rapidapi.com/davethebeast/api/twitter241)
- [Twitter API](https://rapidapi.com/alexanderxbx/api/twitter-api45)

Rename `config.default.py` to `config.py` and paste the key in it.

See [Results & Statistics](#results--statistics) for API usage statistics.

### 3. Run

```shell
python main.py
```

### 4. Build Page

Once you get the result, build a static web page:

```shell
python render.py china.jsonl
```

## Configuration

In `config.py`

```python
SEED_ACCOUNTS = [
    "linboweibu17"
    # "KunDong95265"
]
REQUESTS_PER_SECOND = 9
MAX_HIT = 100000
OUTPUT_FILE = "china.jsonl"
MAX_FOLLOWINGS = 800
```

- `SEED_ACCOUNTS`: Seed accounts in the initial queue
- `REQUESTS_PER_SECOND`: Maximum number of requests per sec
- `MAX_HIT = 100000`: Exit when finding 100000 accounts, 0 = no limit
- `OUTPUT_FILE`: Output file name
- `MAX_FOLLOWINGS`: Max number of accounts fetched from a following list, 0 = no limit

## How It Works

Starting from seed accounts, Breadth-First Search for X accounts based on their following list.

Async http requests are cached with SQLite DB.

## Results & Statistics

- RUN #1: 5,200 results with **17,980** Twttr API request and **1,000** Twitter API requests

## License

MIT
