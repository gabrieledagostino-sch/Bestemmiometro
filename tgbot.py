from os import linesep
import telebot as tb
import dotenv 
import requests
from telebot.util import MAX_MESSAGE_LENGTH

userBest = dict()
userTotal = dict()

def main():
    BASE_URL = "http://bestemmie.org/api/{endpoint}?limit=900"
    token = dotenv.dotenv_values('.env','TOKEN')['TOKEN']
    bot = tb.TeleBot(token)
    response = requests.get(BASE_URL.format(endpoint="bestemmie")).json()['results']

    @bot.message_handler(commands=['score'])
    def score(message):
        text = ''
        tokenString = str(message.from_user.id) + str(message.chat.id)
        if tokenString not in userBest:
            bot.reply_to(message=message, text='Non stai partecipando alla gara, cresci porco di quel tuo dio')
            return
        text += f'{userTotal[message.from_user.id][message.chat.id][1]} : {userTotal[message.from_user.id][message.chat.id][0]}\n'
        for key,val in sorted(userBest[tokenString].items(), key=lambda item: item[1])[::-1]:
            text += f'{key} : {val}\n'
        print(text)
        bot.reply_to(message=message, text=text)
    
    @bot.message_handler(commands=['leaderBoard'])
    def leaderboard(message):
        text = ''
        for key,val in userTotal.items():
            text += f'{val[message.chat.id][1]} : {val[message.chat.id][0]}\n'
        bot.reply_to(message=message, text=text)
         


    @bot.message_handler(func=lambda item: item.text[0] != '/')
    def test(message):
        list = [a['bestemmia'] for a in response if a['bestemmia'] in message.text.upper()]
        print(list)
        print(str(message.from_user.id)+str(message.chat.id))
        tokenString = str(message.from_user.id)+str(message.chat.id)
        if tokenString not in userBest:
            userBest[tokenString] = dict()
            userTotal[message.from_user.id] = dict()
            userTotal[message.from_user.id][message.chat.id] = [0, message.from_user.first_name]
        for bestemmia in list:
            if bestemmia not in userBest[tokenString]:
                userBest[tokenString][bestemmia] = 0
            userBest[tokenString][bestemmia] += 1
        userTotal[message.from_user.id][message.chat.id][0] += len(list)
        print(userBest)
    
    
    bot.polling()

if __name__ == "__main__":
    main()