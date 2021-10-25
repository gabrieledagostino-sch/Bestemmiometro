# -*- coding: UTF-8 -*-
import requests                         #requests, used for the bestemmie.org API
import telebot as tb                    #the telegram bot API
import dotenv                           #used for enviroment variables, to hide sensible information
from pymongo import MongoClient as MC   #the API for mongodb
#import asyncio -> a possible todo : make the db operations async


#some constants used through the code
RISPOSTA_NO_BESTEMMIE = 'Grande, non hai mai bestemmiato, proprio un grande, grandissimo, ti farei un quadro, nono davvero sei proprio un grande'
BESTEMMIE_API_URL = "http://bestemmie.org/api/{endpoint}?limit=900"
SCORE_HEADER = "Grande fra hai bestemmiato {score} volte, proprio un fratello\n"
LEADERBOARD_LENGTH = 9

'''
    la struttura dati del database
    chats
    {
        "_id":chatID                    #the chat ID
        Users:
        [
            {
                "_id":userID            #the ID of the user
                "nome"->string          #name of the user
                bestemmia:str -> int    #a normal profanity with the count it got used
            }
        ]
    }
'''

def putChat(chatID, collection):
    '''
        adds the chat into the database
    '''
    post = {"_id":chatID, "Users":list()}
    collection.insert_one(post)


def ensureChatExistence(chatID, collection):
    '''
        called if i have to do someting with a chat
        it ensure that a chat exists (if it doesn't exists it creates it)
    '''
    result = collection.find_one({"_id":chatID})
    if result is None:
        putChat(chatID, collection)

def putUser(chatID, userID, nome, collection):
    '''
        adds an user into the databse
    '''

    print(chatID, userID, nome)
    post = {"_id":userID, "score":0, "nome":nome}
    collection.update_one(
        {"_id":chatID},
        {"$push":{"Users":post}}
    )
    return post

def getUser (chatID, userID, nome, collection):
    '''
        checks if the user exists
        if it exists it gives it back as a dictionary
        if it doesn't exist adds it  and returns it
    '''
    result = collection.find_one(
        {
            "_id":chatID , 
            "Users":{"$elemMatch":{"_id":userID}}
        }, 
        {"Users.$":1}
    )
    print (result)
    if result is None:
        result = putUser(chatID, userID, nome, collection)
    else:
        result = result['Users'][0]
    return result

def getUsers(chatId, collection):
    '''
        get all users in a chat as a list
    '''
    result = collection.find_one({"_id":chatId})
    result = result['Users']
    return result

def addBestemmia(chatID, userID, bestemmia, collection):
    '''
        goes into the right chat, selects the right user
        increments score and profanity
    '''
    collection.update_one(
        {
            "_id":chatID,
            "Users":{"$elemMatch":{"_id":userID}}
        },
        {
            "$inc":{"Users.$.score":1,f"Users.$.{bestemmia}":1}
        }
    )


def allBestemmie():
    '''
        i go through all the profanities in bestemmie.org and selects the most used
    '''
    #formats the URL
    url = BESTEMMIE_API_URL.format(endpoint="bestemmie")
    bestemmie = []

    while url is not None:
        response = requests.get(url)
        #this line here selects all the profanity strings that have been voted more than 5 time
        bestemmie.extend(best['bestemmia'] for best in response.json()['results'] if best['count']>5)
        url = response.json()['next'] or None

    return bestemmie

def main():
    
    #gets the enviroment values
    token = dotenv.dotenv_values('.env','TOKEN')['TOKEN']
    dbconn = dotenv.dotenv_values('.env','CONNURL')['CONNURL']

    #connects to the mongodb database
    cluster = MC(dbconn)
    db = cluster["Bestemmiometro"]
    collection = db["Chats"]
    
    #initializes the bot
    bot = tb.TeleBot(token)

    #gets the profanities
    response = allBestemmie()

    @bot.message_handler(commands=['score'])
    def score(message):
        '''
            calls getChat with the current chatId
            calls getUser with the current usId
            sorts the profanity list
            scrolls through each profanity
            if the user never said a profanity says RIPOSTA_NO_BESTEMMIE
        '''
        #usual function header

        text = ''
        usId = str(message.from_user.id)
        chatId = str(message.chat.id)
        nome = str(message.from_user.first_name)

        ensureChatExistence(chatId, collection) 
        
        user = getUser(chatId, usId, nome, collection)

        #sorted lambda

        z = lambda item: (item[0] != 'nome' and item[0] != 'score' and item[0] != '_id')

        #sorts the list in profanity most used by the user

        sortedList = [(key,value) for key,value in user.items()]
        sortedList = list(filter(z, sortedList))
        sortedList = sorted(sortedList, key=lambda item: item[1])
        
        #build the response

        text += SCORE_HEADER.format(score=user['score'])
        
        for (key,val) in sortedList[::-1]:
            text += f'{key} : {val}\n'
        if user["score"] == 0: #if the user never used profanities
            text = RISPOSTA_NO_BESTEMMIE
        
        bot.reply_to(message=message, text=text)
    
    
    @bot.message_handler(commands=['leaderboard'])
    def leaderboard(message):
        '''
            same header of score
            goes in all the users in the chat and sorts them by score
            prints the first 10
        '''
        text = ''
        usId = str(message.from_user.id)
        chatId = str(message.chat.id)
        nome = str(message.from_user.first_name)
        
        ensureChatExistence(chatId, collection)
        users = getUsers(chatId, collection)
        
        
        for user in sorted(users, key=lambda item: item["score"])[:-LEADERBOARD_LENGTH:-1]:
            text += f'{user["nome"]} : {user["score"]}\n'

        bot.reply_to(message=message, text=text)
         

    
    @bot.message_handler(func=lambda item: item.text[0] != '/')
    def bestemmioSniffer(message):
        '''
            same header as score function
            i do a list comprehension with all the profanities in the message
            i add the profanity in the table of the user
        '''
        #list comprehension with profanities
        list = [a for a in response if a in message.text.upper()]

        #usual header
        usId = str(message.from_user.id)
        chatId = str(message.chat.id)
        user = None
        nome = str(message.from_user.first_name)

        ensureChatExistence(chatId, collection)
        user = getUser(chatId, usId, nome, collection)

        #goes through each profanity and adds it
        for bestemmia in list:
            addBestemmia(chatId, usId, bestemmia, collection)
        
        #increments the total score
        user['score'] += len(list)
    
    
    bot.polling()



if __name__ == "__main__":
    main()