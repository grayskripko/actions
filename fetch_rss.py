import feedparser
import telegram
import os

def send_message(bot, chat_id, message):
    bot.send_message(chat_id=chat_id, text=message)

def main():
    rss_feed_url = os.getenv('RSS_FEED_URL')
    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_TO')

    # Fetch the RSS feed
    feed = feedparser.parse(rss_feed_url)
    
    print(11)

    # Iterate through the feed entries and send new items to Telegram
    for entry in feed.entries:
        # Check if the entry is newer than the last time we checked the feed
        # You can save the last timestamp in a file or database to persist across runs
        print(type(entry))
        if 'last_checked_timestamp' not in entry:
            entry.last_checked_timestamp = entry.published_parsed
            continue

        if entry.published_parsed > entry.last_checked_timestamp:
            entry.last_checked_timestamp = entry.published_parsed
            message = f'{entry.title}\n{entry.link}'
            bot = telegram.Bot(token=bot_token)
            print(message)
            send_message(bot, chat_id, message)

if __name__ == '__main__':
    main()
