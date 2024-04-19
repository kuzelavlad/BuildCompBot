from telebot import types


def start():
    markup_kb = types.InlineKeyboardMarkup()
    markup_kb.add(types.InlineKeyboardButton('Каталог', callback_data='catalog'))
    markup_kb.add(types.InlineKeyboardButton('Наши Услуги', callback_data='services'))
    markup_kb.add(types.InlineKeyboardButton('Акции', callback_data='discounts'))
    markup_kb.add(types.InlineKeyboardButton('Контакты ', callback_data='contacts'))
    markup_kb.add(types.InlineKeyboardButton('Условия Оплаты', callback_data='payments'))
    markup_kb.add(types.InlineKeyboardButton('Стоимость', callback_data='price'))
    markup_kb.add(types.InlineKeyboardButton('Заявка', callback_data='info_application'))
    markup_kb.add(types.InlineKeyboardButton('Выход', callback_data='exit'))

    return markup_kb


def terms_of_payments():
    markup_kb = types.InlineKeyboardMarkup()
    markup_kb.add(types.InlineKeyboardButton('Рассрочка', callback_data='installment_plan'))
    markup_kb.add(types.InlineKeyboardButton('240 Указ', callback_data='decree'))
    markup_kb.add(types.InlineKeyboardButton('Кредит ', callback_data='credit'))
    markup_kb.add(types.InlineKeyboardButton("Назад в Главное Меню", callback_data="return_to_main_menu"))

    return markup_kb


def application_button():
    markup_kb = types.InlineKeyboardMarkup()
    markup_kb.add(types.InlineKeyboardButton('Оставить Заявку', callback_data='application'))
    markup_kb.add(types.InlineKeyboardButton('Назад в Главное Меню', callback_data='return_to_main_menu'))

    return markup_kb


def price_of_services():
    markup_kb = types.InlineKeyboardMarkup()
    markup_kb.add(types.InlineKeyboardButton('Дом Из Дерева', callback_data='tree_house'))
    markup_kb.add(types.InlineKeyboardButton('Каркасный дом', callback_data='frame_house'))
    markup_kb.add(types.InlineKeyboardButton('Назад в Главное Меню', callback_data='return_to_main_menu'))

    return markup_kb


def pagination_keyboard(current_page, houses):
    markup_kb = types.InlineKeyboardMarkup(row_width=2)

    if current_page > 1:
        markup_kb.add(types.InlineKeyboardButton('Предущая Страница️', callback_data='prev_page'))
    if current_page * 5 < len(houses):
        markup_kb.add(types.InlineKeyboardButton('Следущая Страница️', callback_data='next_page'))

    markup_kb.add(types.InlineKeyboardButton('Назад в Главное Меню', callback_data='return_to_main_menu'))

    return markup_kb


def return_button():
    markup_kb = types.InlineKeyboardMarkup()
    markup_kb.add(types.InlineKeyboardButton("Назад в Главное Меню", callback_data="return_to_main_menu"))

    return markup_kb


def return_terms_menu():
    markup_kb = types.InlineKeyboardMarkup()
    markup_kb.add(types.InlineKeyboardButton("Назад", callback_data="return_to_terms_menu"))

    return markup_kb


def return_price_menu():
    markup_kb = types.InlineKeyboardMarkup()
    markup_kb.add(types.InlineKeyboardButton("Назад", callback_data="return_to_price_menu"))

    return markup_kb
