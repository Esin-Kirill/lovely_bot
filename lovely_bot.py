import re
import requests
from random import choice, randint
from telebot import TeleBot, types
import time
import schedule
import threading
from configs import *


# GLOBALS 
TO_SEND = {}
URL_WEATHER = 'https://www.gismeteo.ru'
URL_MUSIC = 'https://music.yandex.ru/genres'

# INIT 
bot = TeleBot(TOKEN)

# INLINE KEYBORD\BUTTONS
inlineKB = types.InlineKeyboardMarkup
inlineBTN = types.InlineKeyboardButton

# REPLY KEYBORD\BUTTONS
replyKB = types.ReplyKeyboardMarkup
replyBTN = types.KeyboardButton
replyKBRMV = types.ReplyKeyboardRemove

# FUNCS
def job():
    bot.send_message(ADMIN_CHAT_ID, 'Привет!')

def send_to_ADMIN(bot, msg):
    text = f'Сообщение от любимки:\n{msg.text}'
    bot.send_message(ADMIN_CHAT_ID, text)
    bot.send_message(msg.chat.id, """Передал твою просьбу :) Продолжим?""")

        
# Generates morning message from lists of random texts\smiles\names
def generate_morning_msg():
    text = choice(MORNING_MSGS)
    name = choice(MORNING_NAMES)
    smile = choice(MORNING_SMLS)
    msg = f"{text}, {name} {smile}"
    return msg

# Generates random photo for quote -> returns picture
def generate_quote_picture(text):
    global PIXABY_TOKEN

    try:
        text = [re.sub(r'[^а-яё]', ' ', word, flags=re.IGNORECASE) for word in text.split(' ')]
        text = [word.strip() for word in text]
        q = '+'.join(sorted(text, reverse=True)[:2])
        url = f'https://pixabay.com/api/?key={PIXABY_TOKEN}&q={q}&lang=ru'
        result = requests.get(url, headers=USER_AGENT).json()

        hits = result['hits']
        ind = randint(0, len(hits)-1)
        link = hits[ind]['webformatURL']
    except:
        categories = ['backgrounds', 'fashion', 'nature', 'science', 'education', 'feelings',
                    'health', 'people', 'places', 'animals', 'food', 'sports', 'travel', 'buildings', 'music']
        category = choice(categories)
        url = f'https://pixabay.com/api/?key={PIXABY_TOKEN}&category={category}'
        result = requests.get(url, headers=USER_AGENT).json()

        hits = result['hits']
        ind = randint(0, len(hits)-1)
        link = hits[ind]['webformatURL']

    return link

# Generates random quote -> returns quote
def generate_quote():
    # Quote
    params = {'method':'getQuote', 'lang':'ru', 'format':'json'}
    url = 'http://api.forismatic.com/api/1.0/'

    result = requests.get(url, params=params).json()
    quote = result['quoteText']
    author = result['quoteAuthor'] if result['quoteAuthor'] != '' else 'Неизвестный автор'
    
    # Quote picture
    quote_picture1 = requests.get('https://aws.random.cat/meow', headers=USER_AGENT).json()['file'] 
    quote_picture2 = requests.get('https://random.dog/woof.json', headers=USER_AGENT).json()['url'] 
    quote_picture = choice([quote_picture1, quote_picture2])
    quote = f'<b>{quote}</b>\n\n<i>\U000000A9 {author}</i>'
    
    return quote, quote_picture

# Generates random answer (yes, no, maybe) and relevant gif
def generate_yesno():
    options = {
                'yes': ['Пожалуй, да', 'Да, да и ещё раз да!', 'Может как-нибудь в другой раз? (Нет)',
                        'Естессна, а были другие варианты?', 'А почему бы и... Да!)',
                        'Конечно же - да!', 'Однозначно.', 'Просто да и не спрашивай почему...'],
                'no': ['Да не... Кому оно надо :)', 'А почему бы и нет',
                        'Нет', 'Конечно же... нет!', 'Ах и увы, но нет, прости...',
                        'Может в другой раз?)', 'Однозначно - нет.', 'Не стоит...'],
                'maybe': ['Ну, возможно...', 'Хз-хз-хз...', 'Быть или не быть? Хз :)', 'Увы, не могу ничем помочь.',
                          'Сам не знаю :(']
            }
    url = 'https://yesno.wtf/api'
    result = requests.get(url, headers=USER_AGENT).json()
    answer = result['answer']
    answer = choice(options[answer])
    url_gif = result['image']

    return answer, url_gif

# Translates text from en to ru -> returns transalted text
def translate_en_ru(text):
    text_new = text.encode('utf-8')
    url = "https://google-translate1.p.rapidapi.com/language/translate/v2"
    payload = f"source=en&target=ru&q={text_new}"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "application/gzip",
        "X-RapidAPI-Host": "google-translate1.p.rapidapi.com",
        "X-RapidAPI-Key": "16d81c9d27msh9268823dda8e89bp15d511jsn154bc248ca9e"
    }
    result = requests.request("POST", url, data=payload, headers=headers).json()
    transl = result['data']['translations'][0]['translatedText']
    return transl

# Checks text answer from main keybord
def check_answer(message):
    messages = ['погода', 'музыка', 'цитата', 'факты', 'english', 'другое', 'да\нет', 'поиск']
    if message.text.lower() in messages:
        return True
    else:
        return False

# Bot make a google search
def make_a_search(message):
    url = f'https://www.google.com/search?q={message.text}'
    msg = f'<a href="{url}">Результаты 👩‍💻</a>'
    bot.send_message(message.chat.id, msg, parse_mode='HTML')

