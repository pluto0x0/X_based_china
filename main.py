import aiohttp
import asyncio
import json
from aiohttp_client_cache import SQLiteBackend, CacheBackend
from aiohttp_client_cache.session import CachedSession
from pprint import pprint
from collections import deque
from config import KEY

cache = SQLiteBackend("cache.db")

async def get_followings(session, username, maxlen=400):
    headers = {
        "x-rapidapi-key": KEY,
        "x-rapidapi-host": "twitter-api45.p.rapidapi.com",
    }
    url = "https://twitter-api45.p.rapidapi.com/following.php"
    followings = []
    cursor = None
    while True:
        params = {"screenname": username}
        if cursor:
            params["cursor"] = cursor
        try:
            async with session.get(url, headers=headers, params=params) as resp:
                data = await resp.json()
        except Exception as e:
            print(f"Error fetching followings: {e}")
            break
        if data.get("status") != "ok":
            break
        followings.extend(data.get("following", []))
        if not data.get("more_users") or (maxlen > 0 and len(followings) >= maxlen):
            break
        cursor = data.get("next_cursor")
    return followings


async def get_about(session, usernames):
    headers = {
        "x-rapidapi-key": KEY,
        "x-rapidapi-host": "twitter241.p.rapidapi.com",
    }
    url = "https://twitter241.p.rapidapi.com/about-account"
    results = {}
    for username in usernames:
        querystring = {"username": username}
        async with session.get(
            url, headers=headers, params=querystring
        ) as response:
            data = await response.json()
            try:
                about = data["result"]["data"]["user_result_by_screen_name"]["result"][
                    "about_profile"
                ]
            except Exception as e:
                print(f"Error fetching about for {username}: {data}")
            else:
                results[username] = about
    return results


# Usage in Jupyter (top-level await supported):
# r = await get_followings('flayed__')
# Or: r = asyncio.run(get_followings('flayed__'))

seed_ids = ["linboweibu17"]
max_hit = 10000
output_file = "china.jsonl"

async def main():
    queue = deque(seed_ids)
    userset = set()
    with open(output_file, "r") as f:
        for line in f:
            record = json.loads(line)
            userset.add(record["username"])
    print(f"Loaded {len(userset)} existing users from {output_file}")
    hit = 0
    with open(output_file, "a") as f:
        async with CachedSession(cache=cache) as session:
            while queue:
                current_id = queue.popleft()
                print(f"Processing: {current_id}")
                followings = await get_followings(session, current_id, maxlen=300)
                print(f"Found {len(followings)} followings for {current_id}")
                usernames = [user["screen_name"] for user in followings if user["screen_name"]]
                about_info = await get_about(session, usernames)
                print(f"Retrieved about info for {len(about_info)} users")  
                for user, info in about_info.items():
                    try:
                        if info['account_based_in'] == "China":
                            if user not in userset:
                                record = {"username": user, "about_profile": info}
                                f.write(json.dumps(record) + "\n")
                                f.flush()
                                userset.add(user)
                                hit += 1
                            print(f"Found China-based account: {user}")
                            queue.append(user)
                    except KeyError:
                        pass
                if hit >= max_hit:
                    print(f"Reached max hit limit of {max_hit}. Stopping.")
                    break
                print(f"Queue size: {len(queue)}, Total users found: {len(userset)}")

async def test():
    async with CachedSession(cache=cache) as session:
        # r = await get_followings(session, "flayed__")
        # pprint(r)
        r = await get_about(session, ["flayed__", "linboweibu17"])
        pprint(r)

asyncio.run(main())
