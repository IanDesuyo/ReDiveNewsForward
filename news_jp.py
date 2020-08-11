import requests
import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sqlite3

script_dir = os.path.dirname(__file__)

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
}

defaultAvatar = {"username": "Re:Dive 日版公告小秘書", "avatar_url": "https://i.imgur.com/NuZZR7Q.jpg"}


def main():
    # get news list
    r = requests.get("https://priconne-redive.jp/news/", timeout=3.0, headers=header,)

    soup = BeautifulSoup(r.text, "html.parser")
    news_con = soup.select_one(".news-list-contents")

    news_time = news_con.find_all("dt")
    news_title = news_con.find_all("h4")
    news_link = news_con.find_all("a")

    news = []
    for i in range(0, len(news_time)):
        news.append(
            {
                "time": news_time[i].time.text,
                "type": news_time[i].span.text,
                "title": news_title[i].text,
                "url": news_link[i]["href"],
            }
        )
    # compare with prev data
    with open(os.path.join(script_dir, "news_jp.json"), "r", encoding="utf-8") as f:
        try:
            last = json.load(f)
        except:
            last = []
    if news == last:
        return

    lastest = []
    for i in news:
        if not (i in last):
            lastest.append(i)
    # send
    db = sqlite3.connect(os.path.join(script_dir, "app.db"))

    cur = db.cursor()

    for i in lastest:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] sending: " + str(i))
        getContent(i, cur)
    # save
    with open(os.path.join(script_dir, "news_jp.json"), "w+", encoding="utf-8") as f:
        f.write(json.dumps(news))


def getContent(data, cur):
    newsData = requests.get(data["url"], timeout=3.0, headers=header)

    soup = BeautifulSoup(newsData.text, "html.parser")
    content = soup.select_one(".contents-text")

    image = None
    if content.img:
        image = content.img["src"]

    content = BeautifulSoup(str(content).replace("<br/>", "\n"), "html.parser").getText().strip()

    if len(content) > 300:
        content = content[0:300] + f"...\n[詳細內容]({data['url']})"

    embed = {
        "embeds": [
            {
                "author": {"name": "プリンセスコネクト！Re:Dive - " + data["type"], "url": "https://randosoru.me/newsForward"},
                "title": data["title"],
                "url": data["url"],
                "description": content,
                "image": {"url": image},
                "footer": {"text": "Created by randosoru.me "},
                "timestamp": datetime.utcnow().isoformat(),
                "color": 1814232,
                "thumbnail": {"url": "https://i.imgur.com/e4KrYHe.png"},
            }
        ],
    }
    withAvatar = embed.copy()
    withAvatar.update(defaultAvatar)

    tasks = []
    cur.execute("SELECT * FROM NewsChannel WHERE `jp` = 1")
    for row in cur.fetchall():
        if row[4]:
            tasks.append(sendMessage(row[0], row[1], embed))
        # send with default avatar
        else:
            tasks.append(sendMessage(row[0], row[1], withAvatar))

    asyncio.get_event_loop().run_until_complete(asyncSend(tasks))


async def asyncSend(tasks):
    return await asyncio.gather(*tasks, return_exceptions=True)


async def sendMessage(id, token, embed):
    async with aiohttp.ClientSession() as session:
        try:
            await session.post(
                f"https://discord.com/api/webhooks/{id}/{token}", json=embed, timeout=aiohttp.ClientTimeout(connect=3.0)
            )
            await session.close()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
