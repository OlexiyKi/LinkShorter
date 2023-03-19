import asyncio
import random
import string
import os
import motor.motor_asyncio
from aiogram import Bot, Dispatcher, types
import secretkey



BOT_TOKEN = os.environ.get('BOT_TOKEN', secretkey.token)

client = motor.motor_asyncio.AsyncIOMotorClient(
        f'mongodb://root:example@{os.environ.get("DB_HOST", "localhost")}:27017')
db = client['redirecter']
collection = db['redirects']


async def start_handler(event: types.Message):
    await event.answer(
        f"Hello, {event.from_user.get_mention(as_html=True)}!",
        parse_mode=types.ParseMode.HTML,
    )


async def add_urls_handler(event: types.Message):
    long_url = event.text
    user_id = event.from_user.id
    generate_resourse_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    document = await collection.insert_one(
        {'long_url': long_url,
         'resourse_id': generate_resourse_id,
         'user_id': user_id})
    await event.answer(f"Link generated: {generate_resourse_id}")


async def get_user_urls_handler(event: types.Message):
    user_id = event.from_user.id
    documents = await collection.find({'user_id': user_id}).to_list(length=100)
    if documents:
        for document in documents:
            await event.answer(document['long_url'])
    else:
        await event.answer("Sorry, there are no documents in your database")


async def get_urls_handler(event: types.Message):
    document = await collection.find_one({'resourse_id': event.text})
    if document is None:
        await event.answer('Sorry,no found')
    long_url = document['long_url']
    await event.answer(long_url)


async def main():
    bot = Bot(token=BOT_TOKEN)
    try:
        disp = Dispatcher(bot=bot)
        disp.register_message_handler(start_handler, commands={"start", "restart"})
        disp.register_message_handler(add_urls_handler, regexp=r'http(s)?://.*')            #регистрация хєндлеров
        disp.register_message_handler(get_user_urls_handler, commands={'get'})
        disp.register_message_handler(get_urls_handler, regexp=r'\w+')
        await disp.start_polling()
    finally:
        await bot.close()




asyncio.run(main())
