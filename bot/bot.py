import asyncio
Base.metadata.create_all(bind=engine)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
with SessionLocal() as db:
user = get_or_create_user(db, message.from_user.id, message.from_user.username)
await message.answer(
"Привет! Это бот розыгрыша карточек. Нажми /roll чтобы испытать удачу!"
)


@dp.message(Command("roll"))
async def cmd_roll(message: types.Message):
with SessionLocal() as db:
user = get_or_create_user(db, message.from_user.id, message.from_user.username)
card, total = draw_card(db, user)
if not card:
await message.answer("Пока нет доступных карточек. Админ ещё не добавил коллекцию.")
return
await message.answer(
f"🎟️ Выпала карточка: <b>{card.name}</b> (категория: {CATEGORY_DISPLAY[card.category]})\n"
f"💯 Твои очки: {total}",
parse_mode="HTML",
)


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
from sqlalchemy import func
from models import UserCard, Card
with SessionLocal() as db:
user = get_or_create_user(db, message.from_user.id, message.from_user.username)
total = (
db.query(func.coalesce(func.sum(UserCard.count * Card.points), 0))
.join(Card, Card.id == UserCard.card_id)
.filter(UserCard.user_id == user.id)
.scalar()
)
# Сводка по категориям
rows = (
db.query(Card.category, func.count(UserCard.id), func.coalesce(func.sum(UserCard.count), 0))
.join(Card, Card.id == UserCard.card_id)
.filter(UserCard.user_id == user.id)
.group_by(Card.category)
.all()
)
lines = [f"Всего очков: {int(total)}"]
if rows:
lines.append("По категориям:")
for cat, unique_cnt, total_cnt in rows:
lines.append(f"• {CATEGORY_DISPLAY[cat]} — уникальных: {unique_cnt}, всего: {total_cnt}")
else:
lines.append("Коллекция пока пуста.")
await message.answer("\n".join(lines))


async def main():
await dp.start_polling(bot)


if __name__ == "__main__":
asyncio.run(main())