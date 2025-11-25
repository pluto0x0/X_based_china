import aiohttp
import asyncio
import json
from aiohttp_client_cache import SQLiteBackend, CacheBackend
from aiohttp_client_cache.session import CachedSession
from pprint import pprint
from collections import deque
from config import *
from loguru import logger
from queue import PriorityQueue
from aiolimiter import AsyncLimiter

cache = SQLiteBackend("cache.db")
# sem = asyncio.Semaphore(10)
rate_limiter = AsyncLimiter(max_rate=REQUESTS_PER_SECOND, time_period=1)


async def controlled_get(session, url, **kwargs):
    if await session.cache.has_url(url, method="GET", **kwargs):
        async with session.get(url, **kwargs) as resp:
            return await resp.json()
    else:
        async with rate_limiter:
            async with session.get(url, **kwargs) as resp:
                return await resp.json()


async def get_followings(session, username, maxlen=400, cursor=None, sample=False):
    headers = {
        "x-rapidapi-key": KEY,
        "x-rapidapi-host": "twitter-api45.p.rapidapi.com",
    }
    url = "https://twitter-api45.p.rapidapi.com/following.php"
    followings = []
    while True:
        params = {"screenname": username}
        if cursor:
            params["cursor"] = cursor
        try:
            data = await controlled_get(session, url, headers=headers, params=params)
        except Exception as e:
            logger.warning(f"Error fetching followings: {e}")
            break
        if data.get("status") != "ok":
            break
        followings.extend(data.get("following", []))
        cursor = data.get("next_cursor", None)
        if (
            not data.get("more_users")
            or (maxlen > 0 and len(followings) >= maxlen)
            or sample
        ):
            break
    return followings, cursor


async def get_userinfo(session, usernames):
    headers = {
        "x-rapidapi-key": KEY,
        "x-rapidapi-host": "twitter241.p.rapidapi.com",
    }
    url = "https://twitter241.p.rapidapi.com/about-account"
    results = {}

    async def fetch_one(username: str):
        querystring = {"username": username}
        try:
            data = await controlled_get(
                session, url, headers=headers, params=querystring
            )
        except Exception as e:
            logger.warning(f"Error fetching userinfo for {username}: {e}")
            return username, None
        try:
            info = data["result"]["data"]["user_result_by_screen_name"]["result"]
        except Exception:
            logger.warning(f"Error fetching userinfo for {username}: {data}")
            return username, None

        return username, info

    tasks = [fetch_one(u) for u in usernames]
    responses = await asyncio.gather(*tasks, return_exceptions=False)

    for username, info in responses:
        if info is not None:
            results[username] = info

    return results


queue = PriorityQueue()
userset = set()


def init():
    global queue, userset
    for account in SEED_ACCOUNTS:
        queue.put((-1.0, (account, None)))  # (priority, (username, cursor))
    try:
        with open(OUTPUT_FILE, "r") as f:
            for line in f:
                record = json.loads(line)
                userset.add(record["username"])
    except FileNotFoundError:
        logger.info(f"No existing output file found. Starting fresh.")
    logger.info(f"Loaded {len(userset)} existing users from {OUTPUT_FILE}")


async def expand_user(session, file, username, cursor, sample=False):
    global queue, userset

    followings, cursor = await get_followings(
        session, username, maxlen=MAX_FOLLOWINGS, cursor=cursor, sample=sample
    )
    n_followings = len(followings)
    usernames = [user["screen_name"] for user in followings if user["screen_name"]]
    n_usernames = len(usernames)
    about_info = await get_userinfo(session, usernames)
    n_about_info = len(about_info)
    n_hit = n_new = 0
    expand_tasks = []

    async def expand_and_enqueue(user: str):
        try:
            tot, hit, user_cursor = await expand_user(
                session, file, user, None, sample=True
            )
            rate = hit / tot if tot > 0 else 0
        except Exception as e:
            logger.warning(f"Error expanding user {user}: {e}")
            return
        queue.put((-rate, (user, user_cursor)))
        logger.debug(f"Enqueued {user}, priority: {rate:.2%}")

    for user, info in about_info.items():
        try:
            if info["about_profile"]["account_based_in"] == "China":
                n_hit += 1
                if user not in userset:
                    record = {"username": user, "info": info}
                    file.write(json.dumps(record) + "\n")
                    file.flush()
                    userset.add(user)
                    n_new += 1
                    logger.debug(f"✅ Found new China-based account: {user}")
                    # only on new accounts
                    exists_queue = any(user == item[1][0] for item in queue.queue)
                    if not sample and not exists_queue:
                        expand_tasks.append(expand_and_enqueue(user))
        except KeyError:
            pass

    if expand_tasks:
        await asyncio.gather(*expand_tasks)

    return n_about_info, n_hit, cursor


async def main():
    global queue, userset
    init()

    with open(OUTPUT_FILE, "a") as f:
        async with CachedSession(cache=cache) as session:
            while queue:
                rate, (current_id, cursor) = queue.get()
                logger.info(
                    f"Processing: {current_id} ({-rate:.2%})\t Cursor: {cursor}"
                )
                await expand_user(session, f, current_id, cursor, sample=False)
                if MAX_HIT > 0 and len(userset) >= MAX_HIT:
                    logger.info(f"Reached max hit limit of {MAX_HIT}. Stopping.")
                    break
                logger.info(
                    f"Queue size: {len(queue.queue)}, Total users found: {len(userset)}"
                )


asyncio.run(main())
