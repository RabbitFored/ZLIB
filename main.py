import os
import requests
import emoji
from libgensearch import Libgen
import json5
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import telegram
from telegram.ext import Updater, CommandHandler
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update
from telegram.ext import Updater, MessageHandler, Filters, InlineQueryHandler, CommandHandler, CallbackContext, MessageFilter
from telegram.utils.helpers import escape_markdown
import alive
from alive import keep_alive
import broadcast
import database
from hurry.filesize import size


class FilterAwesome(MessageFilter):

  def filter(self, message):
    id = message.chat.id
    status = telegram.Bot(token=os.environ['TOKEN']).getChatMember(
      "@theostrich", id)["status"]
    allowed = ["administrator", "member", "creator"]

    return status not in allowed


filter_awesome = FilterAwesome()


class FilterAwesomes(MessageFilter):

  def filter(self, message):
    id = message.chat.id
    status = telegram.Bot(token=os.environ['TOKEN']).getChatMember(
      "@theostrich", id)["status"]
    allowed = ["administrator", "member", "creator"]
    print(status not in allowed)
    return status in allowed


filter_awesomes = FilterAwesomes()

class FilterT(MessageFilter):

  def filter(self, message):
    return True


filterT = FilterT()


def start(update, context):
  username = update.message.chat.username

  keyboard = [
    [telegram.InlineKeyboardButton("Get help", url="t.me/ostrichdiscussion")],
  ]

  reply_markup = telegram.InlineKeyboardMarkup(keyboard)

  message = f'''
<b>Hey @{username} 👋
I am Zlibrary bot 📖

Use /help to know how to use me</b>
    '''
  context.bot.send_message(
    chat_id=update.effective_chat.id,
    text=message,
    parse_mode='html',
    #reply_markup=reply_markup,
    disable_web_page_preview=True)
  try:
    database.scrape(update)
  except:
    pass


# help
def assist(update, context):
  username = update.message.chat.username
  print("Help :", username)
  keyboard = [
    [
      telegram.InlineKeyboardButton("GET HELP", url="t.me/ostrichdiscussion"),
    ],
  ]

  reply_markup = telegram.InlineKeyboardMarkup(keyboard)

  message = '''
Type @theZlib_bot book_name to search your favourite books.
<b>Ex:</b> @theZlib_bot ostrich

Use /book book_name to search your favourite books.
<b>Ex:</b> <code>/book ostrich</code>

/search - find isbn of book
    '''
  context.bot.send_message(chat_id=update.effective_chat.id,
                           text=message,
                           parse_mode='html',
                           reply_markup=reply_markup,
                           disable_web_page_preview=True)


def donate(update, context):
  keyboard = [
    [
      telegram.InlineKeyboardButton("Contribute",
                                    url="https://github.com/theostrich"),
      telegram.InlineKeyboardButton("Paypal Us",
                                    url="https://paypal.me/donateostrich"),
    ],
  ]

  reply_markup = telegram.InlineKeyboardMarkup(keyboard)
  update.message.reply_text(
    "Thank you for your wish to contribute. I hope you enjoyed using our services. Make a small donation/contribute to let this project alive.",
    reply_markup=reply_markup)


def aboutTheBot(update, context):
  """Log Errors caused by Updates."""

  keyboard = [
    [
      telegram.InlineKeyboardButton((emoji.emojize(":loop:")) + "Channel",
                                    url="t.me/theostrich"),
      telegram.InlineKeyboardButton("👥Support Group", callback_data='2'),
    ],
    [
      telegram.InlineKeyboardButton(
        "🔖Add Me In Group", url="https://t.me/thezlib_bot?startgroup=new")
    ],
  ]

  reply_markup = telegram.InlineKeyboardMarkup(keyboard)

  update.message.reply_text(
    "<b>Hello! I am Zlib, A book bot.</b>"
    "\n\n<b>About Me :</b>"
    "\n\n  - <b>Name</b>        : Zlib"
    "\n\n  - <b>Creator</b>      : @theostrich"
    "\n\n  - <b>Language</b>  : Python 3"
    "\n\n  - <b>Library</b>       : <a href=\"https://github.com/python-telegram-bot/python-telegram-bot/\">python-telegram-bot</a>"
    "\n\nNote : All books you get from this bot are extracted from <a href=\"https://libgen.rs/\">libgen</a>, all credits goes to original authors of the respective books."
    "\n\nIf you enjoy using me and want to help me survive, do donate with the /donate command - my creator will be very grateful! Doesn't have to be much - every little helps! Thanks for reading :)",
    parse_mode='html',
    reply_markup=reply_markup,
    disable_web_page_preview=True)


