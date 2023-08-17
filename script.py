from datetime import datetime
import pandas as pd
import feedparser
from fetch_rss import get_url


def print_recent_gigs(url):
    feed = feedparser.parse(url)
    res = pd.DataFrame(feed['entries'])\
        .assign(date = lambda d: d['published'].apply(
            lambda x: datetime.strptime(x, '%a, %d %b %Y %H:%M:%S %z').strftime('%a %H:%M')),\
                title = lambda d: d['title'].replace({'&amp;': '&'}, regex=True))\
        [['date', 'title', 'summary']]\
        .sort_values('date', ascending=False)\
        .set_index('date')
    print(res.head())

urls = [
    "https://www.upwork.com/ab/feed/topics/rss?securityToken=6351f1c6fbe3477ad3fe521ee0b841899d795fac367917dbff3cc2064e4f0c6b2496f884f4441ad10f97ca6f0db3c8c83f838f65f9b9e73cbb27a159b5662b25&userUid=551492515965923328&orgUid=551492515965923330&topic=6734355",
    get_url()    
]

[print_recent_gigs(u) for u in urls]
