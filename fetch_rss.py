import feedparser, os
from datetime import datetime, timezone, timedelta
import telegram, html, re
from urllib.parse import quote
from asyncio import run
    


def get_url():
    url = f'https://www.upwork.com/ab/feed/jobs/rss?{os.getenv("UPWORKER_PRV")}&' +\
        'api_params=1&contractor_tier=2,3&paging=0;10&sort=recency&verified_payment_only=1&' +\
        'job_type=hourly,fixed&budget=300-&hourly_rate=30-&q=' +\
        'skills:(R OR etl OR dashboard OR dash OR "data analysis") OR (skills:("google sheets" OR excel OR airtable OR sql) AND NOT skills:("web design" OR "web development" OR "web application"))'

    print(url)
    return quote(url, safe=':/&=?')

async def send_message(bot, chat_id, message):
    await bot.send_message(
        chat_id=chat_id, text=html.unescape(
            re.sub('\n\n', '\n', re.sub(r'<br\s*/>', '\n', message))),
        parse_mode=telegram.constants.ParseMode.HTML)

def strfdelta(tdelta):
    minutes, seconds = divmod(tdelta.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h:{minutes}m:{seconds}s"

def main():
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_TO')

    update_freq = (10 + 1) * 60
    min_hourly_salary = 20
    
    feed = feedparser.parse(get_url())
    
    for i, entry in enumerate(feed.entries):
        ttl = '<b>' + entry.title.replace(" - Upwork", "") + '</b>'

        published_datetime = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        time_diff = datetime.now(timezone.utc) - published_datetime
        if time_diff > timedelta(seconds=update_freq):
            print(f'- Old [{ttl}]: {strfdelta(time_diff)}, {datetime.now(timezone.utc)}, {published_datetime}')
            continue

        min_hourly_regx = re.search(r'Hourly Range</b>: \$([^\.-]+)', entry['summary'])
        if min_hourly_regx and int(min_hourly_regx[1]) < min_hourly_salary:
            print(f'- Cheap [{ttl}]: {min_hourly_regx[1]}')
            continue

        message = f'{ttl}\n{entry.summary}'
        if len(message) > 4000:
            message = f'{message[:2000]}\n...\n{message[-2000:]}'
        print(f'+ Send [{ttl}]')
        bot = telegram.Bot(token=bot_token)
        run(send_message(bot, chat_id, message))
            

if __name__ == '__main__':
    main()