def search(update, context):

  print("book : ", update.message.chat.username)
  query_data = context.args
  data_ = ""
  for i in query_data:
    data_ += i
    data_ += " "
  if len(data_.strip()) == 0:
    valid = '''<b>
Enter a valid query 🔍 

Usage: <code>/search ostrich</code>
    </b>'''
    update.message.reply_text(reply_to_message_id=update.message.message_id,
                              text=valid,
                              parse_mode='html')
  else:
    #  try:
    # print(update.message.text)
    m = update.message.reply_text(
      reply_to_message_id=update.message.message_id,
      text="Processing...",
      parse_mode='html')
    url = f"https://annas-archive.org/search?q={data_}"
    req = requests.get(url).content
    soup = BeautifulSoup(req, 'lxml')
    soup.find_all("div", class_="truncate text-xl font-bold")
    redi = soup.find_all(
      'a',
      class_=
      "custom-a flex items-center relative left-[-10] px-[10] py-2 hover:bg-[#00000011]"
    )
    message = f"<b>Found <code>[{len(redi)}]</code> results:</b>\n"
    for i in range(len(redi)):
      redirect = redi[i]["href"]
      redirect_url = f"https://annas-archive.org{redirect}"
      req0 = requests.get(redirect_url).content
      soup0 = BeautifulSoup(req0, 'lxml')
      dataw = soup0.find(
        "div", class_="text-xs p-4 font-mono break-words bg-[#0000000d]").text
      data = json5.loads(dataw)
      if data["file_unified_data"]["sanitized_isbns"]:
        isbn = data["file_unified_data"]["sanitized_isbns"][0]
      else:
        isbn = data["md5"]
    #cover =  data["additional"]["top_box"]["cover_url"]
      title = data["additional"]["top_box"]["title"]
      mess = f'''
<b>{title}</b>: <code>{isbn}</code>
        '''
      if len(message) < 4096:
        message = message + mess
      else:
        break

  # author = data["additional"]["top_box"]["author"]
  #publisher = data["file_unified_data"]["publisher_best"]
  #language = data["file_unified_data"]["language_names"][0]
  #siz = size(data["file_unified_data"]["filesize_best"] )
  #isbn = data["file_unified_data"]["sanitized_isbns"][0]
  #year = data["file_unified_data"]["year_best"]
  #downlink =  data["additional"]["download_urls"][0][1]
  #message = f'''


#<b>{title}</b>

#<b>Author(s):</b> <code>{author}</code>
#<b>Language:</b> <code>{language}</code>
#<b>Year:</b> <code>{year}</code>
#<b>ISBN:</b> <code>{isbn}</code>
#<b>Publisher:</b> <code>{publisher}</code>
#<b>Size:</b> <code>{siz}</code>

#<b>By <a href=\"https://t.me/theZlib_bot\">Zlibrary</a> </b>
#'''
#keyboard = [
#          [
#               telegram.InlineKeyboardButton("Download Link",
#                                                url=downlink),
#              ],
#           ]
#reply_markup = telegram.InlineKeyboardMarkup(keyboard)
#m.delete()
# context.bot.send_photo(chat_id=update.message.chat_id,
#                                   photo=cover,
#                                  reply_markup=reply_markup,
#                                   caption=message,
#                                   parse_mode='html')

    m.delete()
    update.message.reply_text(reply_to_message_id=update.message.message_id,
                              text=f"{message}",
                              parse_mode='html')
  #except:
  #update.message.reply_text(reply_to_message_id=update.message.message_id,text="Book not found\nJoin @theostrich")


