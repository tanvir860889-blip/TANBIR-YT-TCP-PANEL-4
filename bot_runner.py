#!/usr/bin/env python3
"""Worker launched by app.py. Uses the bot engine shipped in this project."""
import asyncio
import os
import sys
import time
import bot_core
import login_engine
from cfonts import render
from bot_core import TcPOnLine, TcPChaT, build_ob55_online_auth, create_auth_token_chat


def load_credentials(path=None):
    path = path or os.environ.get("BOT_FILE", "bot.txt")
    data = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    data[k.strip().lower()] = v.strip()
    except FileNotFoundError:
        return None
    return data if data.get("uid") and data.get("password") else None


async def run_once():
    bot_core.FULL_RESTART_REQUESTED = False
    creds = load_credentials()
    if not creds:
        print("Missing UID/password. Save them in the website panel first.", flush=True)
        await asyncio.sleep(10)
        return
    if creds.get("nick"):
        bot_core.BOT_BRAND = creds["nick"]
    uid, password = creds["uid"], creds["password"]
    region_pref = creds.get("region", "BD")
    print("Starting login...", flush=True)
    result = await login_engine.do_login(uid, password, region_pref)
    if not result:
        print("Login failed; retrying shortly.", flush=True)
        await asyncio.sleep(10)
        return

    bot_core.bot_uid = result["bot_uid"]
    bot_core.ToKen = result["token"]
    bot_core.region = result["region"]
    key, iv = result["key"], result["iv"]
    timestamp = result["timestamp"]
    clan_id, clan_data = result.get("clan_id"), result.get("clan_data")
    chat_ip, chat_port = result["chat_ip"], result["chat_port"]
    online_ip, online_port = result["online_ip"], result["online_port"]
    print(render("TANBIR YT", colors=["cyan", "blue"], align="center"), flush=True)
    print(f"Logged in: UID {result['bot_uid']} | Region {result['region']} | {result['account_name']}", flush=True)

    chat_auth = create_auth_token_chat(int(result["bot_uid"]), result["token"], int(timestamp), key, iv)
    online_auth, _ = build_ob55_online_auth(int(result["bot_uid"]), result["token"], int(timestamp), key, iv)
    ready = asyncio.Event()
    chat_task = asyncio.create_task(TcPChaT(chat_ip, chat_port, chat_auth, key, iv, ready,
                                           result["region"], clan_id=clan_id, clan_data=clan_data))
    await ready.wait()
    await asyncio.sleep(1)
    online_task = asyncio.create_task(TcPOnLine(online_ip, online_port, key, iv, online_auth))
    print("Bot connections started.", flush=True)
    await asyncio.gather(chat_task, online_task)


async def main_loop():
    attempt = 0
    while True:
        attempt += 1
        try:
            print(f"Session {attempt} starting...", flush=True)
            await asyncio.wait_for(run_once(), timeout=7 * 60 * 60)
        except asyncio.TimeoutError:
            print("Session timeout; reconnecting.", flush=True)
            await asyncio.sleep(3)
        except Exception as exc:
            print(f"Worker error: {exc}; retrying in 5 seconds.", flush=True)
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        sys.exit(0)
