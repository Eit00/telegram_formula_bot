import pymysql
import time

DB_CONFIG = {
    "host": "localhost",
    "user": "root",       # замени
    "password": "zaqzaq12", # замени
    "database": "f1_cards",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.Cursor
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Таблица пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            first_name VARCHAR(255),
            username VARCHAR(255),
            points INT DEFAULT 0,
            coins INT DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Таблица карточек
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_cards (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT,
            card_name VARCHAR(255),
            UNIQUE(user_id, card_name),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Кулдаун
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cooldowns (
            user_id BIGINT PRIMARY KEY,
            last_time BIGINT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Чаты
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_chats (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT,
            chat_id BIGINT,
            UNIQUE(user_id, chat_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()
    conn.close()


def add_user(user_id, chat_id, first_name, username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (user_id, first_name, username)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE first_name=VALUES(first_name), username=VALUES(username)
    """, (user_id, first_name, username))
    cur.execute("""
        INSERT IGNORE INTO user_chats (user_id, chat_id)
        VALUES (%s, %s)
    """, (user_id, chat_id))
    conn.commit()
    conn.close()


def update_user(user_id, points, coins):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users SET points = points + %s, coins = coins + %s WHERE user_id = %s
    """, (points, coins, user_id))
    conn.commit()
    conn.close()


def add_card(user_id, card_name):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO user_cards (user_id, card_name) VALUES (%s, %s)
        """, (user_id, card_name))
        conn.commit()
        new = True
    except pymysql.err.IntegrityError:
        new = False
    conn.close()
    return new


def get_user_info(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT points, coins FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.execute("SELECT card_name FROM user_cards WHERE user_id = %s", (user_id,))
    cards = [row[0] for row in cur.fetchall()]
    conn.close()
    return user, cards


def get_global_top(limit=10):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT first_name, username, points FROM users ORDER BY points DESC LIMIT %s
    """, (limit,))
    top = cur.fetchall()
    conn.close()
    return top


def get_chat_top(chat_id, limit=10):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.first_name, u.username, u.points
        FROM users u
        JOIN user_chats uc ON u.user_id = uc.user_id
        WHERE uc.chat_id = %s
        ORDER BY u.points DESC
        LIMIT %s
    """, (chat_id, limit))
    top = cur.fetchall()
    conn.close()
    return top


def get_user_rank_global(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) + 1
        FROM users
        WHERE points > (SELECT points FROM users WHERE user_id = %s)
    """, (user_id,))
    rank = cur.fetchone()[0]
    cur.execute("SELECT points FROM users WHERE user_id = %s", (user_id,))
    points = cur.fetchone()
    conn.close()
    return rank, points[0] if points else 0


def get_user_rank_chat(user_id, chat_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) + 1
        FROM users u
        JOIN user_chats uc ON u.user_id = uc.user_id
        WHERE uc.chat_id = %s
          AND u.points > (SELECT points FROM users WHERE user_id = %s)
    """, (chat_id, user_id))
    rank = cur.fetchone()[0]
    cur.execute("SELECT points FROM users WHERE user_id = %s", (user_id,))
    points = cur.fetchone()
    conn.close()
    return rank, points[0] if points else 0


def can_roll(user_id, cooldown_seconds=14400):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT last_time FROM cooldowns WHERE user_id=%s", (user_id,))
    row = cur.fetchone()

    now = int(time.time())

    if row:
        last_time = row[0]
        if now - last_time < cooldown_seconds:
            conn.close()
            return False, cooldown_seconds - (now - last_time)
        else:
            cur.execute("UPDATE cooldowns SET last_time=%s WHERE user_id=%s", (now, user_id))
    else:
        cur.execute("INSERT INTO cooldowns (user_id, last_time) VALUES (%s, %s)", (user_id, now))

    conn.commit()
    conn.close()
    return True, 0