def book(update, context):

  print("book : ", update.message.chat.username)
  query_data = context.args
  data_ = ""
  for i in query_data:
    data_ += i
    data_ += " "
  if len(data_.strip()) == 0:
    valid = '''<b>
Enter a valid query 🔍 

Usage: <code>/book ostrich</code>
    </b>'''
    update.message.reply_text(reply_to_message_id=update.message.message_id,
                              text=valid,
                              parse_mode='html')
  else:
    try:
      m = update.message.reply_text(
        reply_to_message_id=update.message.message_id,
        text="Processing...",
        parse_mode='html')
      url = f"https://annas-archive.org/search?q={data_}"
      req = requests.get(url)
      if not req.url.split("/")[3] == "md5":
        soup = BeautifulSoup(req.content, 'lxml')
        soup.find_all("div", class_="truncate text-xl font-bold")
        redirect = soup.find_all(
          'a',
          class_=
          "custom-a flex items-center relative left-[-10] px-[10] py-2 hover:bg-[#00000011]"
        )[0]["href"]
        redirect_url = f"https://annas-archive.org{redirect}"
      else:
        redirect_url = req.url
      req0 = requests.get(redirect_url).content
      soup0 = BeautifulSoup(req0, 'lxml')
      dataw = soup0.find(
        "div", class_="text-xs p-4 font-mono break-words bg-[#0000000d]").text
      data = json5.loads(dataw)

      cover = data["additional"]["top_box"]["cover_url"]
      try:
        print(requests.head(cover))
      except:
        cover = "https://c4.wallpaperflare.com/wallpaper/504/398/329/historical-books-wallpaper-preview.jpg"
      title = data["additional"]["top_box"]["title"]
      author = data["additional"]["top_box"]["author"]
      publisher = data["file_unified_data"]["publisher_best"]
      try:
        language = data["additional"]["most_likely_language_name"]
      except:
        language = "English"
      siz = size(data["file_unified_data"]["filesize_best"])
      #pages = result[list(result.keys())[0]]["pages"]
      if data["file_unified_data"]["sanitized_isbns"]:
        isbn = ','.join(data["file_unified_data"]["sanitized_isbns"])
      else:
        isbn = "NA"
      #req = requests.get(url)
      year = data["file_unified_data"]["year_best"]
      downlink = data["additional"]["download_urls"][1][1]
      #print(downlink)

      # libgen = Libgen(result_limit='1')
      #result = libgen.search(data_)
      #cover =  result[list(result.keys())[0]]["coverurl"]
      #url = result[list(result.keys())[0]]["mirrors"]["main"]
      #title = result[list(result.keys())[0]]["title"]
      #author = result[list(result.keys())[0]]["author"]
      #language = result[list(result.keys())[0]]["language"]
      #pages = result[list(result.keys())[0]]["pages"]
      #isbn = result[list(result.keys())[0]]["identifier"]
      #req = requests.get(url)
      #soup = BeautifulSoup(req.text, "lxml")
      #downlink = soup.find("a",string="Cloudflare")["href"]
      message = f'''
<b>{title}</b>

<b>Author(s):</b> <code>{author}</code>
<b>Language:</b> <code>{language}</code>
<b>Year:</b> <code>{year}</code>
<b>ISBN:</b> <code>{isbn}</code>
<b>Publisher:</b> <code>{publisher}</code>
<b>Size:</b> <code>{siz}</code>

<b><a href=\"https://t.me/ArchiveOfBook\">Archive</a> | <a href=\"https://t.me/theZlib_bot\">Zlibrary</a></b>
'''
      print(cover)
      keyboard = [
        [
          telegram.InlineKeyboardButton("Download Link", url=downlink),
        ],
      ]
      reply_markup = telegram.InlineKeyboardMarkup(keyboard)
      m.delete()
      context.bot.send_photo(chat_id=update.message.chat_id,
                             photo=cover,
                             reply_markup=reply_markup,
                             caption=message,
                             parse_mode='html')
      context.bot.send_photo(chat_id=-1001879114748,
                             photo=cover,
                             reply_markup=reply_markup,
                             caption=message,
                             parse_mode='html')

      #url = f"http://libgen.rs/search.php?req=++{data_.strip()}+&open=0&res=25&view=simple&phrase=1&column=def"
      #headers = {
      #"User-Agent":
      #"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
      # "Chrome/83.0.4103.97 Safari/537.36"
      # }
      # r = requests.get(url=url, headers=headers)
      #print(r.text)
      # print(url)
      # try:
      #  if r.status_code == 200:
      #    query_html = r.text
      #    soup = BeautifulSoup(query_html, "lxml")
      # Book Page Link From Search Result
      #   download_page_with_tag = soup.find("table", attrs={"rules": "rows"})
      #   print(download_page_with_tag)
      #  link_start = str(download_page_with_tag).find('href="')
      #  link_end = str(download_page_with_tag).find(
      #      '"', link_start + 6)
      #  book_page_link = str(download_page_with_tag)[link_start +
      #       6:link_end]

      #     r = requests.get(url=book_page_link, headers=headers)
      #    if r.status_code == 200:
      #        book_page_html = r.text
      #        soup = BeautifulSoup(book_page_html, "lxml")
      # Direct Link
      #        download_link_with_tag = soup.find("div", id="download")
      #        link_start = str(download_link_with_tag).find('href="')
      #         link_end = str(download_link_with_tag).find(
      #             '"', link_start + 6)
      #          Direct_link = str(download_link_with_tag)[link_start +
      #                                                    6:link_end]
      # Book Name
      #          book_name = soup.find("h1").text
      # Book Cover
      #         book_cover_link = "http://library.lol/"
      #         book_cover_link_with_tag = soup.find(alt="cover")
      #         link_start = str(book_cover_link_with_tag).find('src="')
      #        link_end = str(book_cover_link_with_tag).find(
      #              '"', link_start + 6)
      #          book_cover_link += str(
      #              book_cover_link_with_tag)[link_start + 6:link_end]
      # Book Detail
      #         Book_Detail = ""
      #          book_cover_link_with_tag = soup.find_all("p")
      #         for i in book_cover_link_with_tag[:-1]:
      #             x = str(i.text).split(",")
      #              for j in x:
      #                  if "Amazon.com" in j:
      #                      pass
      # 3                  else:
      #                     Book_Detail += j.strip()
      #                      Book_Detail += '''


