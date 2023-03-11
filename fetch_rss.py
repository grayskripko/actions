import feedparser
import os
import datetime
import telegram
from asyncio import run
    

async def send_message(bot, chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)
    
def main():
    rss_feed_url = os.getenv('RSS_FEED_URL')
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_TO')
    update_freq = float(os.getenv('UPDATE_FREQ'))
    
#     update_freq = 30 * 60  # test
    feed = feedparser.parse(rss_feed_url)
    
    for entry in feed.entries:
        published_datetime = datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        time_difference = datetime.datetime.now(datetime.timezone.utc) - published_datetime
        is_obsolete = time_difference > datetime.timedelta(minutes=update_freq)

        if not is_obsolete:
#             print(entry)
            ttl = entry.title.replace(" - Upwork", "")
            message = f'{ttl}\n{entry.summary}'
            print(message)
            bot = telegram.Bot(token=bot_token)
            run(send_message(bot, chat_id, message))
#             send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id=' + \
#                 f'{chat_id}&parse_mode=Markdown&text={message}'
#             response = requests.get(send_text)
            

if __name__ == '__main__':
    main()
