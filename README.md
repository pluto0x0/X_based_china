BFS scraper for X accounts based in China.

```
pip install aiohttp_client_cache loguru
```

Run:

You need to fill your own key for the following API's in `config.py`.

- [Twttr API](https://rapidapi.com/davethebeast/api/twitter241)
- [Twitter API](https://rapidapi.com/alexanderxbx/api/twitter-api45)


, then

```
python main.py
```

Build page:

```
python render.py china.jsonl
```