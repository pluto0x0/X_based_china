# BFS scraper for X accounts based in China

Online Demo: <https://pluto0x0.github.io/X_based_china/>

## Run

### 1. Install Requirements

```shell
pip install aiohttp_client_cache loguru
```

### 2. API Key

You will need your own key for the following API's from RapidAPI:

- [Twttr API](https://rapidapi.com/davethebeast/api/twitter241) (~20 Requests / Account)
- [Twitter API](https://rapidapi.com/alexanderxbx/api/twitter-api45) (~1 Requests / 50 Account)

Rename `config.default.py` to `config.py`
Paste the key in it.

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
seed_accounts = [
    "linboweibu17"
]

max_hit = 10000
output_file = "china.jsonl"
max_followings = 300
```

- `seed_accounts`: Seed accounts in the initial queue
- `max_hit = 10000`: Exit when finding 10000 accounts, 0 = no limit
- `output_file`: Output file name
- `max_followings`: Max number of accounts fetched from a following list, 0 = no limit

## How It Works

Starting from seed accounts, Breadth-First Search for X accounts based on their following list.

Async http requests are cached with SQLite DB.

## License

MIT
