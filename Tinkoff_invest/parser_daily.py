from tinkoff.invest import Client
from datetime import datetime
from db import Database
from connection_db import connection
from bot import bot
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime, timedelta
import pytz
from tinkoff.invest import Client, Interval



db = Database(connection)

async def notify_user_about_stocks():
    users = db.get_all_users()
    for user_id in users:
        message = ''
        shares_list = db.get_share(user_id) 
        if shares_list:
            stocks_info = stock_price_change(shares_list)
            for comp in stocks_info.keys():
                if abs(stocks_info[comp]) >= 5:
                    message += f'Стоимость акции {comp} изменились на {stocks_info[comp]}% \n'
            await bot.send_message(chat_id=user_id, text=message)
            
            
def stock_price_change(stock_ticker, user_id):
    changes = dict()
    with Client(db.get_token(user_id)) as client:
        for share in stock_ticker:
            current_price = client.market_data.get_last_prices(figi=share).last_price
            previous_close_price = client.market_data.get_candles(figi=share, from_=datetime.now(), interval=Interval.DAY).candles[-2].close
            price_change_percent = ((current_price - previous_close_price) / previous_close_price) * 100
            changes[share] = price_change_percent
    return changes

async def daily_job():
    while True:
        now = datetime.now(pytz.timezone("Europe/Moscow"))
        next_run = now + timedelta(days=1)
        next_run = next_run.replace(hour=9, minute=0, second=0, microsecond=0) 
        sleep_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(sleep_seconds)
        await notify_user_about_stocks()
        

