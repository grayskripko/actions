import feedparser
import telegram
import os
import datetime
import requests
    

def main():
    rss_feed_url = os.getenv('RSS_FEED_URL')
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_TO')
    update_freq = float(os.getenv('UPDATE_FREQ'))
    
    print(bot_token)
    print(len(bot_token))
    update_freq = 24 * 60  # test

    feed = feedparser.parse(rss_feed_url)
    
    for entry in feed.entries:
        published_datetime = datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        time_difference = datetime.datetime.now(datetime.timezone.utc) - published_datetime
        is_obsolete = time_difference > datetime.timedelta(minutes=update_freq)

        if not is_obsolete:
            print(entry)
            message = f'{entry.title.replace(" - Upwork", "")}\n{entry.summary}'
            print(message)
            send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id=' + \
                f'{chat_id}&parse_mode=Markdown&text={message}'
            response = requests.get(send_text)
            

if __name__ == '__main__':
    main()
