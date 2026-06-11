import asyncio
import json
import os
from random import choice

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton



TOKEN = "8802174236:AAHCC-ddw5qZAafv7pPGRd3YIh-8w9HWms0"

FILE = "data.json"

ADMIN_GROUP_ID = -1003998982278

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
data.setdefault("banned", [])
banned = data["banned"]
data.setdefault("seen", {})
seen = data["seen"]
banned = data.get("banned", [])

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

    seen.setdefault(uid, [])

    candidates = [
        (user_id, anketa)
        for user_id, anketa in users.items()
        if user_id != uid and user_id not in seen[uid]
    ]

    if not candidates:
        await message.answer("🥺 Пока нет новых анкет.")
        return

    user_id, anketa = choice(candidates)
    seen[uid].append(user_id)
    save_data(data)
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
            ),
            InlineKeyboardButton(
                text="🚨 Жалоба",
                callback_data=f"report_{user_id}"
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
    if message.chat.id == ADMIN_GROUP_ID:
        return

    if str(message.from_user.id) in banned:
        await message.answer("⛔ Вы заблокированы")
        return

    if message.text.startswith("/"):
        return

    users[str(message.from_user.id)] = message.text
    save_data(data)

    await message.answer("✅ Анкета сохранена")
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
            like_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="❤️ Лайк",
                            callback_data=f"like_{uid}"
                        ),
                        InlineKeyboardButton(
                            text="❌ Пропустить",
                            callback_data="skip"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🚨 Жалоба",
                            callback_data=f"report_{uid}"
                        )
                    ]
                ]
            )

            await bot.send_message(
                target_id,
                f"❤️ Кому-то понравилась твоя анкета!\n\n{users[uid]}",
                reply_markup=like_keyboard
            )

            if target_id in likes and uid in likes[target_id]:
                user = await bot.get_chat(uid)
                target = await bot.get_chat(target_id)

                user_contact = f"@{user.username}" if user.username else "без username"
                target_contact = f"@{target.username}" if target.username else "без username"

                await bot.send_message(uid, f"💖 Взаимный лайк!\nКонтакт: {target_contact}")
                await bot.send_message(target_id, f"💖 Взаимный лайк!\nКонтакт: {user_contact}")
    if callback.data.startswith("report_"):
        reported_id = callback.data.split("_")[1]

        admin_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🗑 Удалить",
                        callback_data=f"delete_{reported_id}"
                    ),
                    InlineKeyboardButton(
                        text="🚫 Заблокировать",
                        callback_data=f"ban_{reported_id}"
                    )
                ]
            ]
        )

        await bot.send_message(
            ADMIN_GROUP_ID,
            f"🚨 Жалоба на анкету\n\nID: {reported_id}\n\n{users.get(reported_id, 'Анкета не найдена')}",
            reply_markup=admin_keyboard
        )

        await callback.message.answer("✅ Жалоба отправлена администрации")
        await callback.answer()
        return
    if callback.data.startswith("delete_"):
        target_id = callback.data.split("_")[1]

        if target_id in users:
            del users[target_id]

        save_data(data)

        await callback.message.answer("🗑 Анкета удалена")
        await callback.answer()
        return

    if callback.data.startswith("ban_"):
        target_id = callback.data.split("_")[1]

        if target_id in users:
            del users[target_id]

        if target_id not in banned:
            banned.append(target_id)

        save_data(data)

        await callback.message.answer("🚫 Пользователь заблокирован")
        await callback.answer()
    if callback.data == "skip":
        await callback.message.answer("➡️ Пропущено")
        await callback.answer()
        return

@dp.message(Command("broadcast"))
async def broadcast(message: Message):
    if str(message.chat.id) != str(ADMIN_GROUP_ID):
        return

    text = message.text.replace("/broadcast", "").strip()

    if not text:
        await message.answer("Использование: /broadcast текст")
        return

    sent = 0

    for uid in users:
        try:
            await bot.send_message(uid, text)
            sent += 1
        except:
            pass

    await message.answer(f"✅ Отправлено: {sent}")
async def main():
    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
