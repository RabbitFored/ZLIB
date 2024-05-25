
import os
from telegram import TelegramError
import pymongo
from time import sleep
from telegram.ext.dispatcher import run_async

myclient = pymongo.MongoClient(
    os.environ['mongouri'])
database = myclient['bookbot']
collection = database["usercache"]

@run_async
def broadcast(update , context):
    chat_id = update.message.chat_id

    sudoers = [1201465581 , 1520625615 , 1809735866,1775541139]
    fname = update.effective_message
    if chat_id in sudoers :
        chat = (collection.find({}, {'userid': 1, '_id': 0}))
        chats = [sub['userid'] for sub in chat]
        failed = 0
        update.message.reply_text(f"Broadcasting to {len(chats)} users.")

        for chat in chats:
          try:
              context.bot.forward_message(chat_id=chat,
                               from_chat_id=update.message.reply_to_message.chat.id,
                               message_id=update.message.reply_to_message.message_id)
              sleep(2)
          except TelegramError as e:
                print(f"error : {e}")
                failed += 1
                print(f"Cannot message {chat}")
          except:
                failed += 1
                print(f"Cannot message {chat}")


        update.message.reply_text("Broadcast complete. {} users failed to receive the message, probably due to being kicked.".format(failed))
    else:
        context.bot.send_message(chat_id=1201465581, text="Someone tried to access broadcast command"
                                                  "\nUser Info :"
                                                  f"User Id = {chat_id}"
                                                  f"First name = {fname}"
                                                  f"Message = {update.message.reply_to_message.text}")