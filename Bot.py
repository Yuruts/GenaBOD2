# Author Doronin Ivan
# this bot add one picture to another

import telebot
from telebot import apihelper
import requests
import cv2 as cv

API_TOKEN = "626559877:AAE4NGLK1X_9pb_tFFjyW6M7OPO1pqBcVOQ"
apihelper.proxy = {'http': 'http://10.10.1.10:3128'}


bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start', 'help', 'back', 'man'])
def get_commands(message):
    if message.text in ["/help","/start"]:
        bot.send_message(message.from_user.id, "Пришли фото фона")


def Vpaste(background, obj, msk="white", plc="l_d", part=0.3):
    s = min(obj.shape[0] / background.shape[0], obj.shape[1] / background.shape[1])
    ob = cv.resize(obj, None, fx=part / s, fy=part / s, interpolation=cv.INTER_AREA)
    gray = cv.cvtColor(ob, cv.COLOR_BGR2GRAY)
    if msk == "white":
        ret, mask = cv.threshold(gray, gray.max() - 25, gray.max(), cv.THRESH_BINARY)
        mask = cv.bitwise_not(mask)
    else:
        ret, mask = cv.threshold(gray, gray.min(), gray.max(), cv.THRESH_BINARY)
    mask_inv = cv.bitwise_not(mask)
    n, m, l = ob.shape
    # corner selection
    corner = plc.split("_")
    a, b, c, d = 0, n, 0, m
    if corner[0] == "r":
        c, d = -m - 1, -1
    if corner[1] == "d":
        a, b = -n - 1, -1
    roi = background[a:b, c:d]
    m1 = cv.bitwise_and(roi, roi, mask=mask_inv)
    m2 = cv.bitwise_and(ob, ob, mask=mask)
    dst = cv.add(m1, m2)
    background[a:b, c:d] = dst
    return background




@bot.message_handler(content_types=['photo'])
def get_back(message):
    obj = cv.imread("Andrew.png")
    print(message)
    file_id = message.photo[1].file_id
    file_info = bot.get_file(file_id)
    URL = 'https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path)
    print(URL)
    fi = requests.get(URL, allow_redirects=True)
    open("tmp1.jpg", 'wb').write(fi.content)
    background = cv.imread("tmp1.jpg")
    t = Vpaste(background, obj, msk="white", plc="l_d", part=0.45)
    cv.imwrite("out.jpg", t)
    out = open("out.jpg", 'rb')
    bot.send_message(message.from_user.id, "lol")
    bot.send_photo(message.from_user.id, out)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text in ["Привет", "Здаров", "привет", "здаров"]:
        bot.send_message(message.from_user.id, "Здаров, чувак, как сам?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Чё, сам не догадаешься??? Фотку пришли, хули делать")
    elif message.text in ["Норм", "Хорошо", "Неплохо", "Охуенно"]:
        bot.send_message(message.from_user.id, "Ну и молодец, у меня тоже всё супер")
    else:
        bot.send_message(message.from_user.id, "Какой-то бред. Напиши /help.")


bot.polling(none_stop=True, interval=0)
