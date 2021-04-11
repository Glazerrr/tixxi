import telebot


bot = telebot.TeleBot('1619376053:AAG3Zhdw5m3oc98WttZTjm2MLkJMNsPa2zM')
keyboard1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard1.row('Рассчитать заказ 💰', 'Корзина 🛒')
keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard2.row('Назад')
cartkeyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
resetbutton = telebot.types.InlineKeyboardButton('Сброс', callback_data='reset')
cartbutton = telebot.types.InlineKeyboardButton('В корзину', callback_data='addcart')
cartkeyboard.add(resetbutton, cartbutton)
bot.remove_webhook()
zeroprice = 0.0
totalprice = 0.0
calcprice = 0.0
count = 0
width = 0.0
length = 0.0
lengthdict = []
widthdict = []
totalpricedict = []
user_id = 0
users_orders = {}


@bot.callback_query_handler(func=lambda call: True)
def step2(call):
    if call.data == 'reset':
        bot.send_message(call.message.chat.id, 'Сделано', reply_markup = keyboard2)
    elif call.data == 'addcart':
        global totalprice
        totalprice = calcprice
        global count
        count = count + 1
        global length
        global lengthdict
        global widthdict
        global width
        global totalpricedict
        lengthdict.append(length)
        widthdict.append(width)
        totalpricedict.append(calcprice)
        bot.send_message(call.message.chat.id, 'Добавлено в корзину', reply_markup = keyboard2)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id,
                     f'Здравствуйте, Я бот Tixxi. Приятно познакомиться, {message.from_user.first_name}' '. Список моих возможностей /help',
                     reply_markup=keyboard1)


@bot.message_handler(content_types=['text', 'photo'])
def get_text_messages(message):
    global user_id
    user_id = message.from_user.id
    if message.text == 'Рассчитать заказ 💰':
        bot.send_message(message.from_user.id,
                         'Хорошо, я помогу Вам рассчитать заказ, для этого мне необходимо знать параметры '
                         'нашивки.', reply_markup=keyboard2)
        bot.send_message(message.from_user.id, 'Начнем. Отправьте, пожалуйста, длину нашивки в миллиметрах')
        bot.register_next_step_handler(message, get_length)
    if message.text == 'Корзина 🛒':
        global totalprice
        global zeroprice
        global width
        global count
        zeroprice = zeroprice + totalprice
        if count > 0:
            for i in range(count):
                bot.send_message(message.from_user.id, f'Товар {i+1} с размерами {lengthdict[i]} на {widthdict[i]} стоимость {totalpricedict[i]}')
        bot.send_message(message.from_user.id, f'Стоимость вашей покупки: {zeroprice} рублей')
    if message.text == 'Назад':
        bot.register_next_step_handler(message, get_text_messages)
        bot.send_message(message.from_user.id, 'Выберите интересующее вас меню', reply_markup=keyboard1)
    if message.text == "Завершить":
        hide_keyboard = telebot.types.ReplyKeyboardRemove()
        global users_orders
        users_orders = {user_id: {length: 123, width: 123}}
        bot.send_message(message.chat.id, 'Ваш запрос принят',
                         reply_markup=hide_keyboard)
        msg = " От клиента {} поступил заказ:\n{}.\nИ вопрос:\n" \
              "{}".format(message.chat.id, users_orders[message.chat.id][length],
                          users_orders[message.chat.id][width])
        bot.send_message(731806971, msg)
    if message.content_type == 'photo':
        raw = message.photo[2].file_id
        name = raw + ".jpg"
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(name, 'wb') as new_file:
            new_file.write(downloaded_file)
        img = open(name, 'rb')
        bot.send_message(731806971,
                         "Запрос от\n*{name} {last}*".format(name=message.chat.first_name, last=message.chat.last_name),
                         parse_mode="Markdown")  # от кого идет сообщение и его содержание
        bot.send_photo(731806971, img)
        bot.send_message(message.chat.id, "*{name}!*\n\nСпасибо за инфу".format(name=message.chat.first_name,
                                                                                last=message.chat.last_name,
                                                                                text=message.text),
                         parse_mode="Markdown")


def get_length(message):
    if message.text == 'Назад':
        bot.send_message(message.from_user.id, 'Выберите интересующее вас меню', reply_markup=keyboard1)
        return
    global length
    length = message.text
    if is_number(length):
        length = float(length)
        bot.send_message(message.from_user.id,
                         'Хорошо, далее отправьте, пожалуйста, ширину Вашей нашивки в миллиметрах')
        bot.register_next_step_handler(message, price)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста введите число без букв и пробелов')
        bot.register_next_step_handler(message, get_length)


def price(message):
    if message.text == 'Назад':
        bot.send_message(message.from_user.id, 'Выберите интересующее вас меню', reply_markup=keyboard1)
        return
    global width
    width = message.text
    if is_number(width):
        width = float(width)
        global totalprice
        global calcprice
        calcprice = width * length
        bot.send_message(message.from_user.id, f'Стоимость вашего заказа {toFixed(calcprice, 2)} рублей', reply_markup=cartkeyboard)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста введите число без букв и пробелов')
        bot.register_next_step_handler(message, price)
    if message.text == 'Назад':
        bot.register_next_step_handler(message, get_text_messages)
        bot.send_message(message.from_user.id, 'Выберите интересующее вас меню', reply_markup=keyboard1)
        return


def is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"


if __name__ == '__main__':
    bot.polling(none_stop=True)
