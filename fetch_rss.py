import feedparser, os
from datetime import datetime, timezone, timedelta
import telegram, html, re
from urllib.parse import quote
from asyncio import run
    

def get_url():
    prv = os.getenv('UPWORKER_PRV')
    add_excel = 'OR "google sheets" OR excel OR airtable' if True else ''
    url = 'https://www.upwork.com/ab/feed/jobs/rss?&' + prv +\
        'api_params=1&contractor_tier=2,3&paging=0;10&sort=recency&verified_payment_only=1&' +\
        'job_type=hourly,fixed&budget=300-&hourly_rate=30-&q=' +\
        f'skills:(dax OR spark OR database R OR sql OR etl OR dashboard OR dash OR "data analytics" OR "data analysis" {add_excel})'
    print(url)
    return quote(url, safe=':/&=?')

async def send_message(bot, chat_id, message):
    await bot.send_message(
        chat_id=chat_id, text=html.unescape(
            re.sub('\n\n', '\n', re.sub(r'<br\s*/>', '\n', message))),
        parse_mode=telegram.constants.ParseMode.HTML)
    
def main():
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_TO')

    update_freq = (10 + 1) * 60
    min_hourly_salary = 20
    
    feed = feedparser.parse(get_url())
    
    for i, entry in enumerate(feed.entries):
        ttl = '<b>' + entry.title.replace(" - Upwork", "") + '</b>'

        published_datetime = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        time_difference = datetime.now(timezone.utc) - published_datetime
        if time_difference > timedelta(seconds=update_freq):
            print(f'Obsolete [{ttl}]: {time_difference}, {datetime.now(timezone.utc)}, {published_datetime}')
            continue

        min_hourly_regx = re.search(r'Hourly Range</b>: \$([^\.-]+)', entry['summary'])
        if min_hourly_regx and int(min_hourly_regx[1]) < min_hourly_salary:
            print(f'Cheap [{ttl}]: {min_hourly_regx[1]}')
            continue

        message = f'{ttl}\n{entry.summary}'
        print(f'Tg [{ttl}]')
        bot = telegram.Bot(token=bot_token)
        run(send_message(bot, chat_id, message))
            

if __name__ == '__main__':
    main()
