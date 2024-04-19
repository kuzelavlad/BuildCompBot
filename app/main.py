import telebot
import requests
# from django.core.mail import send_mail
from dotenv import load_dotenv
import os
import re
from key_board.bot_keyboard import *

# Загрузка переменных из файла .env
load_dotenv()

# Получение токена из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")

# Создание объекта бота
bot = telebot.TeleBot(TOKEN)

# Отдельный апи адрес для заявки
API_URL = os.getenv("API_URL")

BASE_URL = os.getenv("BASE_URL")

SELECTING_ACTION, SELECTING_TERM, VIEWING_PAYMENT_TERMS = range(3)

NAME, NUMBER, MESSAGE = range(3)

APPLICATION_KEY = 'application'

last_messages = {}
current_page = 1


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    markup_kb = start()
    sent_message = bot.send_message(message.chat.id,
                                    f'Добро пожаловать!\nНаша компания Aroma Stroy – гуру строительного бизнеса.Более '
                                    f'20 лет на рынке мы дарим тепло и уют нашим клиентам.Строительство домов под '
                                    f'ключ по всей Беларуси:\n•Собственное производство\n•Весь цикл от проекта до '
                                    f'заселения только с одной компанией\n•Прозрачное ценообразование\n•Подарок '
                                    f'каждому клиенту\nМы сохраним ваше время и нервы, гарантируя качественный '
                                    f'результат. ',
                                    reply_markup=markup_kb)

    last_messages[message.chat.id] = sent_message.message_id

    # Теперь можно безопасно удалить старое сообщение
    bot.delete_message(message.chat.id, message.id)


# Обработчик для кнопки "Каталог"
@bot.callback_query_handler(func=lambda call: call.data == 'catalog')
def handle_catalog_callback(call):
    get_houses(call.message, current_page)


# Обработчик для кнопки "Назад"
@bot.callback_query_handler(func=lambda call: call.data == 'return_to_main_menu')
def handle_return_to_main_menu_callback(call):
    handle_start(call.message)


# Обработчик для кнопки "Назад в Меню Условий Оплаты"
@bot.callback_query_handler(func=lambda call: call.data == 'return_to_terms_menu')
def handle_return_to_main_menu_callback(call):
    get_terms_of_payments(call.message)


# Обработчик для кнопки "Назад в Меню Стоимости"
@bot.callback_query_handler(func=lambda call: call.data == 'return_to_price_menu')
def handle_return_to_main_menu_callback(call):
    get_price(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'services')
def handle_services_callback(call):
    get_services(call.message)


# Обработчик для кнопки "Контакты"
@bot.callback_query_handler(func=lambda call: call.data == 'contacts')
def handle_contacts_callback(call):
    get_contacts_and_address(call.message)


# Обработчик для кнопки "Акции"
@bot.callback_query_handler(func=lambda call: call.data == 'discounts')
def handle_contacts_callback(call):
    get_discount(call.message)


# Обработчик для кнопки "Условия Оплаты"
@bot.callback_query_handler(func=lambda call: call.data == 'payments')
def handle_contacts_callback(call):
    get_terms_of_payments(call.message)


# Обработчик для кнопки "Рассрочка"
@bot.callback_query_handler(func=lambda call: call.data == 'installment_plan')
def handle_contacts_callback(call):
    get_installment_plan(call.message)


# Обработчик для кнопки "240 Указ"
@bot.callback_query_handler(func=lambda call: call.data == 'decree')
def handle_contacts_callback(call):
    get_decree(call.message)


# Обработчик для кнопки "Кредит"
@bot.callback_query_handler(func=lambda call: call.data == 'credit')
def handle_contacts_callback(call):
    get_credit(call.message)


# Обработчик для кнопки "Стоимость"
@bot.callback_query_handler(func=lambda call: call.data == 'price')
def handle_contacts_callback(call):
    get_price(call.message)


# Обработчик для кнопки "Домокомплект"
@bot.callback_query_handler(func=lambda call: call.data == 'tree_house')
def handle_contacts_callback(call):
    get_tree_house(call.message)


# Обработчик для кнопки "Под ключ"
@bot.callback_query_handler(func=lambda call: call.data == 'frame_house')
def handle_contacts_callback(call):
    get_frame_house(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'info_application')
def handle_info_application(call):
    get_info_application(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'application')
def handle_application_callback(call):
    chat_id = call.message.chat.id
    last_messages[chat_id] = {}
    collect_application_data(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'next_page')
def handle_next_page_callback(call):
    global current_page
    current_page += 1
    get_houses(call.message, current_page)


# Обработчик для кнопки "Предыдущая страница"
@bot.callback_query_handler(func=lambda call: call.data == 'prev_page')
def handle_prev_page_callback(call):
    global current_page
    if current_page > 1:
        current_page -= 1
    get_houses(call.message, current_page)


@bot.callback_query_handler(func=lambda call: call.data == "exit")
def exit_func(call):
    markup = types.InlineKeyboardMarkup()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="До свидания!",
                          reply_markup=markup)


page_objects = {}


