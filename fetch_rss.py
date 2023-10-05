import feedparser, os
from datetime import datetime, timezone, timedelta
import telegram, html, re
from urllib.parse import quote
import time
from asyncio import run
    

SETTINGS = dict(
    update_freq = (10 + 0.5) * 60,
    min_hourly = 10,
    target_hourly = 30,
    full_week =['', '&workload=full_time'][False],
    more_month=['', '&duration_v3=months,semester,ongoing'][False],
    queries  = [f'{x} NOT India' for x in [
        'skills:("data analysis" OR "power bi" OR tableau OR R OR etl OR dashboard)',
        'skills:("dbt OR t-sql OR airflow OR spark)',
        # 'skills:("google analytics")'
        ]])
    
def get_url(query):
    assert "skills:(" in query
    url = f'https://www.upwork.com/ab/feed/jobs/rss?{os.getenv("UPWORKER_PRV")}&' +\
        'api_params=1&sort=recency&verified_payment_only=1&paging=0;10&' +\
        f'job_type=hourly&hourly_rate={SETTINGS["target_hourly"]}-' +\
        f'{SETTINGS["full_week"]}{SETTINGS["more_month"]}&q={query}'
    # .replace("&", "%26")
    click_url = re.sub(
        r'.*/rss\?\*\*\*&', 
        'https://www.upwork.com/nx/jobs/search/?', url)
    print(click_url)
    time.sleep(2)
    return quote(url, safe=':/&=?')

def main():
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_TO')
    # print(get_url(SETTINGS['queries'][0]))
    feed = [(qr, entr) for qr in SETTINGS['queries'] for entr in feedparser.parse(get_url(qr)).entries]
    print(len(feed))
    
    processed = []
    for quer, entry in feed:
        short_qr = re.search(r'skills:\("?(\w+)', quer).group(1) if len(SETTINGS['queries']) > 1 else ''
        ttl = f'<b>{entry.title.replace(" - Upwork", "")}</b> [{short_qr}]'

        published_datetime = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        time_diff = datetime.now(timezone.utc) - published_datetime
        if time_diff > timedelta(seconds=SETTINGS['update_freq']):
            print(f'- Old [{ttl}]: {strfdelta(time_diff)}')
            continue

        min_hourly_regx = re.search(r'Hourly Range</b>: \$([^\.-]+)', entry.summary)
        if min_hourly_regx and int(min_hourly_regx[1]) < SETTINGS['min_hourly']:
            print(f'- Cheap [{ttl}]: {min_hourly_regx[1]}')
            continue

        us_job = 'Only freelancers located in the United States may apply'
        if us_job in entry.summary:
            print(f'- US only [{ttl}]')
            continue
            # ttl += ' [US only]'

        message = f'{ttl}\n{entry.summary}'
        if len(message) > 4000:
            message = f'{message[:2000]}\n...\n{message[-2000:]}'

        if entry.summary in processed:
            print(f'- Duplicated [{ttl}]')
            continue
        processed.append(entry.summary)
        
        print(f'+ Send [{ttl}]')
        bot = telegram.Bot(token=bot_token)
        run(send_message(bot, chat_id, message))
            

async def send_message(bot, chat_id, message):
    await bot.send_message(
        chat_id=chat_id, text=html.unescape(
            re.sub('\n\n', '\n', re.sub(r'<br\s*/>', '\n', message))),
        parse_mode=telegram.constants.ParseMode.HTML)

def strfdelta(tdelta):
    minutes, seconds = divmod(tdelta.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h:{minutes}m:{seconds}s"

if __name__ == '__main__':
    main()
