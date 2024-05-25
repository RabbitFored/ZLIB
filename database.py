import os
import pymongo

def scrape(data):
    myclient = pymongo.MongoClient(
      os.environ['mongouri']
)
    database = myclient['bookbot']

    userid = data.message.chat.id
    chattype = data.message.chat.type

    if chattype == 'private':
        collection = database["usercache"]
    elif (chattype == 'group') or (chattype == 'supergroup'):
        collection = database["groupcache"]

    manybase = myclient['manybase']
    if chattype == 'private':
        cluster = manybase["totalcache"]
    elif (chattype == 'group') or (chattype == 'supergroup'):
        cluster = manybase["groupical"]

    firstseen = data.message.date
    result = collection.find_one({'userid': userid})
    manyres = cluster.find_one({'userid': userid})
    try:
        result['userid']
        userexist = True
    except:
        userexist = False

    try:
        manyres['userid']
        exuser = True
    except:
        exuser = False

    title = data.message.chat.title
    entireadmin = data.message.chat.all_members_are_administrators
    username = data.message.chat.username
    firstname = data.message.chat.first_name
    lastname = data.message.chat.last_name


    scraped = {}
    scraped['userid'] = userid
    scraped['chattype'] = chattype

    if (chattype == 'group') or (chattype == 'supergroup'):
        scraped['title'] = title
        scraped['type'] = chattype
        scraped['username'] = username
        scraped['entireadmin'] = entireadmin
        scraped['firstseen'] = firstseen
    else:
        scraped['username'] = username
        scraped['firstname'] = firstname
        scraped['lastname'] = lastname
        scraped['is-banned'] = False
        scraped['firstseen'] = firstseen

    if (userexist == False):
        collection.insert_one(scraped)

    if (exuser == False):
        cluster.insert_one(scraped)

