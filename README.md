# BFS scraper for X accounts based in China

## Run

### 1. Install Requirements

```
pip install aiohttp_client_cache loguru
```

### 2. API Key

Run:

You will need your own key for the following API's from RapidAPI:

- [Twttr API](https://rapidapi.com/davethebeast/api/twitter241)
- [Twitter API](https://rapidapi.com/alexanderxbx/api/twitter-api45)

Rename `config.default.py` to `config.py`
Paste the key in it.

### 3.

```
python main.py
```

### 4. Build Page

Build a static web paage:

```
python render.py china.jsonl
```

## Configuration

Edit `config.py`

```python
seed_users = [
    "linboweibu17"
]

max_hit = 10000
output_file = "china.jsonl"
max_followings = 300
```

- `seed_users`: Seed users in the initial queue
- `max_hit = 10000`: Exit when finding 10000 users, 0 = no limit
- `output_file`: Outout file name
- `max_followings`: Max number of users fetched from a following list, 0 = no limit

## How It Works

Starting from seed users, Breadth-First Search for X users based on their following list.

## License

MIT