#'''
#          # Download Book Cover
#          open("Book Cover.png",
#              "wb").write(requests.get(book_cover_link).content)
#          # Adding Watermark to Book Cover
#          photo = Image.open("./Book Cover.png")
# make the image editable
#          width, height = photo.size
#           draw = ImageDraw.Draw(photo)
#           text = "@theZlib_bot"
#           font = ImageFont.truetype(
#               '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
#               20)
#           textwidth, textheight = draw.textsize(text, font)
#           # calculate the x,y coordinates of the text
#           margin = 5
#           x = width - textwidth - margin
#           y = height - textheight - margin
# draw watermark in the bottom right corner
#           draw.text((x, y), text, font=font)
#            photo.save("./Book Cover.png")
#           # making message
#           message = f'''
#📖 <b>{book_name}</b>
#<b>{Book_Detail.replace("<", "").replace(">", "").replace("/", "")}</b>
#<b>Archived on<a href=\"https://t.me/ArchiveOfBook\"> Archive Of Books</a> 📚️ </b>
#<b>By <a href=\"https://t.me/theZlib_bot\">Zlibrary</a> </b>
#'''
#                   # making button
# keyboard = [
#     [
#        telegram.InlineKeyboardButton("Download Link",
#                                       url=Direct_link),
#     ],
# ]
# reply_markup = telegram.InlineKeyboardMarkup(keyboard)
# sending to user
# context.bot.send_photo(chat_id=update.message.chat_id,
#                        photo=,
#                        reply_markup=reply_markup,
#                        caption=message,
#                        parse_mode='html')
# sending to log channel
# context.bot.send_photo(chat_id="-1001177555443",
#                        photo=open('./Book Cover.png',
#  3                                   'rb'),
#                        reply_markup=reply_markup,
#                        caption=message,
#                        parse_mode='html')
# context.bot.send_photo(chat_id=Channel_id, photo=open('./Book Cover.png', 'rb'),
#                        reply_markup=reply_markup, caption=message, parse_mode='html')

