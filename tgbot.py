import telebot as tb
import dotenv 
import requests

RISPOSTA_NO_BESTEMMIE = 'Non stai partecipando alla gara, cresci porco di quel tuo dio'

'''
users -> {userId -> User}
'''
users = dict()

class User:
    #chats{ chatId -> {totale : count}{bestemmia : totale};

    def __init__(self, nome, chats = dict()):
        #qui dichiaro il dizionario
        self.chats = chats
        self.nome = nome



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
        usId = str(message.from_user.id)
        chatId = str(message.chat.id)
        
        if (usId not in users) or (chatId not in users[usId].chats) or (users[usId].chats[chatId]['totale'] == 0):
            
            bot.reply_to(message=message, text=RISPOSTA_NO_BESTEMMIE)
            return
        
        user = users[usId].chats[chatId]

        for key,val in sorted(user.items(), key=lambda item: item[1])[::-1]:
            text += f'{key} : {val}\n'
        
        bot.reply_to(message=message, text=text)
    
    @bot.message_handler(commands=['leaderboard'])
    def leaderboard(message):
        '''
            prende gli elementi del dizionario userTotal e li sorta per numero di bestemmie totale
        '''
        text = ''
        usId = str(message.from_user.id)
        chatId = str(message.chat.id)
        
        unsortedDic = [us for key, us in users.items() if chatId in us.chats]
        
        for user in sorted(unsortedDic, key=lambda item: item.chats[chatId]['totale']):
            text += f'{user.nome} : {user.chats[chatId]["totale"]}\n'

        bot.reply_to(message=message, text=text)
         


    @bot.message_handler(func=lambda item: item.text[0] != '/')
    def bestemmioSniffer(message):
        '''
            faccio una list comprehension con tutte le bestemmie contenute nel messaggio riconosciute su bestemmie.org
            se l'utente non é inizializzato lo si inizializza
            si aggiorna il dizionario delle bestemmie dette e il totale
        '''
        list = [a['bestemmia'] for a in response if a['bestemmia'] in message.text.upper()]
        
        usId = str(message.from_user.id)
        chatId = str(message.chat.id)
        user = None

        print(usId)

        if usId not in users:
            users[usId] = User(message.from_user.first_name)
        print(users[usId])
        user = users[usId].chats
        if chatId not in user:
            user[chatId] = dict()
            #qui dichiaro il totale
            user[chatId]['totale'] = 0

        for bestemmia in list:
            if bestemmia not in user[chatId]:
                user[chatId][bestemmia] = 0
            user[chatId][bestemmia] += 1
        
        print(user[chatId])
        print(user)
        #qui lo aggiorno
        user[chatId]['totale'] += len(list)
    
    
    bot.polling()

if __name__ == "__main__":
    main()