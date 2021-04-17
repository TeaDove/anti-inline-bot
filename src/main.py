# quickstart для Aiogram

import logging
import configparser

from aiogram import Bot, Dispatcher, executor, types, utils
import aiogram
import redis

START = open("res/start", 'r').read()
config = configparser.ConfigParser()
config.read("secret_data/config.ini")
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%y-%m-%d %H:%M')
bot = Bot(token=config['credentials']['telegram-api'])
dp = Dispatcher(bot)

r = redis.Redis(
    host='localhost',
    port=10001)
NAME = "anti-inline-bot"

async def get_chat_dict(chat_id: int) -> dict:
    chat_dict = r.hgetall(f"{NAME}:{chat_id}")
    default_dict = {b'deletion': 1, b'q': 1}
    if not bool(chat_dict):
        r.hset(f"{NAME}:{chat_id}", mapping=default_dict)
        chat_dict = default_dict
    elif set(chat_dict.keys()) != set(default_dict.keys()):
        r.delete(f"{NAME}:{chat_id}")
        r.hset(f"{NAME}:{chat_id}", mapping=default_dict)
    return chat_dict


@dp.my_chat_member_handler()
async def send(event: types.ChatMemberUpdated): 
    if "new_chat_member" in event and event["new_chat_member"]["status"] == "member":
        await event.bot.send_message(event["chat"]["id"], START, parse_mode="html")
        await get_chat_dict(event["chat"]["id"])


@dp.message_handler(commands=['start', 'help'])
async def send(message: types.Message): 
    await message.answer(START, parse_mode="html")


@dp.message_handler(commands=['toggle'])
async def send(message: types.Message): 
    if message.chat.type == types.ChatType.PRIVATE:
        await message.answer("Error, you can't change this setting in private chat")
    else:
        member = await message.chat.get_member(message.from_user.id)
        if ('status' in member and member['status'] != "member"):
            chat_dict = await get_chat_dict(message.chat.id)
            to_set = b'0' if chat_dict[b'deletion'] == b'1' else b'1'
            chat_dict[b'deletion'] = to_set
            r.hset(f"{NAME}:{message.chat.id}", mapping=chat_dict)
            await message.answer(f"No I <b>will{'' if to_set == b'1' else ' not'}</b> delete messages via inline bots", parse_mode="html")


@dp.message_handler(commands=['q'])
async def send(message: types.Message): 
    if message.chat.type == types.ChatType.PRIVATE:
        await message.answer("Error, you can't change this setting in private chat")
    else:
        member = await message.chat.get_member(message.from_user.id)
        if ('status' in member and member['status'] != "member"):
            chat_dict = await get_chat_dict(message.chat.id)
            to_set = b'0' if chat_dict[b'q'] == b'1' else b'1'
            chat_dict[b'q'] = to_set
            r.hset(f"{NAME}:{message.chat.id}", mapping=chat_dict)
            await message.answer(f"No I <b>will{'' if to_set == b'1' else ' not'}</b> omit warning", parse_mode="html")


@dp.message_handler(content_types=types.ContentType.ANY)
async def send(message: types.Message): 
    chat_dict = await get_chat_dict(message.chat.id)
    print(message)
    if chat_dict[b'deletion'] == b'1' and 'via_bot' in message:
        try:
            await message.delete()
        except:
            pass
        if chat_dict[b'q'] == b'0':
            await message.answer(f"<b>Warning</b>, {message.from_user.get_mention(as_html=True)}, no inline bots in this chat!", parse_mode="html")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)