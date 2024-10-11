import sqlite3
import logging
import time

logger = logging.getLogger(__name__)


def initialize_database():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            free_interactions_used INTEGER NOT NULL DEFAULT 0,
            indecent_credits INTEGER NOT NULL DEFAULT 0,
            llm TEXT NOT NULL DEFAULT 'Indecent',  -- Added column for LLM
            voice_id TEXT NOT NULL DEFAULT 'PB6BdkFkZLbI39GHdnbQ'  -- Default Voice (Natasha by default)
        )
    ''')

    # Create payments table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            payment_id TEXT NOT NULL,
            credits INTEGER NOT NULL,
            timestamp INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    logger.debug("Database initialized.")


def get_user(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT free_interactions_used, indecent_credits, llm, voice_id FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if row:
        user = {
            'free_interactions_used': row[0],
            'indecent_credits': row[1],
            'llm': row[2],
            'voice_id': row[3]
        }
    else:
        cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
        conn.commit()
        user = {
            'free_interactions_used': 0,
            'indecent_credits': 0,
            'llm': 'Indecent',  # Default LLM
            'voice_id': 'PB6BdkFkZLbI39GHdnbQ'  # Default to Natasha character's voice
        }
    conn.close()
    logger.debug(f"Retrieved user {user_id}: {user}")
    return user


def update_user(user_id, **kwargs):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values())
    values.append(user_id)
    cursor.execute(f'UPDATE users SET {fields} WHERE user_id = ?', values)
    conn.commit()
    conn.close()
    logger.debug(f"Updated user {user_id}: {kwargs}")


def add_credits(user_id, credits):
    user = get_user(user_id)
    new_credits = user['indecent_credits'] + credits
    update_user(user_id, indecent_credits=new_credits)
    logger.debug(
        f"Added {credits} credits to user {user_id}. New balance: {new_credits}")


def increment_free_interactions(user_id):
    """Increment the count of free interactions used by the user."""
    try:
        user = get_user(user_id)
        new_free = user['free_interactions_used'] + 1
        update_user(user_id, free_interactions_used=new_free)
        logger.debug(
            f"Incremented free interactions for user {user_id}. Total used: {new_free}")
        return new_free
    except Exception as e:
        logger.exception(
            f"Error in increment_free_interactions for user {user_id}: {e}")
        raise


def store_payment_id(user_id, payment_id, credits):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO payments (user_id, payment_id, credits, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, payment_id, credits, int(time.time())))
    conn.commit()
    conn.close()
    logger.debug(f"Stored payment ID {payment_id} for user {user_id}")