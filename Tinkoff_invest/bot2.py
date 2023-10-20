from aiogram import types, executor, Bot, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db2 import *
TOKEN = '6308347573:AAHRkAHGuBCmw_cDgm8J9z1pA3N9AZZ3bb8'
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class user_reg(StatesGroup):
    nickname = State()
    token = State()
    email = State()


@dp.message_handler(state=user_reg.nickname)
async def add_nickname_(message:types.Message, state=FSMContext):
    chat_id = message.chat.id
    await state.finish()
    if len(message.text) >=16:
        await bot.send_message(chat_id, "Никнейм не должен превышать 15 символов")
    elif  message.text[0].isdigit():
        await bot.send_message(chat_id, "Никнейм не должен начинаться с цифры")
    else:
        add_user_nickname(message)

# @dp.message_handler(state=add_user_nickname)
# async def add_token_(message :types.Message, state = FSMContext):
#     chat_id = message.chat.id
#     await bot.send_message(chat_id, 'suc')

@dp.message_handler(commands=['start'])
async def start_message(message:types.Message, state= FSMContext):
    chat_id = message.chat.id
    if user_exists(chat_id):
        await bot.send_message(chat_id, "Вы уже зарегестрированны!")
    else:
        add_user(message)
        await bot.send_message(chat_id, f"Привет, {message.chat.first_name}!\nВведи свой никнейм")
        await user_reg.nickname.set()



if __name__ == "__main__":
    executor.start_polling(dp)

