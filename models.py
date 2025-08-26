import enum
rare = "rare" # Редкий
epic = "epic" # Эпический
mythic = "mythic" # Мифический
legendary = "legendary" # Легендарный


CATEGORY_DISPLAY = {
CardCategory.common: "Обычный",
CardCategory.rare: "Редкий",
CardCategory.epic: "Эпический",
CardCategory.mythic: "Мифический",
CardCategory.legendary: "Легендарный",
}


class User(Base):
__tablename__ = "users"
id = Column(Integer, primary_key=True)
tg_id = Column(Integer, unique=True, index=True, nullable=False)
username = Column(String, nullable=True)
joined_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)


cards = relationship("UserCard", back_populates="user", cascade="all, delete-orphan")


class Card(Base):
__tablename__ = "cards"
id = Column(Integer, primary_key=True)
name = Column(String, unique=True, nullable=False)
category = Column(Enum(CardCategory), index=True, nullable=False)
points = Column(Integer, nullable=False, default=1)


owners = relationship("UserCard", back_populates="card", cascade="all, delete-orphan")


class UserCard(Base):
__tablename__ = "user_cards"
id = Column(Integer, primary_key=True)
user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
card_id = Column(Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)
count = Column(Integer, nullable=False, default=0)


user = relationship("User", back_populates="cards")
card = relationship("Card", back_populates="owners")


__table_args__ = (
UniqueConstraint("user_id", "card_id", name="uq_user_card"),
)


class DropRate(Base):
__tablename__ = "drop_rates"
id = Column(Integer, primary_key=True)
category = Column(Enum(CardCategory), unique=True, nullable=False)
weight = Column(Float, nullable=False, default=0.0) # Вес вероятности (не обязательно нормализован)