#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#
import asyncio
import math
import os
import shutil
import socket
from datetime import datetime

import dotenv
import heroku3
import requests
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

import config
from config import BANNED_USERS
from strings import get_command
from YukkiMusic import app
from YukkiMusic.core.call import Yukki
from YukkiMusic.misc import HAPP, SUDOERS, XCB, db
from YukkiMusic.utils.database import (
    get_active_chats,
    get_cmode,
    remove_active_chat,
    remove_active_video_chat,
)
from YukkiMusic.utils.decorators import AdminActual, language
from YukkiMusic.utils.decorators.language import language
from YukkiMusic.utils.pastebin import Yukkibin

# Commands
GETLOG_COMMAND = get_command("GETLOG_COMMAND")
GETVAR_COMMAND = get_command("GETVAR_COMMAND")
DELVAR_COMMAND = get_command("DELVAR_COMMAND")
SETVAR_COMMAND = get_command("SETVAR_COMMAND")
USAGE_COMMAND = get_command("USAGE_COMMAND")
UPDATE_COMMAND = get_command("UPDATE_COMMAND")
RESTART_COMMAND = get_command("RESTART_COMMAND")
REBOOT_COMMAND = get_command("REBOOT_COMMAND")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def is_heroku():
    return "heroku" in socket.getfqdn()


@app.on_message(
    command=GETLOG_COMMAND,
    from_user=SUDOERS,
)
@language
async def log_(event, _):
    try:
        if await is_heroku():
            if HAPP is None:
                return await event.reply(_["heroku_1"])
            data = HAPP.get_log()
            link = await Yukkibin(data)
            return await event.reply(link)
        else:
            if os.path.exists(config.LOG_FILE_NAME):
                log = open(config.LOG_FILE_NAME)
                lines = log.readlines()
                data = ""
                try:
                    NUMB = int(event.text.split(None, 1)[1])
                except:
                    NUMB = 100
                for x in lines[-NUMB:]:
                    data += x
                link = await Yukkibin(data)
                return await event.reply(link)
            else:
                return await event.reply(_["heroku_2"])
    except Exception:
        await event.reply(_["heroku_2"])


@app.on_message(
    command=GETVAR_COMMAND,
    from_user=SUDOERS,
)
@language
async def varget_(event, _):
    usage = _["heroku_3"]
    if len(event.text.split()) != 2:
        return await event.reply(usage)
    check_var = event.text.split(None, 2)[1]
    if await is_heroku():
        if HAPP is None:
            return await event.reply(_["heroku_1"])
        heroku_config = HAPP.config()
        if check_var in heroku_config:
            return await event.reply(
                f"**{check_var}:** `{heroku_config[check_var]}`"
            )
        else:
            return await event.reply(_["heroku_4"])
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await event.reply(_["heroku_5"])
        output = dotenv.get_key(path, check_var)
        if not output:
            await event.reply(_["heroku_4"])
        else:
            return await event.reply(f"**{check_var}:** `{str(output)}`")


@app.on_message(
    command=DELVAR_COMMAND,
    from_user=SUDOERS,
)
@language
async def vardel_(event, _):
    usage = _["heroku_6"]
    if len(event.text.split()) != 2:
        return await event.reply(usage)
    check_var = event.text.split(None, 2)[1]
    if await is_heroku():
        if HAPP is None:
            return await event.reply(_["heroku_1"])
        heroku_config = HAPP.config()
        if check_var in heroku_config:
            await event.reply(_["heroku_7"].format(check_var))
            del heroku_config[check_var]
        else:
            return await event.reply(_["heroku_4"])
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await event.reply(_["heroku_5"])
        output = dotenv.unset_key(path, check_var)
        if not output[0]:
            return await event.reply(_["heroku_4"])
        else:
            await event.reply(_["heroku_7"].format(check_var))
            os.system(f"kill -9 {os.getpid()} && python3 -m YukkiMusic")


@app.on_message(
    command=SETVAR_COMMAND,
    from_user=SUDOERS,
)
@language
async def set_var(event, _):
    usage = _["heroku_8"]
    if len(event.text.split()) < 3:
        return await event.reply(usage)
    to_set = event.text.split(None, 2)[1].strip()
    value = event.text.split(None, 2)[2].strip()
    if await is_heroku():
        if HAPP is None:
            return await event.reply(_["heroku_1"])
        heroku_config = HAPP.config()
        if to_set in heroku_config:
            await event.reply(_["heroku_9"].format(to_set))
        else:
            await event.reply(_["heroku_10"].format(to_set))
        heroku_config[to_set] = value
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await event.reply(_["heroku_5"])
        dotenv.set_key(path, to_set, value)
        if dotenv.get_key(path, to_set):
            await event.reply(_["heroku_9"].format(to_set))
        else:
            await event.reply(_["heroku_10"].format(to_set))
        os.system(f"kill -9 {os.getpid()} && python3 -m YukkiMusic")


