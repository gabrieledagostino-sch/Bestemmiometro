import telebot as tb
import dotenv 
import requests
#import asyncio -> a possible todo : make the db operations async
import pymongo
from pymongo import MongoClient as MC
# -*- coding: UTF-8 -*-

RISPOSTA_NO_BESTEMMIE = 'Grande, non hai mai bestemmiato, proprio un grande, grandissimo, ti farei un quadro, nono davvero sei proprio un grande'

'''
    la struttura dati del database
    chats {chatis -> userDict}
    userDict{userId -> bestemmieDict, score}
    bestemmieDict{bestemmia -> volteUsata}
'''
'''
    Wrapper functions for db
'''
def putChat(chatID, collection):
    post = {"_id":chatID, "users":dict()}
    collection.insert_one(post)


def ensureChatExistence(chatID, collection):
    result = collection.find_one({"_id":chatID})
    if result is None:
        putChat(chatID, collection)

def getUser (chatID, userID, collection):
    collection.find_one({"_id":chatID , "Users":{"$elemMatch":{"_id":userID}}}, {"Users.$":1})
    pass

def main():
    BASE_URL = "http://bestemmie.org/api/{endpoint}?limit=900"
    
    token = dotenv.dotenv_values('.env','TOKEN')['TOKEN']
    dbconn = dotenv.dotenv_values('.env','CONNURL')['CONNURL']
    cluster = MC(dbconn)
    db = cluster["Bestemmiometro"]
    collection = db["Chats"]
    
    bot = tb.TeleBot(token)
    response = requests.get(BASE_URL.format(endpoint="bestemmie")).json()['results']

    @bot.message_handler(commands=['score'])
    def score(message):
        '''
            calls getChat with the current chatId
            calls getUser with the current usId
            scrolls through each profanity
            if the user never said a profanity says RIPOSTA_NO_BESTEMMIE
        '''
        text = ''
        usId = str(message.from_user.id)
        chatId = str(message.chat.id)

        chat = ensureChatExistence(chatId, collection) 
        
        user = getUser(chatId, usId, collection)

        
        for key,val in sorted(user.items(), key=lambda item: item[1])[::-1]:
            text += f'{key} : {val}\n'
        if user["score"] == 0:
            text = RISPOSTA_NO_BESTEMMIE
        
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
        
        for user in sorted(unsortedDic, key=lambda item: item.chats[chatId]['totale'])[::-1]:
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

        if chatId not in users:
            users[usId] = User(message.from_user.first_name, {chatId:{'totale':0}})
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