import os
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import pandas as pd

TOKEN = "7848695900:AAHqxq3UJeazVnziwkPG3unFIaYZ_BKVeLA"
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# Завантажуємо таблицю
file_path = "LoyaltyHotelPrograms.xlsx"
try:
    df = pd.read_excel(file_path)
except FileNotFoundError:
    print(f"Файл {file_path} не знайдено!")
    exit(1)
except Exception as e:
    print(f"Помилка завантаження файлу: {e}")
    exit(1)

weights = {
    "Price Segment": 5,
    "Style/Vibe": 5,
    "Loyalty Program's Benefits": 5,
    "Hotels Benefits": 4,
    "What's near Hotels": 4,
    "Country": 5,
    "Rating": 4
}

user_data = {}

def get_best_loyalty_program(user_answers):
    def calculate_score(row):
        score = 0
        for key, weight in weights.items():
            if key in user_answers and str(user_answers[key]).lower() in str(row[key]).lower():
                score += weight
        return score

    df["Score"] = df.apply(calculate_score, axis=1)
    columns = ["Loyalty Program", "Hotel Brand"] + (["Website"] if "Website" in df.columns else [])
    top_programs = df.sort_values(by="Score", ascending=False).head(8)[columns]
    return top_programs

# Клавіатури з варіантами відповідей (на українській мові)
price_segment_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Економ"), KeyboardButton(text="Середній")],
        [KeyboardButton(text="Преміум"), KeyboardButton(text="Люкс")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

style_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Модерн"), KeyboardButton(text="Затишний"), KeyboardButton(text="Еко")],
        [KeyboardButton(text="Люкс"), KeyboardButton(text="Молодіжний"), KeyboardButton(text="Тематичний")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

benefits_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Знижки"), KeyboardButton(text="Безкоштовні ночі")],
        [KeyboardButton(text="Швидкі бали"), KeyboardButton(text="Елітний статус")],
        [KeyboardButton(text="Подарунки")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

hotel_benefits_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Wi-Fi"), KeyboardButton(text="Басейн")],
        [KeyboardButton(text="Ресторан"), KeyboardButton(text="Спортзал")],
        [KeyboardButton(text="Сімейний")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

location_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Центр міста"), KeyboardButton(text="Аеропорт")],
        [KeyboardButton(text="Бізнес-зона"), KeyboardButton(text="Природа")],
        [KeyboardButton(text="Шопінг")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

country_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="США"), KeyboardButton(text="Іспанія")],
        [KeyboardButton(text="ОАЕ"), KeyboardButton(text="Таїланд")],
        [KeyboardButton(text="Інше")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

rating_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="60"), KeyboardButton(text="70")],
        [KeyboardButton(text="80"), KeyboardButton(text="90")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@router.message(Command(commands=["start"]))
async def start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    await message.reply("Привіт! Я допоможу тобі підібрати програму лояльності для готелів. Який у тебе бюджет? Обери варіант:", reply_markup=price_segment_kb)

@router.message()
async def handle_answers(message: types.Message):
    user_id = message.from_user.id
    text = message.text.lower()

    if user_id not in user_data:
        user_data[user_id] = {}

    if "Price Segment" not in user_data[user_id]:
        user_data[user_id]["Price Segment"] = text.capitalize()
        await message.reply(f"Чудово, {text.capitalize()} — хороший вибір. Який стиль готелів тобі подобається? Обери:", reply_markup=style_kb)
    elif "Style/Vibe" not in user_data[user_id]:
        user_data[user_id]["Style/Vibe"] = text
        await message.reply(f"{text.capitalize()} — цікаво! Які бонуси від програми лояльності тобі потрібні? Вибирай:", reply_markup=benefits_kb)
    elif "Loyalty Program's Benefits" not in user_data[user_id]:
        user_data[user_id]["Loyalty Program's Benefits"] = text
        await message.reply(f"{text.capitalize()} — зрозуміло. Що для тебе важливо в готелі? Обери:", reply_markup=hotel_benefits_kb)
    elif "Hotels Benefits" not in user_data[user_id]:
        user_data[user_id]["Hotels Benefits"] = text
        await message.reply(f"{text.capitalize()} — гарно. Що має бути поруч із готелем? Вибирай:", reply_markup=location_kb)
    elif "What's near Hotels" not in user_data[user_id]:
        user_data[user_id]["What's near Hotels"] = text
        await message.reply(f"{text.capitalize()} — чудово. В якій країні плануєш відпочивати? Обери:", reply_markup=country_kb)
    elif "Country" not in user_data[user_id]:
        user_data[user_id]["Country"] = text if text != "інше" else "Будь-яка"
        await message.reply(f"{text.capitalize()} — приємне місце. Який рейтинг тобі підходить? Вкажи число:", reply_markup=rating_kb)
    elif "Rating" not in user_data[user_id]:
        try:
            rating = int(text)
            user_data[user_id]["Rating"] = rating
            results = get_best_loyalty_program(user_data[user_id])
            reply_text = "Ось кілька програм лояльності, які можуть тобі підійти:\n"
            for _, row in results.iterrows():
                program = row["Loyalty Program"]
                brand = row["Hotel Brand"]
                website = row.get("Website", None)
                if website:
                    reply_text += f"🏨 [{brand} - {program}]({website})\n"
                else:
                    reply_text += f"🏨 {brand} - {program}\n"
            reply_text += "\nСподіваюся, тобі сподобається! Хочеш спробувати ще раз? Напиши /start."
            await message.reply(reply_text, parse_mode="Markdown")
            user_data.pop(user_id)
        except ValueError:
            await message.reply("Рейтинг має бути числом. Спробуй ще раз:", reply_markup=rating_kb)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())