@app.on_message(
    command=USAGE_COMMAND,
    from_user=SUDOERS,
)
@language
async def usage_dynos(event, _):
    ### Credits CatUserbot
    if await is_heroku():
        if HAPP is None:
            return await event.reply(_["heroku_1"])
    else:
        return await event.reply(_["heroku_11"])
    dyno = await event.reply(_["heroku_12"])
    Heroku = heroku3.from_key(config.HEROKU_API_KEY)
    account_id = Heroku.account().id
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {config.HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + account_id + "/actions/get-quota"
    r = requests.get("https://api.heroku.com" + path, headers=headers)
    if r.status_code != 200:
        return await dyno.edit("Unable to fetch.")
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)
    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)
    await asyncio.sleep(1.5)
    text = f"""
**Dyno usage**

<u>Usage:</u>
Total used: `{AppHours}`**h**  `{AppMinutes}`**m**  [`{AppPercentage}`**%**]

<u>Remaining Quota</u>
Total Left: `{hours}`**h**  `{minutes}`**m**  [`{percentage}`**%**]"""
    return await dyno.edit(text)


@app.on_message(
    command=UPDATE_COMMAND,
    from_user=SUDOERS,
)
@language
async def update_(event, _):
    if await is_heroku():
        if HAPP is None:
            return await event.reply(_["heroku_1"])
    response = await event.reply(_["heroku_13"])
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit(_["heroku_14"])
    except InvalidGitRepositoryError:
        return await response.edit(_["heroku_15"])
    to_exc = f"git fetch origin {config.UPSTREAM_BRANCH} &> /dev/null"
    os.system(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]
    for checks in repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit("Bot is up to date")
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[(format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4],
    )
    updates = "".join(
        f"<b>➣ #{info.count()}: <a href={REPO_}/commit/{info}>{info.summary}</a> By -> {info.author}</b>\n\t\t\t\t<b>➥ Commited On:</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} {datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
        for info in repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}")
    )
    _update_response_ = "**A new upadte is available for the Bot! **\n\n➣ Pushing upadtes Now\n\n__**Updates:**__\n"
    _final_updates_ = f"{_update_response_} {updates}"

    if len(_final_updates_) > 4096:
        url = await Yukkibin(updates)
        nrs = await response.edit(
            f"**A new upadte is available for the Bot!**\n\n➣ Pushing upadtes Now\n\n__**Updates:**__\n\n[Check Upadtes]({url})",
            link_preview=False,
        )
    else:
        nrs = await response.edit(_final_updates_, link_preview=False)
    os.system("git stash &> /dev/null && git pull")

    try:
        served_chats = await get_active_chats()
        for x in served_chats:
            try:
                await app.send_message(
                    int(x),
                    "{0} Is upadted herself\n\nYou can start playing after 15-20 Seconds".format(
                        app.mention
                    ),
                )
                await remove_active_chat(x)
                await remove_active_video_chat(x)
            except:
                pass
        await response.edit(
            _final_updates_
            + f"» Bot Upadted Sucessfully Now wait until the bot starts",
            link_preview=False,
        )
    except:
        pass

    if await is_heroku():
        try:
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            await response.edit(
                f"{nrs.text}\n\nSomething went wrong, Please check logs"
            )
            return await app.send_message(
                config.LOG_GROUP_ID,
                "An exception occurred #updater due to : <code>{0}</code>".format(
                    err
                ),
            )
    else:
        os.system("pip3 install --no-cache-dir -U -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && python3 -m YukkiMusic")
        exit()


@app.on_message(
    command=REBOOT_COMMAND,
    is_group=True,
    from_user=BANNED_USERS,
    is_restricted=True,
)
@AdminActual
async def reboot(event, _):
    mystic = await event.reply(
        f"Please Wait... \nRebooting{app.mention} For Your Chat."
    )
    try:
        db[event.chat_id] = []
        await Yukki.stop_stream(event.chat_id)
    except:
        pass
    chat_id = await get_cmode(event.chat_id)
    if chat_id:
        try:
            await app.get_entity(chat_id)
        except:
            pass
        try:
            db[chat_id] = []
            await Yukki.stop_stream(chat_id)
        except:
            pass
    return await mystic.edit("Sucessfully Restarted \nTry playing Now..")


@app.on_message(
    command=RESTART_COMMAND,
    from_user=BANNED_USERS,
    is_restricted=True,
)
async def restart_(event):
    if not event.sender_id in SUDOERS:
        if event.is_private:
            return
        return await reboot(event)
    response = await event.reply("Restarting...")
    ac_chats = await get_active_chats()
    for x in ac_chats:
        try:
            await app.send_message(
                int(x),
                f"{app.mention} Is restarting...\n\nYou can start playing after 15-20 seconds",
            )
            await remove_active_chat(x)
            await remove_active_video_chat(x)
        except:
            pass

    try:
        shutil.rmtree("downloads")
        shutil.rmtree("raw_files")
        shutil.rmtree("cache")
    except:
        pass
    await response.edit(
        "Restart process started, please wait for few seconds until the bot starts..."
    )
    os.system(f"kill -9 {os.getpid()} && python3 -m YukkiMusic")