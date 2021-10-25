import pymongo
import dotenv
from pymongo import MongoClient as MC

dbconn = dotenv.dotenv_values('.env','CONNURL')['CONNURL']
cluster = MC(dbconn)
db = cluster["Bestemmiometro"]
collection = db["Chats"]

result = collection.find_one({"_id":"chatProva"})
print(result)

'''
collection.update_one(
    {"_id":"chatProva"},
    {
        "$push":                                     ---> Adds something to an embedded
        {
            "users":{"_id":"Test1","score":0}
        }
    }
)  
''' 
'''
collection.update_one(
    {
        "_id":"chatProva", 
        "Users":{"$elemMatch":{"_id":"GabboCosti"}}  ---> Updates something into an embedded
    },
    {
        "$set":{"Users.$.score":0}
    }
)
'''
'''
collection.update_one(
    {
        "_id":"chatProva"
    },
    {
        "$pull":{"users":{
            "_id":"Test1","score":0
        }}
    }
)
'''
'''
collection.update_one(
    {
        "_id":"chatProva"
    },                          --->removes the entire array
    {
        "$unset":{"users":""}
    }
)
'''

#collection.update_one(
#    {"_id":"chatProva"},
#    {"$push":{"Users":{"_id":"GabboCosti","score":2}}}
#)
#
#collection.update_one(
#    {"_id":"chatProva"},
#    {"$push":{"Users":{"_id":"GabboCosti","score":3}}}
#)
#
#collection.update_one(
#    {"_id":"chatProva"},
#    {"$push":{"Users":{"_id":"GabboCosti","score":4}}}
#)
#
#collection.update_one(
#    {"_id":"chatProva"},
#    {"$push":{"Users":{"_id":"GabboCosti","score":5}}}
#)
#
#collection.find_one
#(
#    {"_id":"chatProva"}
#)

result = collection.find_one(
    {"_id":"chatProva", 
        "Users":
            {"$elemMatch":
                {"_id":"GabboCosti"}}},
    {"Users.$":1}
)
print(result)
print(result["Users"][0])
