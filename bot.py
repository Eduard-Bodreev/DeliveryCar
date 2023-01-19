import logging
import time

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import keyboards
from sqlite import db_start, send_customer, send_deliver, remove_deliver, remove_customer, send_orders, add_orders, \
    add_customer, add_deliver, get_cus, get_del_id, get_cus_id, select, upd_orders

logging.basicConfig(level=logging.INFO)

API_TOKEN = '5896227879:AAGieMnU1QLKKP5mgzwYjpu7OSYcRYGO64E'


async def on_startup(_):
    await db_start()


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

global order_id


# States


class Form(StatesGroup):
    role = State()
    car_apps = State()

    """for deliver"""
    car_mark = State()
    remoteness = State()
    adr = State()
    geo = State()
    car_app = State()
    latitude = State()
    longitude = State()
    agree = State()
    geo_agree = State()
    search = State()
    end = State()

    """for customer"""
    adr_to = State()
    timing = State()
    radius = State()
    cus_agree = State()

    """for admin"""
    auth = State()
    ex = State()
    acc = State()
    back = State()
    remove = State()
    customer_id = State()
    deliver_id = State()
    status = State()
    order = State()


@dp.message_handler(commands=['admin'])
async def auth_admin(message: types.Message):
    await Form.auth.set()

    await bot.send_message(message.chat.id, "Введите пароль")


@dp.message_handler(state=Form.auth)
async def auth_admin(message: types.Message, state: FSMContext):
    if message.text == "1":
        async with state.proxy() as data:
            await Form.acc.set()
            data['auth'] = True
            await bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboards.markup_admin)
    else:
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Выход")
        markup1.add(item1)
        await state.finish()
        await message.reply("Пароль не верный")
        await bot.send_message(message.chat.id, "Для начала работы с ботом введите /start",
                               reply_markup=keyboards.start)


@dp.message_handler(state=Form.acc)
async def auth_admin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['acc'] = message.text
    if message.text == "Доставщики":
        await bot.send_message(message.chat.id, f"Доставщики: ", reply_markup=keyboards.markup_admin_remove)
        await bot.send_message(message.chat.id, await send_deliver())
        await Form.back.set()

    elif message.text == "Заказчики":
        await bot.send_message(message.chat.id, f"Заказчики: ", reply_markup=keyboards.markup_admin_remove)
        await bot.send_message(message.chat.id, await send_customer())
        await Form.back.set()

    elif message.text == "Заказы":
        await bot.send_message(message.chat.id, f"Выберите действие", reply_markup=keyboards.markup_admin_order)
        """await bot.send_message(message.chat.id, await send_orders())"""
        await Form.order.set()

    elif message.text == "Выход":
        await state.finish()
        await message.reply("Возвращайтесь", reply_markup=keyboards.start)

    else:
        await bot.send_message(message.chat.id, "блин", reply_markup=keyboards.markup_admin)


@dp.message_handler(state=Form.back)
async def back_admin(message: types.Message):
    if message.text == "Удалить запись":
        await bot.send_message(message.chat.id, f"Для того, что бы удалить запись укажите user_id: ")
        await Form.remove.set()

    elif message.text == "Назад":
        await bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboards.markup_admin)
        await Form.acc.set()
    else:
        await bot.send_message(message.chat.id, "блин", reply_markup=keyboards.markup_admin)


@dp.message_handler(state=Form.order)
async def order_admin(message: types.Message):
    if message.text == "Посмотреть заказы":
        await bot.send_message(message.chat.id, f"Заказы: ")
        await bot.send_message(message.chat.id, await send_orders())

    elif message.text == "Создать заказ":
        await bot.send_message(message.chat.id, "Что бы создать заказ введите id заказчика",
                               reply_markup=keyboards.markup_admin)
        await Form.customer_id.set()

    elif message.text == "Удалить заказ":
        await bot.send_message(message.chat.id, f"Для того, что бы удалить запись укажите user_id: ")
        await Form.acc.set()

    elif message.text == "Назад":
        await bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboards.markup_admin)
        await Form.acc.set()

    else:
        await bot.send_message(message.chat.id, "блин", reply_markup=keyboards.markup_admin)


@dp.message_handler(state=Form.customer_id)
async def create_order_customer_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['customer_id'] = message.text

        data['status'] = "создан"
    await bot.send_message(message.chat.id, "введите id доставщика")
    await Form.deliver_id.set()
    await bot.send_message(message.chat.id, str(await get_cus(message.text)))

    if message.text == "Назад":
        await bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboards.markup_admin)
        await Form.acc.set()


