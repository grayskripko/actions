import json
import platform
import subprocess
import feedparser, os
from datetime import datetime, timedelta, timezone
import requests
import telegram, html, re
from urllib.parse import quote
import psycopg2
import pytz
import time
from asyncio import run
    

SETTINGS = dict(
    min_hourly = 20,
    target_hourly = 30,
    full_week =['', '&workload=full_time'][False],
    more_month=['', '&duration_v3=months,semester,ongoing'][False],
    queries  = [f'{x} NOT India' for x in [
        'skills:("data analysis") ("data analyst" OR "product analyst" OR R)'
        # 'skills:("power bi") NOT (India)'
        # 'skills:("data analysis" OR "power bi" OR tableau OR R OR etl OR dashboard) NOT (India OR skills:("market research"))',
        # 'skills:(dbt OR t-sql OR airflow OR spark)',
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

def get_prev_access(token=None):
    gist_id = '4b2de7378ef2847345660b9c544fc9eb'
    response = requests.get(
        f'https://api.github.com/gists/{gist_id}', 
        headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    prev_str = json.loads(response.text)['files']['tgup.txt']['content']
    prev_access = datetime.strptime(prev_str.split('.')[0], "%Y-%m-%d %H:%M:%S")\
        .replace(tzinfo=timezone.utc)
    # prev_access = pytz.timezone('Etc/GMT+3').localize(prev_access_notz)
    print(f'prev_access: {prev_access}')
    
    updated_content = {'files': {'tgup.txt': {'content': str(datetime.now())}}}
    response = requests.patch(
        f'https://api.github.com/gists/{gist_id}', 
        headers={'Authorization': f'Bearer {token}'}, 
        json=updated_content)
    assert response.status_code == 200
    return prev_access

    # with psycopg2.connect(conn_str) as conn:
    #     with conn.cursor() as cur:
    #         cur.execute('SELECT * FROM LAST_ACC;')
    #         last_acc = cur.fetchone()[0]
    #         print(f'Since prev access: {datetime.now(timezone.utc) - last_acc}')
    #         cur.execute('UPDATE LAST_ACC SET time = NOW() WHERE time = %s;', (last_acc,))
    #         conn.commit()
    #         return last_acc

def main():
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_TO')
    gitpat = os.getenv('GITPAT')
    # neon_str = os.getenv('NEON_STR')
    # print(get_url(SETTINGS['queries'][0]))

    assert([x is not None for x in [bot_token, chat_id, gitpat]])
    feed = [(qr, entr) for qr in SETTINGS['queries'] for entr in feedparser.parse(get_url(qr)).entries]
    prev_acc = get_prev_access(gitpat)
    
    processed = []
    for quer, entry in feed:
        short_qr = re.search(r'skills:\("?(\w+)', quer).group(1)
        ttl = f'<b>{entry.title.replace(" - Upwork", "")}</b> [{short_qr}]'

        published_datetime = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        time_diff = prev_acc - published_datetime
        if time_diff > timedelta(seconds=0):
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
        print('bot token', bot_token)
        bot = telegram.Bot(token=bot_token)
        run(send_message(bot, chat_id, message))

async def send_message(bot, chat_id, message):
    await bot.send_message(
        chat_id=chat_id, text=html.unescape(
            re.sub('\n\n', '\n', re.sub(r'<br\s*/>', '\n', message))),
        parse_mode=telegram.constants.ParseMode.HTML)

def strfdelta(tdelta):
    days = tdelta.days
    minutes, seconds = divmod(tdelta.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    total_hours = days * 24 + hours
    return f"{total_hours}h:{minutes}m:{seconds}s"


if __name__ == '__main__':
    # print(get_prev_access(gitpat))
    # subprocess.run(["sudo", "hwclock", "-s"])
    # why don't run on local machine: bot_token, chat_id are missed
    main()
