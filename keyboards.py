from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

inline_kb_full = InlineKeyboardMarkup(row_width=2)
inline_kb_full.add(InlineKeyboardButton('Заказы', callback_data='/orders'))
inline_btn_3 = InlineKeyboardButton('Доставщики', callback_data='/deliverers')
inline_btn_4 = InlineKeyboardButton('Сообщения', callback_data='/msg')
inline_btn_5 = InlineKeyboardButton('Завершенные заказы', callback_data='/completed ')
inline_kb_full.add(inline_btn_3, inline_btn_4, inline_btn_5)

markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Отправить свою локацию 🗺️', request_location=True), KeyboardButton('Указать адрес')
)

markup_admin = ReplyKeyboardMarkup(resize_keyboard=True)
item1 = KeyboardButton("Заказчики")
item2 = KeyboardButton("Доставщики")
item3 = KeyboardButton("Сообщения")
item4 = KeyboardButton("Заказы")
item5 = KeyboardButton("Выход")
markup_admin.add(item1, item2, item4)
markup_admin.add(item5)

markup_admin_remove = ReplyKeyboardMarkup(resize_keyboard=True)
item1 = KeyboardButton("Удалить запись")
item2 = KeyboardButton("Назад")
markup_admin_remove.add(item1, item2)

markup_admin_order = ReplyKeyboardMarkup(resize_keyboard=True)
item1 = KeyboardButton("Посмотреть заказы")
item2 = KeyboardButton("Создать заказ")
item3 = KeyboardButton("Удалить заказ")
item4 = KeyboardButton("Назад")
markup_admin_order.add(item1, item2, item3, item4)

start = ReplyKeyboardMarkup(resize_keyboard=True)
item1 = KeyboardButton("/start")
item2 = KeyboardButton("/help")
item3 = KeyboardButton("/apps")
start.add(item1)
start.add(item2, item3)
