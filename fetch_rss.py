import feedparser, os
from datetime import datetime, timezone, timedelta
import telegram, html, re
from urllib.parse import quote
import time
from asyncio import run
    

SETTINGS = dict(
    update_freq = (10 + 1) * 60,
    min_hourly_salary = 20,
    queries = [
        '(skills:("data analysis" OR R OR etl OR dashboard OR pandas OR "power bi" OR tableau OR looker) OR (skills:("google sheets" OR excel OR airtable OR sql) AND NOT skills:(seo OR lead OR m arket OR "data entry"))) AND NOT (India OR "full stack")'#,
        # 'skills:(chatgpt OR openai OR llm) AND NOT Midjourney'
        ])
    
def get_url(query):
    assert "skills:(" in query
    fulltime_type = ['', '&workload=full_time'][0]
    duration_v3=['', '&duration_v3=months,semester,ongoing'][0]
    url = f'https://www.upwork.com/ab/feed/jobs/rss?{os.getenv("UPWORKER_PRV")}&' +\
        'api_params=1&contractor_tier=2,3&paging=0;10&sort=recency&verified_payment_only=1&' +\
        f'job_type=hourly&hourly_rate=40-{fulltime_type}{duration_v3}&q={query}'
    # .replace("&", "%26")
    print(url)
    time.sleep(2)
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
    # print(get_url(SETTINGS['queries'][0]))
    feed = [(qr, entr) for qr in SETTINGS['queries'] for entr in feedparser.parse(get_url(qr)).entries]
    print(len(feed))
    
    processed = []
    for quer, entry in feed:
        short_qr = re.search(r'skills:\("?(\w+)', quer).group(1)
        ttl = f'<b>{entry.title.replace(" - Upwork", "")}</b> [{short_qr}]'

        published_datetime = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        time_diff = datetime.now(timezone.utc) - published_datetime
        if time_diff > timedelta(seconds=SETTINGS['update_freq']):
            print(f'- Old [{ttl}]: {strfdelta(time_diff)}')
            continue

        min_hourly_regx = re.search(r'Hourly Range</b>: \$([^\.-]+)', entry['summary'])
        if min_hourly_regx and int(min_hourly_regx[1]) < SETTINGS['min_hourly_salary']:
            print(f'- Cheap [{ttl}]: {min_hourly_regx[1]}')
            continue

        message = f'{ttl}\n{entry.summary}'
        if len(message) > 4000:
            message = f'{message[:2000]}\n...\n{message[-2000:]}'

        if message in processed:
            print(f'- Duplicated [{ttl}]')
            continue

        processed.append(message)
        print(f'+ Send [{ttl}]')
        bot = telegram.Bot(token=bot_token)
        run(send_message(bot, chat_id, message))
            

if __name__ == '__main__':
    main()
