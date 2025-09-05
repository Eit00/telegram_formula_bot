import random

# Карточки недели (пример с картинками в папке images/)
CARDS = {
    "Обычный": [
        {"name": "Стратеги Феррари", "image": "images/ferrari_strategists.jpg"},
        {"name": "Т поза", "image": "images/t_pose.jpg"},
        {"name": "Сид Ферстаппен", "image": "images/sid_verstappen.jpg"}
    ],
    "Редкий": [
        {"name": "Что такое километр?", "image": "images/what_the_fuck_is_kilometer.jpg"}
    ],
    "Эпический": [
        {"name": "Неправильный флаг", "image": "images/wrong_flag_verstappen.jpg"}
    ],
    "Легендарный": [
        {"name": "I have it printed out", "image": "images/i_have_it_printed_out.gif"}
    ]
}

POINTS = {
    "Обычный": 1000,
    "Редкий": 3000,
    "Эпический": 5000,
    "Легендарный": 10000
}

def roll_card():
    rarity = random.choices(
        ["Обычный", "Редкий", "Эпический", "Легендарный"],
        weights=[70, 20, 9, 1],
        k=1
    )[0]

    card = random.choice(CARDS[rarity])
    points = POINTS[rarity]
    coins = random.randint(1, 3)
    return rarity, card, points, coins