# making button

# if any error occur
#     except:

#     valid = '''<b>404 : 📖 Book not found in my database</b>'''
#update.message.reply_text(
#reply_to_message_id=update.message.message_id,
#       text=valid,
#    parse_mode='html')

    except Exception as e:
      print(e)
      update.message.reply_text(reply_to_message_id=update.message.message_id,
                                text="Book not found")


def boook(link):
  headers = {
    "User-Agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/83.0.4103.97 Safari/537.36"
  }

  r = requests.get(url=link, headers=headers)
  if r.status_code == 200:
    book_page_html = r.text
    soup = BeautifulSoup(book_page_html, "lxml")
    # Direct Link
    download_link_with_tag = soup.find("div", id="download")
    link_start = str(download_link_with_tag).find('href="')
    link_end = str(download_link_with_tag).find('"', link_start + 6)
    Direct_link = str(download_link_with_tag)[link_start + 6:link_end]
    # Book Name
    book_name = soup.find("h1").text
    message = f'''
📖 <b>{book_name}</b>
<b> Download Link ~ <a href=\"{Direct_link}\">Direct Link</a></b>
'''

    return message


def inlinequery(update: Update, context: CallbackContext) -> None:
  query = update.inline_query.query
  print(query)
  if len(query) > 2:
    print("Query : ", query)
    libg = Libgen(result_limit='1')
    result = libg.search(query)
    print(len(result))
    results = []
    lent = 3
    if len(result) < lent:
      lent = len(result)
    if len(result) == 0:
      results.append(
        InlineQueryResultArticle(
          id=1,
          title="No results found",
          input_message_content=InputTextMessageContent("Join @theostrich")))
#                        input_message_content=InputTextMessageContent(
#                            boook(book_page_link[i]),
#                            parse_mode=ParseMode.HTML,
#                        ),
#                        reply_markup=reply_markup),)

    for i in range(lent):

      url = result[list(result.keys())[i]]["mirrors"]["main"]
      title = result[list(result.keys())[i]]["title"]
      author = result[list(result.keys())[i]]["author"]
      language = result[list(result.keys())[i]]["language"]
      pages = result[list(result.keys())[i]]["pages"]
      isbn = result[list(result.keys())[i]]["identifier"]
      req = requests.get(url)
      soup = BeautifulSoup(req.text, "lxml")
      downlink = soup.find("a", string="Cloudflare")["href"]
      message = f'''
<b>{title}</b>

<b>Author(s):</b> {author}
<b>Language:</b> {language}
<b>Pages:</b> {pages}
<b>ISBN:</b> {isbn}

<b>By <a href=\"https://t.me/theZlib_bot\">Zlibrary</a> </b>'''

      keyboard = [
        [
          telegram.InlineKeyboardButton("Download Link", url=downlink),
        ],
      ]
      #print(i)
      results.append(
        InlineQueryResultArticle(
          id=i + 1,
          title=result[list(result.keys())[i]]["title"],
          thumb_url=result[list(result.keys())[i]]["coverurl"],
          input_message_content=InputTextMessageContent(
            message,
            parse_mode=ParseMode.HTML,
          ),
          reply_markup=telegram.InlineKeyboardMarkup(
            keyboard)  #reply_markup=reply_markup),
        ))
    update.inline_query.answer(results)

    #url = f"http://libgen.rs/search.php?req=++{query}+&open=0&res=25&view=simple&phrase=1&column=def"
    #headers = {
    #    "User-Agent":
    #    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
  #     "Chrome/83.0.4103.97 Safari/537.36"
  # }
  #r = requests.get(url=url, headers=headers)
  # try:
  #if r.status_code == 200:
  #    query_html = r.text
  #    soup = BeautifulSoup(query_html, "lxml")
  # Book Page Link From Search Result
  #   book_page_link = []
  #   bookz_name = []
  #   download_page_with_tag = soup.find_all("a", title='Gen.lib.rus.ec')
  #  download_name = soup.find_all("td", width="500")

  #  if len(download_name) <= 3:
  #      for i in range(0, len(download_name)):
  #          book_page_link.append(download_page_with_tag[i]['href'])#
  #            bookz_name.append(download_name[i].text)
  #  else:
  #    for i in range(0, 3):
  #         book_page_link.append(download_page_with_tag[i]['href'])
  #       bookz_name.append(download_name[i].text)

  #   print(bookz_name)
  #   print(book_page_link)

  #  keyboard = [
  #      [
  #          telegram.InlineKeyboardButton(
  #            "Join Ostrich", url="https://t.me/theostrich"),
  #     ],
  # ]
  # reply_markup = telegram.InlineKeyboardMarkup(keyboard)


