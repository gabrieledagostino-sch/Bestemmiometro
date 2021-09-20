import telebot as tb
import dotenv 
import requests

userBest = dict()

def main():
    URL_BASE = BASE_URL = "http://bestemmie.org/api/{endpoint}?limit=900"
    token = dotenv.dotenv_values('.env','TOKEN')['TOKEN']
    bot = tb.TeleBot(token)

    @bot.message_handler()
    def test(message):
        bot.reply_to(message=message, text=message.text)
        response = requests.get(BASE_URL.format(endpoint="bestemmie"))
        response.raise_for_status()
        list = [a['bestemmia'] for a in response.json()['results'] if a['bestemmia'] in message.text.upper()]
        print(list)
        if message.from_user.id not in userBest:
            userBest[message.from_user.id] = dict()
        for bestemmia in list:
            if bestemmia not in userBest[message.from_user.id]:
                userBest[message.from_user.id][bestemmia] = 0
            userBest[message.from_user.id][bestemmia] += 1
        print(userBest)
    

    bot.polling()

if __name__ == "__main__":
    main()