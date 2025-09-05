from aiogram import Bot, Dispatcher, types, filters
from aiogram.utils import executor
from config import BOT_TOKEN, TRIGGER_MESSAGE
from database import init_db, add_user, update_user, add_card, get_user_info, get_global_top, get_chat_top, get_user_rank_global, get_user_rank_chat, can_roll
from cards import roll_card
from aiogram.types import BotCommand


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

init_db()


@dp.message_handler(commands=["collection"])
async def show_collection(message: types.Message):
    user_id = message.from_user.id
    user, cards = get_user_info(user_id)

    if not user:
        await message.reply("У вас пока нет карточек. Попробуйте выбить их с помощью команды '!карточка' 🎴")
        return

    points, coins = user
    if cards:
        cards_list = "\n".join([f"• {c}" for c in cards])
    else:
        cards_list = "— пока пусто —"

    await message.reply(
        f"📊 Ваша коллекция:\n\n"
        f"⭐ Очки: {points}\n"
        f"💰 Монеты: {coins}\n\n"
        f"🎴 Карточки:\n{cards_list}"
    )
            

@dp.message_handler(commands=["top"])
async def global_top(message: types.Message):
    user_id = message.from_user.id
    top = get_global_top(limit=10)
    rank, points = get_user_rank_global(user_id)

    if not top:
        await message.reply("📊 Глобальный топ пока пуст!")
        return

    text = "🌍 Глобальный топ игроков:\n\n"
    for i, (first_name, username, points_top) in enumerate(top, start=1):
        name = f"@{username}" if username else first_name
        text += f"{i}. {name} — {points_top} очков\n"

    # твоя позиция
    if points > 0:
        text += f"\n📈 Ваша позиция: {rank}-е место ({points} очков)"
    else:
        text += "\n📈 У вас пока нет очков."

    await message.reply(text)


@dp.message_handler(commands=["chattop"])
async def chat_top(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    top = get_chat_top(chat_id, limit=10)
    rank, points = get_user_rank_chat(user_id, chat_id)

    if not top:
        await message.reply("📊 В этом чате ещё никто не выбивал карточки!")
        return

    text = "💬 Топ игроков чата:\n\n"
    for i, (first_name, username, points_top) in enumerate(top, start=1):
        name = f"@{username}" if username else first_name
        text += f"{i}. {name} — {points_top} очков\n"

    # твоя позиция
    if points > 0:
        text += f"\n📈 Ваша позиция в чате: {rank}-е место ({points} очков)"
    else:
        text += "\n📈 У вас пока нет очков в этом чате."

    await message.reply(text)

    
@dp.message_handler(commands=["mytop"])
async def my_top(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    global_rank, global_points = get_user_rank_global(user_id)
    chat_rank, chat_points = get_user_rank_chat(user_id, chat_id)

    if global_points == 0:
        await message.reply("📊 У вас пока нет очков. Попробуйте выбить карточку через '!карточка' 🎴")
        return

    text = (f"📈 Ваш рейтинг:\n\n"
            f"🌍 Глобально: {global_rank}-е место ({global_points} очков)\n"
            f"💬 В этом чате: {chat_rank}-е место ({chat_points} очков)")
    
    await message.reply(text)
    
@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    text = (
        "🤖 Доступные команды:\n\n"
        "🎴 !карточка — выбить случайную карточку\n"
        "📂 /коллекция — показать вашу коллекцию карточек\n"
        "🌍 /топ — глобальный топ игроков\n"
        "💬 /топчата — топ игроков в этом чате\n"
        "📈 /мойтоп — ваше место в рейтингах\n"
        "ℹ️ /help — показать список команд\n"
    )
    await message.reply(text)
    
@dp.message_handler(commands=["memocard"])
@dp.message_handler(filters.Text(equals=["!мемокарта"]))
async def card_drop(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    username = message.from_user.username

    # проверка кулдауна
    allowed, wait_time = can_roll(user_id)
    if not allowed:
        hours = wait_time // 3600
        minutes = (wait_time % 3600) // 60
        await message.reply(f"⏳ Вы уже выбивали карточку недавно!\nПопробуйте снова через {hours} ч {minutes} мин.")
        return

    add_user(user_id, chat_id, first_name, username)

    rarity, card, points, coins = roll_card()
    new = add_card(user_id, card["name"])

    caption_new = (
        f"🎉 Вам выпала {rarity} карточка:\n<b>{card['name']}</b>\n"
        f"+{points} очков, +{coins} монет 💰"
    )
    caption_repeat = (
        f"🔁 Повторка: {rarity} карточка <b>{card['name']}</b>\n"
        f"+{points} очков, +{coins+1} монет 💰"
    )

    if new:
        update_user(user_id, points, coins)
        caption = caption_new
    else:
        update_user(user_id, points, coins + 1)
        caption = caption_repeat

    file_path = card["image"].lower()

    if file_path.endswith(".gif"):
        with open(card["image"], "rb") as anim:
            await bot.send_animation(chat_id=chat_id, animation=anim, caption=caption, parse_mode="HTML")

    elif file_path.endswith(".webp"):
        with open(card["image"], "rb") as sticker:
            await bot.send_sticker(chat_id=chat_id, sticker=sticker)
        await bot.send_message(chat_id=chat_id, text=caption, parse_mode="HTML")

    elif file_path.endswith((".mp4", ".mov", ".avi", ".webm")):
        with open(card["image"], "rb") as video:
            await bot.send_video(chat_id=chat_id, video=video, caption=caption, parse_mode="HTML")

    else:
        with open(card["image"], "rb") as photo:
            await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, parse_mode="HTML")



    
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="memocard", description="Выбить случайную карточку 🎴"),
        BotCommand(command="collection", description="Ваша коллекция карточек"),
        BotCommand(command="top", description="Глобальный топ игроков"),
        BotCommand(command="chattop", description="Топ игроков в этом чате"),
        BotCommand(command="mytop", description="Ваше место в рейтингах"),
        BotCommand(command="help", description="Показать список команд"),
    ]
    await bot.set_my_commands(commands)



    
if __name__ == "__main__":
    from aiogram import executor

    async def on_startup(dp):
        await set_commands(bot)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
