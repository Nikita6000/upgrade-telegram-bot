import telegram
from credentials.telegram import BOT_TOKEN


if __name__ == "__main__":
    bot = telegram.Bot(token=BOT_TOKEN)
    resp = bot.setWebhook(
        url=f"https://upgrade-244619.appspot.com/{BOT_TOKEN}",
        certificate='cert.pem'
    )
    print(resp)
