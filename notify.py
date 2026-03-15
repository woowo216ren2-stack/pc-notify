import os
import feedparser
import requests
from datetime import datetime, timezone, timedelta

# 環境変数から取得
LINE_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_USER_ID = os.environ["LINE_USER_ID"]

JST = timezone(timedelta(hours=9))

# RSSフィード一覧
FEEDS = [
    {"name": "エルミタージュ秋葉原", "url": "https://www.gdm.or.jp/feed"},
    {"name": "ASCII.jp 自作PC", "url": "https://ascii.jp/pc/rss.xml"},
    {"name": "ITmedia PC USER", "url": "https://rss.itmedia.co.jp/rss/2.0/pcuser.xml"},
]

# キーワードフィルター
KEYWORDS = [
    "セール", "sale", "値下", "特価", "タイムセール",
    "GPU", "グラボ", "RTX", "RX", "メモリ", "RAM",
    "SSD", "CPU", "Ryzen", "Core i",
    "マザーボード", "電源", "ケース",
    "モニター", "ディスプレイ",
    "ガジェット", "自作", "新発売", "発売",
    "WQHD", "マウス", "チェア", "USBメモリ",
    "板タブ", "電源タップ", "デスク", "充電器", "マイク",
    "RTX 4060", "RTX 4070",
    "DDR5", "Gen4", "Gen5",
]
def fetch_news():
    results = []
    now = datetime.now(JST)
    cutoff = now - timedelta(hours=24)
    
    for feed_info in FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:10]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                
                # キーワードフィルター
                if not any(kw.lower() in title.lower() for kw in KEYWORDS):
                    continue
                
                results.append(f"【{feed_info['name']}】\n{title}\n{link}")
        except Exception as e:
            print(f"Error fetching {feed_info['name']}: {e}")
    
    return results

def send_line_message(text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": text}]
    }
    res = requests.post(url, headers=headers, json=payload)
    print(f"LINE API response: {res.status_code} {res.text}")

def main():
    now = datetime.now(JST).strftime("%Y/%m/%d %H:%M")
    news = fetch_news()
    
    if not news:
        message = f"🖥️ PC情報通知 {now}\n\n該当ニュースなし"
    else:
        items = "\n\n".join(news[:10])  # 最大10件
        message = f"🖥️ PC情報通知 {now}\n\n{items}"
    
    # LINEに送信
    # 1000文字超えたら分割
    if len(message) > 1000:
        chunks = [message[i:i+1000] for i in range(0, len(message), 1000)]
        for chunk in chunks:
            send_line_message(chunk)
    else:
        send_line_message(message)

if __name__ == "__main__":
    main()