def get_houses(message, current_page):
    chat_id = message.chat.id

    try:
        response = requests.get(f'{BASE_URL}houses/', timeout=60)
        if response.status_code == 200:
            houses = response.json()

            if chat_id in last_messages and current_page in page_objects:
                for message_id in page_objects[current_page]:
                    try:
                        bot.delete_message(chat_id, message_id)
                    except Exception as e:
                        pass

            start_index = (current_page - 1) * 5
            end_index = current_page * 5

            page_objects[current_page] = []

            for house in houses[start_index:end_index]:
                keyboard = types.InlineKeyboardMarkup()

                if 'slug' in house:
                    slug = house['slug']
                    view_button = types.InlineKeyboardButton("Посмотреть на сайте",
                                                             url=f"http://aroma-stroy.by/catalog/{slug}/", timeout=120)
                    keyboard.add(view_button)
                else:
                    slug = "Нет информации о slug"
                    view_button = types.InlineKeyboardButton("Ссылка недоступна", callback_data="no_slug")
                    keyboard.add(view_button)

                caption = (
                    f"Название Дома: {house['title']}\n"
                    f"Проект: {house['project_name']}\n"
                    f"Этажи: {house['floors']}\n"
                    f"Цена: {house['price']} {house['currency']}\n"
                    f"Площадь: {house['area']} м²"
                )

                photo_url = house['main_image']
                photo_response = requests.get(photo_url)
                if photo_response.status_code == 200:
                    photo = photo_response.content
                    message = bot.send_photo(chat_id, photo, caption=caption, reply_markup=keyboard)
                    page_objects[current_page].append(message.message_id)

            # Выводим клавиши пагинации только один раз после вывода всех 5 объектов
            bot.send_message(chat_id, "Выберите действие:", reply_markup=pagination_keyboard(current_page, houses))

        else:
            bot.send_message(chat_id, 'Произошла ошибка при получении данных о домах')

    except Exception as e:
        bot.send_message(chat_id, f'Произошла ошибка: {str(e)}')


# Функция для получения контактов
def get_contacts_and_address(message):
    chat_id = message.chat.id
    try:

        if chat_id in last_messages:
            bot.delete_message(chat_id, last_messages[chat_id])

        response = requests.get(f"{BASE_URL}contacts-and-address/", timeout=60)
        if response.status_code == 200:
            data = response.json()

            contacts_data = data.get("contacts", [])
            address_data = data.get("address", [])

            if contacts_data:
                bot.send_message(chat_id, "Контакты:")
                for contact in contacts_data:
                    bot.send_message(chat_id,
                                     f"{contact['department']}\n {contact['phone_number']}\n {contact['name']}")

            if address_data:
                bot.send_message(chat_id, "Адреса:")
                for address in address_data:
                    bot.send_message(chat_id,
                                     f"{address['title_address']}\nАдрес: {address['office_address']}")

            sent_message = bot.send_message(chat_id, "Нажмите кнопку 'Назад', чтобы вернуться в главное меню.",
                                            reply_markup=return_button())

            last_messages[chat_id] = sent_message.message_id

        else:
            bot.send_message(chat_id, 'Произошла ошибка при получении данных о контактах и адресах.')
    except Exception as e:
        bot.send_message(chat_id, f'Произошла ошибка: {str(e)}')


def get_services(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     f'Мы предлагаем максимально полный комплекс услуг по строительству:\n•загородных домов под '
                     f'ключ\n•коробок домов\n•домов под чистовую отделку\n•бань, беседок, садовой мебели\nА также по '
                     f'вашему желанию, мы выполним любой сложности отделочные работы.\nПри строительстве загородного '
                     f'дома с нами, Вы избавляете себя от хлопот обращения к разным исполнителям, постоянного '
                     f'контроля за стройкой, поиска всех материалов.\nЗаказывая наши услуги, Вы получаете готовый '
                     f'дом, не вкладывая в стройку собственного времени и сил.',
                     reply_markup=return_button())


def get_discount(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     f'Хотите переехать в свой собственный загородный дом уже в этом году?\n'
                     f'Тогда скорее связывайтесь с нами и мы бесплатно поможем Вам с выбором дома.Разработка проекта '
                     f'и 3D визуализация – подарок вам абсолютно бесплатно при заказе наших услуг.\n'
                     f'Вам останется лишь определиться с конструкцией дома и ждать его. И это не все!\nУ нас вы '
                     f'сможете бесплатно получить баню. Что для этого надо?\nЗаказать проект дома и в течении 3 недель '
                     f'внести аванс.\n'
                     f'С нами вы сможете сэкономить более 35 тысяч белорусских рублей.\n'
                     f'Заманчиво? Тогда быстрее звоните по номеру +375296542694\n   '
                     f'Ожидание звонка поможет скрасить наш сайт, где вы увидите уже готовые проекты ⬇️⬇️⬇️ \n'
                     f'http://aroma-stroy.by',
                     reply_markup=return_button())


def get_terms_of_payments(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     f'Хотите построить собственный загородный дом, но не можете определиться со способом '
                     f'оплаты?\nAroma Story может предложить вам несколько очень выгодных вариантов с приятными '
                     f'условиями.\nВыбор за вами🫱🏼‍🫲🏻',
                     reply_markup=terms_of_payments())


