from os import linesep
import telebot as tb
import dotenv 
import requests
from telebot.util import MAX_MESSAGE_LENGTH

RISPOSTA_NO_BESTEMMIE = 'Non stai partecipando alla gara, cresci porco di quel tuo dio'

#Sistemare questi dizionari, troppo complessi
#prolly é meglio fare una classe Utente con ste robe
userBest = dict()
'''
    userBest -> {key:bestemmia, val:conto}
'''
userTotal = dict()
'''
    userTotal -> { key:chatId , val: [Nome,conta] }
'''

def main():
    BASE_URL = "http://bestemmie.org/api/{endpoint}?limit=900"
    token = dotenv.dotenv_values('.env','TOKEN')['TOKEN']
    bot = tb.TeleBot(token)
    response = requests.get(BASE_URL.format(endpoint="bestemmie")).json()['results']

    @bot.message_handler(commands=['score'])
    def score(message):
        '''
            prende il tokenString (user id + chat id)
            nel'if controlla se il dizionario é vuoto
            controlla ogni bestemmia detta e quante volte nel for
            TODO Se l'utente ha inviato un messaggio spunterá 0 come totale, si vuole mandare lo stesso il messaggio RISPOSTA_NO_BESTEMMIE
        '''
        text = ''
        tokenString = str(message.from_user.id) + str(message.chat.id)
        if tokenString not in userBest:
            bot.reply_to(message=message, text=RISPOSTA_NO_BESTEMMIE)
            return
        text += f'{userTotal[message.from_user.id][message.chat.id][1]} : {userTotal[message.from_user.id][message.chat.id][0]}\n'
        for key,val in sorted(userBest[tokenString].items(), key=lambda item: item[1])[::-1]:
            text += f'{key} : {val}\n'
        print(text)
        bot.reply_to(message=message, text=text)
    
    @bot.message_handler(commands=['leaderBoard'])
    def leaderboard(message):
        '''
            prende gli elementi del dizionario userTotal e li sorta per numero di bestemmie totale
        '''
        text = ''
        print(userTotal.items())
        for key,val in sorted(userTotal.items(), key = lambda item: item[1][message.chat.id][0])[::-1]:
            print('yoo')
            text += f'{val[message.chat.id][1]} : {val[message.chat.id][0]}\n'
        bot.reply_to(message=message, text=text)
         


    @bot.message_handler(func=lambda item: item.text[0] != '/')
    def test(message):
        '''
            faccio una list comprehension con tutte le bestemmie contenute nel messaggio riconosciute su bestemmie.org
            se l'utente non é inizializzato lo si inizializza
            si aggiorna il dizionario delle bestemmie dette e il totale
        '''
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