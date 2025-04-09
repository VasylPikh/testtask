import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import pandas as pd

TOKEN = "ТУТ_ВСТАВ_СВІЙ_ТОКЕН"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Завантажуємо таблицю
file_path = "LoyaltyHotelPrograms.xlsx"
df = pd.read_excel(file_path)

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
    top_programs = df.sort_values(by="Score", ascending=False).head(8)[["Loyalty Program", "Hotel Brand", "Score"]]
    
    return top_programs

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    await message.reply("Привіт! 🏨 Давай знайдемо тобі ідеальну програму лояльності! \n\n👉 Спочатку скажи, який у тебе бюджет? (Economy, Midscale, Premium, Luxury)")

@dp.message_handler()
async def handle_answers(message: types.Message):
    user_id = message.from_user.id
    text = message.text.lower()

    if user_id not in user_data:
        user_data[user_id] = {}

    if "price_segment" not in user_data[user_id]:
        user_data[user_id]["Price Segment"] = text.capitalize()
        await message.reply("Який стиль готелів тобі подобається? 😎 (Modern, Cozy, Eco, Luxury, Youthful, Thematic)")
    elif "style" not in user_data[user_id]:
        user_data[user_id]["Style/Vibe"] = text
        await message.reply("Які бонуси в програмі тебе цікавлять? 🎁 (Discounts, Free nights, Fast points, Elite status, Gifts)")
    elif "benefits" not in user_data[user_id]:
        user_data[user_id]["Loyalty Program's Benefits"] = text
        await message.reply("Які переваги готелів для тебе важливі? 🍽️ (Wi-Fi, Pool, Restaurant, Gym, Family)")
    elif "hotel_benefits" not in user_data[user_id]:
        user_data[user_id]["Hotels Benefits"] = text
        await message.reply("Що має бути поруч із готелем? 🏙️ (City center, Airport, Business, Nature, Shopping)")
    elif "location" not in user_data[user_id]:
        user_data[user_id]["What's near Hotels"] = text
        await message.reply("В яких країнах ти хочеш відпочивати? 🌍 (USA, Spain, UAE, Thailand, etc.)")
    elif "country" not in user_data[user_id]:
        user_data[user_id]["Country"] = text
        await message.reply("Який мінімальний рейтинг тобі підходить? ⭐ (60, 70, 80, 90)")
    elif "rating" not in user_data[user_id]:
        user_data[user_id]["Rating"] = int(text)

        results = get_best_loyalty_program(user_data[user_id])
        
        reply_text = "🏆 Найкращі програми для тебе:\n"
        for _, row in results.iterrows():
            reply_text += f"🏨 {row['Hotel Brand']} - {row['Loyalty Program']} ({row['Score']} балів)\n"

        await message.reply(reply_text)
        user_data.pop(user_id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
