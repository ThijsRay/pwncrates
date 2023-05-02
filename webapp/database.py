"""
This file serves as the primary interface between the database and the rest of the code.

Sticking to this convention allows us to easily modify or switch the database without performing shotgun surgery.
"""
import mysql.connector
import time

config = {
    'user': 'root',
    'password': 'root',
    'host': 'db',
    'port': '3306',
    'database': 'pwncrates'
}


def get_users():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM users')
    results = [name for name in cursor]
    cursor.close()
    connection.close()

    return results


def get_username(user_id) -> str:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM users WHERE id = %s LIMIT 1', (user_id,))
    results = [user_id[0] for user_id in cursor]
    cursor.close()
    connection.close()

    if len(results) == 0:
        return ""

    return results[0]


def get_password(user_name) -> str:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT password FROM users WHERE name = %s LIMIT 1', (user_name,))
    results = [password_hash[0] for password_hash in cursor]
    cursor.close()
    connection.close()

    if len(results) == 0:
        return ""

    return results[0]


def get_id(user_name) -> str:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM users WHERE name = %s LIMIT 1', (user_name,))
    results = [password_hash[0] for password_hash in cursor]
    cursor.close()
    connection.close()

    if len(results) == 0:
        return ""

    return results[0]


def register_user(user_name, password):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('INSERT INTO users (name, password) VALUES (%s, %s)', (user_name, password))
    connection.commit()
    cursor.close()
    connection.close()
    return


def get_challenges(category, difficulty="hard"):
    difficulties = {
        "easy": 1,
        "medium": 2,
        "hard": 3
    }
    # Translate the difficulty to int
    difficulty = difficulties[difficulty.lower()]

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT id, name, description, points, subcategory FROM challenges '
                   'WHERE category = %s AND difficulty <= %s',
                   (category, difficulty))
    results = {}
    for (id, name, description, points, subcategory) in cursor:
        if subcategory in results.keys():
            results[subcategory].append((id, name, description, points))
        else:
            results[subcategory] = [(id, name, description, points)]
    cursor.close()
    connection.close()

    return results


def get_categories():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT category FROM challenges;')
    results = [category[0] for category in cursor]
    cursor.close()
    connection.close()

    return results


def submit_flag(challenge_id, flag, user_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT flag FROM challenges WHERE id = %s AND flag = %s;', (challenge_id, flag))

    if cursor.fetchone():
        cursor.execute('SELECT id FROM solves WHERE challenge_id = %s AND user_id = %s;', (challenge_id, user_id))
        if cursor.fetchone():
            ret = "Already solved"
        else:
            cursor.execute('INSERT INTO solves (challenge_id, solved_time, user_id) VALUES (%s, %s, %s);',
                           (challenge_id, int(time.time()), user_id))
            cursor.execute('UPDATE challenges SET solves = solves + 1 WHERE id = %s', (challenge_id,))
            cursor.execute('UPDATE users U SET U.points = U.points + '
                           '(SELECT points FROM challenges WHERE id = %s) '
                           'WHERE id = %s', (challenge_id, user_id))
            connection.commit()
            ret = "OK"
    else:
        ret = "Incorrect flag"

    cursor.close()
    connection.close()

    return ret


def get_scoreboard():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT name, points FROM users ORDER BY points DESC;')
    results = [user for user in cursor]
    cursor.close()
    connection.close()

    return results


def get_solves(user_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT challenge_id FROM solves WHERE user_id = %s;', (user_id,))
    results = [challenge_id[0] for challenge_id in cursor]
    cursor.close()
    connection.close()

    return results


def get_writeups(challenge_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT U.name, W.id FROM writeups W, users U '
                   'WHERE W.challenge_id = %s AND W.user_id = U.id;', (challenge_id,))
    results = [(name, writeup_id) for name, writeup_id in cursor]
    cursor.close()
    connection.close()

    return results


def get_writeup_file(challenge_id, writeup_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT file_name FROM writeups '
                   'WHERE challenge_id = %s AND id = %s;', (challenge_id, writeup_id))
    results = [filename[0] for filename in cursor]
    cursor.close()
    connection.close()

    return results


def get_challenge_name(challenge_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM challenges '
                   'WHERE id = %s;', (challenge_id,))
    results = [filename[0] for filename in cursor]
    cursor.close()
    connection.close()

    return results