# What about this?
#
#i= 0
#results = []
#while i < len(bookz_name):
#    article = InlineQueryResultArticle(
#                        id=i+1,
#                        title=bookz_name[i],
#                        input_message_content=InputTextMessageContent(
#                            boook(book_page_link[i]),
#                            parse_mode=ParseMode.HTML,
#                        ),
#                        reply_markup=reply_markup),
#               ]
#    results.append(article)
#    i += 1
#
# Any max. len limitation for results?

# if len(bookz_name) == 1:
#     results = [
#        InlineQueryResultArticle(
#            id='1',
#             title=bookz_name[0],
#             input_message_content=InputTextMessageContent(
#                 boook(book_page_link[0]),
#                 parse_mode=ParseMode.HTML,
#              ),
#             reply_markup=reply_markup),
#       ]
#   elif len(bookz_name) == 2:
#       results = [
#          InlineQueryResultArticle(
#              id='1',
#               title=bookz_name[0],
#               input_message_content=InputTextMessageContent(
#                   boook(book_page_link[0]),
#                  parse_mode=ParseMode.HTML,
#               ),
#              reply_markup=reply_markup),
#          InlineQueryResultArticle(
#              id='2',
#             title=bookz_name[1],
#             input_message_content=InputTextMessageContent(
#                  boook(book_page_link[1]),
#                   parse_mode=ParseMode.HTML,
#               ),
#               reply_markup=reply_markup),
#       ]
#   elif len(bookz_name) == 3:
#      results = [
#           InlineQueryResultArticle(
#               id='1',
#               title=bookz_name[0],
#               input_message_content=InputTextMessageContent(
#                   boook(book_page_link[0]),
#                   parse_mode=ParseMode.HTML,
#               ),
#               reply_markup=reply_markup),
#           InlineQueryResultArticle(
#                id='2',
#                title=bookz_name[1],
#                input_message_content=InputTextMessageContent(
#                    boook(book_page_link[1]),
#                    parse_mode=ParseMode.HTML,
#                 ),
#                 reply_markup=reply_markup),
#             InlineQueryResultArticle(
#                 id='3',
#                 title=bookz_name[2],
##                 input_message_content=InputTextMessageContent(
#                     boook(book_page_link[2]),
#                    parse_mode=ParseMode.HTML,
#                 ),
#                  reply_markup=reply_markup),
#         ]

# update.inline_query.answer(results)


def eos(update: Update, context: CallbackContext) -> None:
  text = '''<b>Join @theostrich to access this bot</b>'''
  keyboard = [[
    telegram.InlineKeyboardButton("JOIN OSTRICH",
                                  url="https://telegram.dog/theostrich/")
  ]]

  reply_markup = telegram.InlineKeyboardMarkup(keyboard)
  update.message.reply_photo(photo = open("/home/runner/ZLIB/minion.jpg", 'rb' ) ,caption=text, reply_markup=reply_markup, parse_mode='html')


