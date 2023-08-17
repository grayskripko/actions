import feedparser, os
from datetime import datetime, timezone, timedelta
import telegram, html, re
from urllib.parse import quote
from asyncio import run
    

def get_url():
    prv = os.getenv('UPWORKER_PRV')
    url = 'https://www.upwork.com/ab/feed/jobs/rss?' + prv +\
        '&api_params=1&contractor_tier=2,3&paging=0;10&sort=recency&verified_payment_only=1' +\
        '&hourly_rate=50-&job_type=hourly&proposals=0-4,5-9,10-14,15-19&q='+\
        'skills:("google analytics" OR airtable OR "google sheets" OR excel OR sql OR dashboard OR "data analytics" OR "data analysis")'
    return quote(url, safe=':/&=?')

async def send_message(bot, chat_id, message):
    await bot.send_message(
        chat_id=chat_id, text=html.unescape(
            re.sub('\n\n', '\n', re.sub(r'<br\s*/>', '\n', message))),
        parse_mode=telegram.constants.ParseMode.HTML)
    
def main():
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_TO')

    update_freq = 10 + 1
    min_hourly_salary = 25
    
    feed = feedparser.parse(get_url())
    
    for i, entry in enumerate(feed.entries):
        if i == 0:
            print(f'{entry.title}, {str(entry.published)}')
        published_datetime = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        time_difference = datetime.now(timezone.utc) - published_datetime
        is_obsolete = time_difference > timedelta(minutes=update_freq)
        
        if not is_obsolete:
            min_hourly_regx = re.search(r'Hourly Range</b>: \$([^\.-]+)', entry['summary'])
            if min_hourly_regx and int(min_hourly_regx[1]) < min_hourly_salary:
               continue
            ttl = '<b>' + entry.title.replace(" - Upwork", "") + '</b>'
            message = f'{ttl}\n{entry.summary}'
            print(message)
            bot = telegram.Bot(token=bot_token)
            run(send_message(bot, chat_id, message))
            

if __name__ == '__main__':
    main()