def get_installment_plan(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     f'Если кредит в банке вас не устраивает, вы можете обратиться к нам и мы предложим вам самые '
                     f'выгодные условия, на которые только способны.\nС каждым клиентом они оговариваются лично, '
                     f'но процента ниже, чем у нас, вы точно не найдете.',
                     reply_markup=return_terms_menu())


def get_decree(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     f'Следуя указу Президента Республики Беларусь №240 наша компания предоставляет льготные условия '
                     f'для строительства частных домов многодетным и малоимущим семьям, от чего многие застройщики '
                     f'отказываются.\nМы же всегда идем на уступки и принимаем государственные субсидии в качестве '
                     f'оплаты.',
                     reply_markup=return_terms_menu())


def get_credit(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     f'Aroma Stroy сотрудничает с несколькими банками: «Беларусбанк», «Белинвестбанк» и '
                     f'«МТБанк».\nУсловия по кредиту устанавливают банковские учреждения, но со своей стороны мы '
                     f'гарантируем качество и скорость.\nУже через несколько месяцев вы сможете въехать в собственный '
                     f'дом.',
                     reply_markup=return_terms_menu())


def get_price(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f'Мечтаете построить загородный коттедж? Мы предлагаем вам самые выгодные условия. '
                              f'Выбирайте свой дом 🏠',
                     reply_markup=price_of_services())


def get_tree_house(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     f'Деревянный дом – отличное решение для проживания с гарантией на 50 лет.\nЛетом такой дом '
                     f'подарит вам прохладу, зимой же сохранит тепло.\nА собственное деревообрабатывающее '
                     f'производство позволит удивить вас ценами:Цена одного м² - от 1800 б.р.\nВсе подробности в '
                     f'нашем каталоге http://aroma-stroy.by/catalog',
                     reply_markup=return_price_menu())


def get_frame_house(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     f'Наша компания строит дома и по каркасной технологии.\nЭти коттеджи устойчивы к непогоде, '
                     f'долговечны и экологичны.\nИ при таких преимуществах имеют не высокую стоимость и возводятся '
                     f'всего за пару месяцев.\nЦена каркасного дома стартует от 1300 б.р.\nВы можете выбрать проект '
                     f'из нашего каталога или же придумать свой, а мы его адаптируем для '
                     f'строительства\nhttp://aroma-stroy.by/catalog',
                     reply_markup=return_price_menu())


def get_info_application(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     f'Если у вас возникли вопросы, предложения или вам требуется дополнительная информация о наших '
                     f'услугах, мы всегда готовы помочь.\n Наши специалисты ответят на все ваши вопросы и помогут '
                     f'воплотить идеи в реальность.\n Вы можете самостоятельно позвонить нам или оставить заявку и '
                     f'менеджер свяжется с вами в течении 10 минут.',
                     reply_markup=application_button())


def collect_application_data(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Как к вам можно обращаться?")
    bot.register_next_step_handler(message, process_name_step)


def process_name_step(message):
    chat_id = message.chat.id
    name = message.text
    bot.send_message(chat_id, "Ваш номер телефона?")
    last_messages[chat_id]['name'] = name
    bot.register_next_step_handler(message, process_number_step)


def process_number_step(message):
    chat_id = message.chat.id
    number = message.text

    if not re.match(r'^\+?\d+$', number):
        bot.send_message(chat_id, "Номер телефона должен содержать только цифры и может начинаться с '+'. "
                                  "Пожалуйста, введите номер еще раз.")
        return process_name_step(message)

    bot.send_message(chat_id, "Опишите вопрос, который хотели бы обсудить.")
    last_messages[chat_id]['number'] = number
    bot.register_next_step_handler(message, process_message_step)


def process_message_step(message):
    chat_id = message.chat.id
    message_text = message.text

    application_data = last_messages[chat_id]
    application = {
        "name": application_data["name"],
        "number": application_data["number"],
        "message": message_text
    }

    try:
        response = requests.post(API_URL, json=application)
        if response.status_code == 201:
            bot.send_message(chat_id, "Заявка успешно создана! Нажмите кнопку назад для возрата в главное меню",
                             reply_markup=return_button())

            # TODO: сделать возможным отправление заявки на почту
            #  (возможно придется создать новую почту gmail)

            # subject = 'Новая заявка создана через Telegram'
            # message = f'Новая заявка была создана через Telegram.\n\n' \
            #           f'Имя: {application_data["name"]}\n' \
            #           f'Телефон: {application_data["number"]}\n' \
            #           f'Сообщение: {message_text}'
            # from_email = 'none@exemple.com'
            # recipient_list = ['Alfa-Building@yandex.by']
            #
            # send_mail(subject, message, from_email, recipient_list=recipient_list, fail_silently=False)

            # bot.send_message(chat_id, "Заявка успешно создана! Нажмите кнопку назад для возврата в главное меню",
            #                  reply_markup=return_button())
        else:
            bot.send_message(chat_id, "Произошла ошибка при создании заявки.")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")


if __name__ == '__main__':
    bot.polling(none_stop=True)
