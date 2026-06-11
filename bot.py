import asyncio
import json
import os
from random import choice

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton



TOKEN = "8802174236:AAHCC-ddw5qZAafv7pPGRd3YIh-8w9HWms0"

FILE = "data.json"


def load_data():
    if os.path.exists(FILE):
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "likes": {}}


def save_data(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


data = load_data()
users = data["users"]
likes = data["likes"]


bot = Bot(token=TOKEN)
dp = Dispatcher()
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Смотреть анкеты")],
        [KeyboardButton(text="👤 Моя анкета")],
        [KeyboardButton(text="🗑 Удалить анкету")],
        [KeyboardButton(text="⚠️ Жалоба")]
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start(message: Message):
   

    await message.answer(
        await message.answer(
        "Выберите действие внизу👇\n\n"
        "🪷 P.S. Пример анкеты: https://t.me/buddhism_cooperation/25?comment=14",
        reply_markup=menu
    )
)
    
@dp.message(Command("search"))
async def search(message: Message):
    uid = str(message.from_user.id)

    if uid not in users:
        await message.answer("⚠️ Сначала отправь анкету")
        return

    candidates = [
        (user_id, anketa)
        for user_id, anketa in users.items()
        if user_id != uid
    ]

    if not candidates:
        await message.answer("😢 Пока нет других анкет")
        return

    user_id, anketa = choice(candidates)

    
    keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="❤️ Лайк",
                callback_data=f"like_{user_id}"
            ),
            InlineKeyboardButton(
                text="❌ Пропустить",
                callback_data="skip"
            )
        ]
    ]
)

    await message.answer(anketa, reply_markup=keyboard)
@dp.message(Command("profile"))
async def profile(message: Message):
    uid = str(message.from_user.id)

    if uid not in users:
        await message.answer("⚠️ У тебя пока нет анкеты")
        return

    await message.answer("👤 Твоя анкета:\n\n" + users[uid])



@dp.message(Command("delete"))
async def delete_profile(message: Message):
    uid = str(message.from_user.id)

    if uid not in users:
        await message.answer("⚠️ У тебя и так нет анкеты")
        return

    del users[uid]

    if uid in likes:
        del likes[uid]

    save_data(data)

    await message.answer("🗑 Анкета удалена")
@dp.message(lambda message: message.text == "⚠️ Жалоба")
async def report(message: Message):
    await message.answer(
    "⚠️ Для отправки жалобы напиши сюда:\n\@buddhism_cooperation_bot"
)
@dp.message(lambda message: message.text == "🔎 Смотреть анкеты")
async def button_search(message: Message):
    await search(message)

@dp.message(lambda message: message.text == "👤 Моя анкета")
async def button_profile(message: Message):
    await profile(message)

@dp.message(lambda message: message.text == "🗑 Удалить анкету")
async def button_delete(message: Message):
    await delete_profile(message)
@dp.message()
async def save_anketa(message: Message):
    if message.text.startswith("/"):
        return

    users[str(message.from_user.id)] = message.text
    save_data(data)

    await message.answer("✅ Анкета сохранена! Напиши /search")
@dp.callback_query()
async def handle(callback: CallbackQuery):
    uid = str(callback.from_user.id)

    if callback.data.startswith("copy_"):
        target_id = callback.data.split("_")[1]

        if target_id in users:
            await callback.message.answer(users[target_id])

        await callback.answer("📋 Анкета отправлена")
        return

      if callback.data.startswith("like_"):
        target_id = callback.data.split("_")[1]
        likes.setdefault(uid, [])

        if target_id not in likes[uid]:
            likes[uid].append(target_id)

        save_data(data)

        await callback.message.answer("💌 Лайк отправлен!")

        if target_id in users:
            await bot.send_message(
                target_id,
                f"❤️ Кому-то понравилась твоя анкета!\n\n{users[uid]}"
            )
                    return
        # взаимный лайк
        
        if target_id in likes and uid in likes[target_id]:
            user = await bot.get_chat(uid)
            target = await bot.get_chat(target_id)

            user_contact = f"@{user.username}" if user.username else f"id: {uid}"
            target_contact = f"@{target.username}" if target.username else f"id: {target_id}"

            await bot.send_message(uid, f"💖 Взаимный лайк!\nКонтакт: {target_contact}")
            await bot.send_message(target_id, f"💖 Взаимный лайк!\nКонтакт: {user_contact}")

    if callback.data == "skip":
        await callback.message.answer("➡️ Пропущено")

    await callback.answer()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