# Morning message 
def bot_send_morning_msg(chat_id):
    msg = generate_morning_msg()
    bot.send_message(chat_id, msg)


# BOT methods
@bot.message_handler(func=lambda message: message.from_user.username not in USERS)
def some(message):
    # Msg for unknown user
    msg = "Permission denied \U0001F6A8"
    bot.send_message(message.chat.id, msg)

    # Msg for ADMIN
    msg = f"Какой-то {message.from_user.username} нашёл бота и пытался подключиться."
    bot.send_message(ADMIN_CHAT_ID, msg)


@bot.message_handler(commands=['help'])
def bot_send_help(message):
    kb = replyKB(row_width=2, resize_keyboard=True)
    btn1 = replyBTN('Погода')
    btn2 = replyBTN('Музыка')
    btn3 = replyBTN('Цитата')
    btn4 = replyBTN('Да\Нет')
    btn5 = replyBTN('Поиск')
    btn6 = replyBTN('Другое')
    kb.add(btn1, btn2, btn3, btn4, btn5, btn6)

    bot.send_message(message.chat.id, MSG_HELP, reply_markup=kb, parse_mode='HTML')

@bot.message_handler(commands=['start'])
def bot_start(message):
    global TO_SEND

    if message.chat.id not in TO_SEND and TO_SEND.get(message.chat.id) != True:
        TO_SEND[message.chat.id] = True
        schedule.every().day.at("04:00").do(bot_send_morning_msg, message.chat.id)
    
    kb = replyKB(row_width=2, resize_keyboard=True)
    btn1 = replyBTN('Погода')
    btn2 = replyBTN('Музыка')
    btn3 = replyBTN('Цитата')
    btn4 = replyBTN('Да\Нет')
    btn5 = replyBTN('Поиск')
    btn6 = replyBTN('Другое')
    kb.add(btn1, btn2, btn3, btn4, btn5, btn6)

    bot.send_message(message.chat.id, MSG_WELCOME, reply_markup=kb, parse_mode='HTML')

# Text calllback handler (from replay keyboard)
@bot.message_handler(func=lambda x: check_answer(x))
def bot_process_callback(message):
    message_text = message.text.lower()
    chat_id = message.chat.id

    if message_text == 'погода':
        msg = f"""Пожалуйста, погода на <a href="{URL_WEATHER}">сегодня</a>"""
        bot.send_message(chat_id, msg, parse_mode='HTML')
    
    if message_text == 'музыка':
        msg = f"""Выбирай музыку под своё <a href="{URL_MUSIC}">настроение</a>"""
        bot.send_message(chat_id, msg, parse_mode='HTML')

    if message_text == 'цитата':
        quote_text, quote_picture = generate_quote()
        bot.send_photo(chat_id, photo=quote_picture, caption=quote_text, parse_mode='HTML')

    if message_text == 'да\нет':
        bot_yesno(message)

    if message_text == 'факты':
        msg = 'Извините, этот раздел ещё дорабатывается.'
        bot.send_message(chat_id, msg)

    if message_text == 'поиск':
        answer = bot.send_message(chat_id, 'Что будем искать \U0001F440')
        bot.register_next_step_handler(answer, make_a_search)
        # bot_teach_english(message)

    if message_text == 'другое':
        msg = """Если хочешь, чтобы я что-нибудь сюда добавил, просто напиши это текстом, и я перешлю твою просьбу :)"""
        answer = bot.send_message(chat_id, msg)
        bot.register_next_step_handler(answer, send_to_ADMIN)


# Calllback handler
@bot.callback_query_handler(func=lambda x: x.data)
def bot_process_callback(call):
    if call.data == 'weather':
        msg = f"""Оп... Погодка на <a href="{URL_WEATHER}">сегодня</a>"""
        bot.send_message(call.message.chat.id, msg, parse_mode='HTML')
    
    if call.data == 'music':
        msg = f"""Ммм... и какое же сегодня у тебя <a href="{URL_MUSIC}">настроение</a>?"""
        bot.send_message(call.message.chat.id, msg, parse_mode='HTML')

    if call.data == 'quote':
        quote_text, quote_picture = generate_quote()
        bot.send_photo(call.message.chat.id, photo=quote_picture, caption=quote_text, parse_mode='HTML')

    if call.data == 'exit':
        msg = """Окау... Чем тогда займёмся? \U0001F60F\n(пришли команду или напиши какое-нибудь сообщение)"""
        bot.send_message(call.message.chat.id, msg)


@bot.message_handler(commands=['yesno'])
def bot_yesno(message):
    text1 = 'Подожди секунду, я помогу тебе определиться \U000023F3'
    text2 = 'Подожди секунду, я помогу тебе определиться \U0000231B'
    message = bot.send_message(message.chat.id, text1)

    for _ in range(2):
        time.sleep(0.3)
        bot.edit_message_text(text2, message.chat.id, message.id)
        time.sleep(0.3)
        bot.edit_message_text(text1, message.chat.id, message.id)
    
    answer, gif_link = generate_yesno()
    bot.send_animation(message.chat.id, gif_link, caption=answer)


@bot.message_handler(content_types=['text'])
def bot_reply_text(message):
    msg = "Прости, но я пока что не понимаю человеческий язык... Может, в будущем, но пока что - нет :("
    bot.send_message(message.chat.id, msg)


if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()

    while True:
        schedule.run_pending()
        time.sleep(1)