def bos(update: Update, context: CallbackContext) -> None:
  try:
    print(update.message.text)
    m = update.message.reply_text(
      reply_to_message_id=update.message.message_id,
      text="Processing...",
      parse_mode='html')
    url = f"https://annas-archive.org/search?q={update.message.text}"
    req = requests.get(url)
    if not req.url.split("/")[3] == "md5":
      soup = BeautifulSoup(req.content, 'lxml')
      soup.find_all("div", class_="truncate text-xl font-bold")
      redirect = soup.find_all(
        'a',
        class_=
        "custom-a flex items-center relative left-[-10] px-[10] py-2 hover:bg-[#00000011]"
      )[0]["href"]
      redirect_url = f"https://annas-archive.org{redirect}"
    else:
      redirect_url = req.url

    req0 = requests.get(redirect_url).content
    soup0 = BeautifulSoup(req0, 'lxml')
    dataw = soup0.find(
      "div", class_="text-xs p-4 font-mono break-words bg-[#0000000d]").text
    data = json5.loads(dataw)
    cover = data["additional"]["top_box"]["cover_url"]
    try:
      print(requests.head(cover))
    except:
      cover = "https://c4.wallpaperflare.com/wallpaper/504/398/329/historical-books-wallpaper-preview.jpg"
    title = data["additional"]["top_box"]["title"]
    author = data["additional"]["top_box"]["author"]
    publisher = data["file_unified_data"]["publisher_best"]
    try:
      language = data["additional"]["most_likely_language_name"]
    except:
      language = "English"
    siz = size(data["file_unified_data"]["filesize_best"])
    if data["file_unified_data"]["sanitized_isbns"]:
      isbn = ','.join(data["file_unified_data"]["sanitized_isbns"])
    else:
      isbn = "NA"
    year = data["file_unified_data"]["year_best"]
    print(data["additional"]["download_urls"])
    downlink = data["additional"]["download_urls"][1][1]

    message = f'''
<b>{title}</b>

<b>Author(s):</b> <code>{author}</code>
<b>Language:</b> <code>{language}</code>
<b>Year:</b> <code>{year}</code>
<b>ISBN:</b> <code>{isbn}</code>
<b>Publisher:</b> <code>{publisher}</code>
<b>Size:</b> <code>{siz}</code>

<b><a href=\"https://t.me/ArchiveOfBook\">Archive</a> | <a href=\"https://t.me/theZlib_bot\">Zlibrary</a></b>
'''
    keyboard = [
      [
        telegram.InlineKeyboardButton("Download Link", url=downlink),
      ],
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    m.delete()
    context.bot.send_photo(chat_id=update.message.chat_id,
                           photo=cover,
                           reply_markup=reply_markup,
                           caption=message,
                           parse_mode='html')
    context.bot.send_photo(chat_id=-1001879114748,
                           photo=cover,
                           reply_markup=reply_markup,
                           caption=message,
                           parse_mode='html')

  except:
    update.message.reply_text(reply_to_message_id=update.message.message_id,
                              text="Book not found\nJoin @theostrich")


updater = Updater(token=os.environ['TOKEN'], use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(InlineQueryHandler(inlinequery))
dispatcher.add_handler(MessageHandler(filter_awesome, eos))

book_handler = CommandHandler('book', book,filters=filter_awesomes)
dispatcher.add_handler(book_handler)
book_handler = CommandHandler(['search','find'], search,filters=filter_awesomes)
dispatcher.add_handler(book_handler)

help_handler = CommandHandler('help', assist,filters=filter_awesomes)
dispatcher.add_handler(help_handler)
start_handler = CommandHandler('start', start,filters=filter_awesomes)
dispatcher.add_handler(start_handler)
broadcast_handeler = CommandHandler('broadcast', broadcast.broadcast,run_async=True)
dispatcher.add_handler(broadcast_handeler)

donate_handler = CommandHandler('donate', donate,filters=filter_awesomes)
dispatcher.add_handler(donate_handler)
about_handler = CommandHandler('about', aboutTheBot,filters=filter_awesomes)
dispatcher.add_handler(about_handler)
dispatcher.add_handler(MessageHandler(filter_awesomes, bos))
keep_alive()
updater.start_polling()
