import random
if not user:
user = User(tg_id=tg_id, username=username)
db.add(user)
db.commit()
db.refresh(user)
else:
# Обновим username, если изменился
if username and user.username != username:
user.username = username
db.commit()
return user




def weighted_category(db: Session) -> CardCategory:
rates = db.query(DropRate).all()
# На случай пустой таблицы — подстрахуемся
if not rates:
ensure_default_drop_rates(db)
rates = db.query(DropRate).all()
cats = [r.category for r in rates]
ws = [max(r.weight, 0.0) for r in rates]
total = sum(ws)
if total <= 0:
# Если админ убил все веса, используем дефолт
cats = list(DEFAULT_RATES.keys())
ws = list(DEFAULT_RATES.values())
return random.choices(cats, weights=ws, k=1)[0]




def draw_card(db: Session, user: User) -> Tuple[Optional[Card], int]:
"""
Разыграть карту пользователю:
- Выбрать категорию по весам.
- Случайно выбрать карту из категории.
- Увеличить count в UserCard и вернуть карту и новый total_points.
Возвращает (Card | None, total_points)
"""
cat = weighted_category(db)
cards = db.query(Card).filter(Card.category == cat).all()
if not cards:
# Фолбэк: если в выбранной категории нет карточек — пробуем по порядку категорий
for fallback_cat in CATEGORY_ORDER:
cards = db.query(Card).filter(Card.category == fallback_cat).all()
if cards:
break
if not cards:
return None, 0


card = random.choice(cards)


uc = db.query(UserCard).filter_by(user_id=user.id, card_id=card.id).first()
if not uc:
uc = UserCard(user_id=user.id, card_id=card.id, count=1)
db.add(uc)
else:
uc.count += 1
db.commit()


# Посчитаем суммарные очки пользователя (учитывая дубликаты)
total_points = (
db.query(func.coalesce(func.sum(UserCard.count * Card.points), 0))
.join(Card, Card.id == UserCard.card_id)
.filter(UserCard.user_id == user.id)
.scalar()
)
return card, int(total_points)