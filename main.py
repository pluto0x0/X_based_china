import aiohttp
import asyncio
import json
from aiohttp_client_cache import SQLiteBackend, CacheBackend
from aiohttp_client_cache.session import CachedSession
from pprint import pprint
from collections import deque
from config import *
from loguru import logger

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
            logger.warning(f"Error fetching followings: {e}")
            break
        if data.get("status") != "ok":
            break
        followings.extend(data.get("following", []))
        if not data.get("more_users") or (maxlen > 0 and len(followings) >= maxlen):
            break
        cursor = data.get("next_cursor")
    return followings


async def get_userinfo(session, usernames):
    headers = {
        "x-rapidapi-key": KEY,
        "x-rapidapi-host": "twitter241.p.rapidapi.com",
    }
    url = "https://twitter241.p.rapidapi.com/about-account"
    results = {}
    for username in usernames:
        querystring = {"username": username}
        try:
            async with session.get(
                url, headers=headers, params=querystring
            ) as response:
                data = await response.json()
                try:
                    info = data["result"]["data"]["user_result_by_screen_name"][
                        "result"
                    ]
                except Exception as e:
                    logger.warning(f"Error fetching userinfo for {username}: {data}")
                else:
                    results[username] = info
        except Exception as e:
            logger.warning(f"Error fetching userinfo for {username}: {e}")
    return results


async def main():
    queue = deque(seed_accounts)
    userset = set()
    try:
        with open(output_file, "r") as f:
            for line in f:
                record = json.loads(line)
                userset.add(record["username"])
    except FileNotFoundError:
        pass
    logger.info(f"Loaded {len(userset)} existing users from {output_file}")
    hit = 0
    with open(output_file, "a") as f:
        async with CachedSession(cache=cache) as session:
            while queue:
                current_id = queue.popleft()
                logger.info(f"Processing: {current_id}")
                followings = await get_followings(
                    session, current_id, maxlen=max_followings
                )
                logger.info(f"Found {len(followings)} followings for {current_id}")
                usernames = [
                    user["screen_name"] for user in followings if user["screen_name"]
                ]
                about_info = await get_userinfo(session, usernames)
                logger.info(f"Retrieved about info for {len(about_info)} users")
                for user, info in about_info.items():
                    try:
                        if info["about_profile"]["account_based_in"] == "China":
                            if user not in userset:
                                record = {"username": user, "info": info}
                                f.write(json.dumps(record) + "\n")
                                f.flush()
                                userset.add(user)
                                hit += 1
                                logger.debug(f"Found China-based account: {user}")
                            if user not in queue:
                                queue.append(user)
                    except KeyError:
                        pass
                if max_hit > 0 and hit >= max_hit:
                    logger.info(f"Reached max hit limit of {max_hit}. Stopping.")
                    break
                logger.info(
                    f"Queue size: {len(queue)}, Total users found: {len(userset)}"
                )


asyncio.run(main())