@dp.message_handler(state=Form.deliver_id)
async def create_order(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboards.markup_admin)
        await Form.acc.set()
    else:
        async with state.proxy() as data:
            data['deliver_id'] = message.text
        await bot.send_message(message.chat.id, "заказ создан", reply_markup=keyboards.markup_admin)
        await add_orders(state, user_id=message.date)
        await Form.acc.set()


@dp.message_handler(state=Form.remove)
async def back_admin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Назад":
            await bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboards.markup_admin)
            await Form.acc.set()
        else:
            await bot.send_message(message.chat.id, f"Запись с user_id {message.text} удалена",
                                   reply_markup=keyboards.markup_admin)
            print(message.text)
            if data['acc'] == "Заказы":
                await remove_customer(message.text)
            elif data['acc'] == "Доставщики":
                await remove_deliver(message.text)

            await Form.acc.set()


@dp.callback_query_handler()
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    code = callback_query.data[-1]
    print(f"callback code={code}")
    await bot.send_message(callback_query.from_user.id, f'Нажата инлайн кнопка! code={code}')


@dp.message_handler(commands=["geo"])
async def geo(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    await bot.send_message(message.chat.id, "Привет! Нажми на кнопку и передай мне свое местоположение",
                           reply_markup=keyboard)


@dp.message_handler(content_types=["location"])
async def location(message):
    if message.location is not None:
        await bot.send_location(message.chat.id, message.location.latitude, message.location.longitude)
        cus_id = await get_cus_id(message.chat.id)
        await bot.send_location(cus_id, message.location.latitude, message.location.longitude)


@dp.message_handler(commands=["apps"])
async def apps(message):
    await bot.send_message(message.chat.id, "Напишите приложения для аренды машины каршеринга, "
                                            "к которым вы имеете доступ.")

    await Form.car_apps.set()


@dp.message_handler(state=Form.car_apps)
async def add_car_apps(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['car_apps'] = message.text
        await bot.send_message(message.chat.id, "Супер, для начала работы с ботом введите /start",
                               reply_markup=keyboards.start)


@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    await bot.send_message(message.chat.id, "Эта инструкция поможет разобраться с использованием данного бота,\n"
                                            "для начала работы с ботом введите /start, \n"
                                            "далее на выбор будут предложены две роли: Заказчик и Доставщик \n"
                                            "(Только не пугайтесь, поработать курьером для доставки машины прийдется "
                                            "только во время вашей поездки, на работу мы Вас не пытаемся устроить).\n"
                                            "Перед началом работы пропишите команду /apps, что бы мы знали какие"
                                            " машины каршеринга вам можно доставлять. \n"
                                            "Что бы получить доступ к админ-панели введите команду /admin , "
                                            "но учтите, что нужен пароль!\n"
                                            "На этом все, удачного пользования!",
                           reply_markup=keyboards.start)


@dp.message_handler(commands='хуй')
async def cmd_help(message: types.Message):
    await bot.send_message(message.chat.id, "Сам хуй", reply_markup=keyboards.start)


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """

    # Set state
    await Form.role.set()

    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_name = message.from_user.first_name
    logging.info(f'{user_id=} {user_full_name=} {time.asctime()}')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Заказать")
    item2 = types.KeyboardButton("Доставить")
    markup.add(item1, item2)

    await bot.send_message(message.chat.id, f"Привет, {user_name}! Этот бот разработан в рамках мерояприятия 'Я в деле'"
                                            f" командой deceda.", reply_markup=markup)


@dp.message_handler(state=Form.role)
async def process_role(message: types.Message, state: FSMContext):
    """
    Process user role
    """

    async with state.proxy() as data:
        markup = types.ReplyKeyboardRemove()
        if message.text == "Доставить":
            data['role'] = "deliver"
            await Form.car_app.set()

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Яндекс Драйв")
            item2 = types.KeyboardButton("Делимобиль")
            item3 = types.KeyboardButton("Ситидрайв")
            item4 = types.KeyboardButton("BelkaCar")
            markup.add(item1, item2)
            markup.add(item3, item4)

            await bot.send_message(message.chat.id, "Какое приложение для каршеринга вы используете?",
                                   reply_markup=markup)
        elif message.text == "Заказать":
            data['role'] = "customer"
            await Form.adr_to.set()
            await bot.send_message(message.chat.id, "Укажите адрес", reply_markup=markup)

        elif message.text == "Выход" or message.text == "/stop":
            await state.finish()
            await message.reply("Возвращайтесь", reply_markup=keyboards.start)


@dp.message_handler(state=Form.adr_to)
async def process_adr_to(message: types.Message, state: FSMContext):
    """
    Process user role
    """
    if message.text == "Выход" or message.text == "/stop":
        await state.finish()
        await message.reply("Возвращайтесь", reply_markup=keyboards.start)
    else:
        async with state.proxy() as data:
            data['adr_to'] = message.text
        await Form.timing.set()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("В течение 15 минут")
        item2 = types.KeyboardButton("В течение 30 минут")
        item3 = types.KeyboardButton("В течение часа")
        markup.add(item1, item2, item3)
        await bot.send_message(message.chat.id, "Время доставки?", reply_markup=markup)


@dp.message_handler(state=Form.car_app)
async def process_car(message: types.Message, state: FSMContext):
    # Update state and data
    if message.text == "Выход" or message.text == "/stop":
        await state.finish()
        await message.reply("Возвращайтесь", reply_markup=keyboards.start)
    else:
        markup = types.ReplyKeyboardRemove()
        await state.update_data(car_app=str(message.text))
        await Form.car_mark.set()
        await bot.send_message(message.chat.id, "Укажите модель и номер машины?", reply_markup=markup)


@dp.message_handler(state=Form.car_mark)
async def process_car(message: types.Message, state: FSMContext):
    # Update state and data
    if message.text == "Выход" or message.text == "/stop":
        await state.finish()
        await message.reply("Возвращайтесь", reply_markup=keyboards.start)
    else:
        await state.update_data(car_mark=str(message.text))
        await Form.remoteness.set()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Заказы рядом")
        item2 = types.KeyboardButton("Заказы по адресу")
        markup.add(item1, item2)
        await bot.send_message(message.chat.id, f"Машина {message.text}", reply_markup=markup)


@dp.message_handler(state=Form.timing)
async def process_timing(message: types.Message, state: FSMContext):
    # Update state and data
    if message.text == "Выход" or message.text == "/stop":
        await state.finish()
        await message.reply("Возвращайтесь", reply_markup=keyboards.start)
    else:
        await state.update_data(timing=str(message.text))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("3 км- 49₽")
        item2 = types.KeyboardButton("2 км- 99₽")
        item3 = types.KeyboardButton("1 км- 149₽")
        item4 = types.KeyboardButton("Точно по адресу- 249₽")
        markup.add(item1, item2, item3, item4)
        await bot.send_message(message.chat.id, "В каком радиусе доставить?", reply_markup=markup)
        await Form.radius.set()


@dp.message_handler(state=Form.remoteness)
async def process_remoteness(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Заказы рядом":
            data['remoteness'] = "nearby"
            await Form.adr.set()
            await bot.send_message(message.chat.id, "Отправте геопозицию или укажите адрес",
                                   reply_markup=keyboards.markup_request)
        elif message.text == "Заказы по адресу":
            data['remoteness'] = "at"
            await Form.adr.set()
            await bot.send_message(message.chat.id, "Укажите адрес")
        elif message.text == "Выход" or message.text == "/stop":
            await state.finish()
            await message.reply("Возвращайтесь", reply_markup=keyboards.start)


@dp.message_handler(state=Form.radius)
async def process_radius(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['radius'] = message.text

        # And send message
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('role: ', data['role']),
                md.text('adr_to:', data['adr_to']),
                md.text('timing:', data['timing']),
                md.text('radius:', data['radius']),
                sep='\n',
            ),
            reply_markup=keyboards.start,

        )
    await add_customer(state, customer_id=message.date, user_id=message.from_user.id)
    await bot.send_message(message.chat.id, "Идет поиск...")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("3 км- 49₽")
    item2 = types.KeyboardButton("2 км- 99₽")
    item3 = types.KeyboardButton("1 км- 149₽")
    item4 = types.KeyboardButton("Точно по адресу- 249₽")
    markup.add(item1, item2, item3, item4)
    await bot.send_message(message.chat.id, "Если поиск идет слишком долго- выберите радиус доставки заново",
                           reply_markup=markup)
    del_id = None
    while del_id is None:
        del_id = await get_del_id(message.chat.id)
        print(del_id)
    else:
        print(del_id)
        markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton('/Выполнен'), KeyboardButton('/Сорван'))
        await bot.send_message(message.chat.id, f'Ваш заказ принят: \n '
                                                f'Приложение каршеринга: {await select("car_app", "deliver", "user_id", del_id)}\n'
                                                f'Машина {await select("car_mark", "deliver", "user_id", del_id)}',
                               reply_markup=markup_request)

        await state.finish()


@dp.message_handler(content_types=["location", "text"], state=Form.adr)
async def process_adr(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        if message.location is not None:
            data['adr'] = f"{message.location.latitude}, {message.location.longitude}"
        else:
            data['adr'] = message.text

        data['latitude'] = "0"
        data['longitude'] = "0"
        # And send message
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('role: ', data['role']),
                md.text('car app:', data['car_app']),
                md.text('car mark:', data['car_mark']),
                md.text('adr:', data['adr']),
                sep='\n',
            ),
            reply_markup=keyboards.start,
            parse_mode=ParseMode.MARKDOWN,
        )
    await add_deliver(state, deliver_id=message.date, user_id=message.from_user.id)
    await bot.send_message(message.chat.id, "Идет поиск...")
    await bot.send_message(message.chat.id, "Если поиск идет слишком долго- отправте геолокацию или адрес заново",
                           reply_markup=keyboards.markup_request)
    cus_id = None
    while cus_id is None:
        cus_id = await get_cus_id(message.chat.id)
    else:
        print(cus_id)
        markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton('Принять заявку'), KeyboardButton('Отклонить заявку'))
        await bot.send_message(message.chat.id, f'В данном районе есть заказ: \n '
                                                f'{await select("radius", "customer", "user_id", cus_id)}\n'
                                                f'{await select("adr_to", "customer", "user_id", cus_id)}',
                               reply_markup=markup_request)
        await Form.agree.set()

    # await state.finish()


@dp.message_handler(content_types=["location", "text"], state=Form.agree)
async def process_radius(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        if message.text == "Принять заявку":
            data['agree'] = "yes"
            await Form.geo_agree.set()
            markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton('Поделиться геопозицией🗺️', request_location=True), KeyboardButton('Не делиться'))
            await bot.send_message(message.chat.id, "Делиться геопозицией?", reply_markup=markup_request)
        elif message.text == "Отклонить заявку":
            data['agree'] = "no"
            await bot.send_message(message.chat.id, "Очень жаль, отправте заявку на доставку снова",
                                   reply_markup=keyboards.start)
            await state.finish()


@dp.message_handler(content_types=["location", "text"], state=Form.geo_agree)
async def process_radius(message: types.Message, state: FSMContext):
    markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/Подъезжаю'))
    async with state.proxy() as data:
        if message.location is not None:
            data['geo_agree'] = message.location
            await bot.send_message(message.chat.id, "Супер")
            await state.finish()
        else:
            data['geo_agree'] = "no"
            await bot.send_message(message.chat.id, "Очень жаль")
            await state.finish()
    await bot.send_message(message.chat.id, "Отправте /Подъезжаю когда вам останется 5 минут до конца поездки",
                           reply_markup=markup_request)


# agree = State()
# search = State()
@dp.message_handler(commands=["Подъезжаю"])
async def process_radius(message: types.Message, state: FSMContext):
    await bot.send_message(await get_cus_id(message.chat.id), "Водитель подъезжает, включите автобронирование")
    markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('/Выполнен'), KeyboardButton('/Сорван'))
    await bot.send_message(message.chat.id, "Супер", reply_markup=markup_request)
    await state.finish()


# в


@dp.message_handler(commands=["Выполнен"])
async def process_radius(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data['role'] == "deliver":
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
            keyboard.add(button_geo)
            await bot.send_message(message.chat.id, "Чудесно, отправте свою геолокацию",
                                   reply_markup=keyboard)
        elif data['role'] == "customer":
            await bot.send_message(message.chat.id, "Супер", reply_markup=keyboards.start)
            await bot.send_message(400156846, f"Выволнение заказа подтверждено заказчиком {message.chat.id}",
                                   reply_markup=keyboards.start)
            await upd_orders("выполнен", "customer_id", message.chat.id)


@dp.message_handler(commands=["Сорван"])
async def process_radius(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, "Жаль...(", reply_markup=keyboards.start)
    async with state.proxy() as data:
        if data['role'] == "deliver":
            await upd_orders("сорван", "deliver_id", message.chat.id)
        elif data['role'] == "customer":
            await upd_orders("сорван", "customer_id", message.chat.id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
