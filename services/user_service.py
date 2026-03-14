from database.db import get_db

AVATAR_COLORS = [
    '#00f5ff','#bf00ff','#ffd700','#39ff14',
    '#ff006e','#00ff88','#ff6b35','#4cc9f0'
]

def username_exists(username):
    conn = get_db()
    row = conn.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone()
    conn.close()
    return row is not None

def create_user(username, avatar_color):
    conn = get_db()
    try:
        conn.execute('INSERT INTO users (username, avatar_color) VALUES (?,?)',
                     (username, avatar_color))
        conn.commit()
        conn.close()
        return True, "Profile created!"
    except Exception as e:
        conn.close()
        return False, "Username already taken!"

def get_user(username):
    conn = get_db()
    row = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_user_xp(username, xp_earned, streak):
    conn = get_db()
    c = conn.cursor()
    user = c.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    if user:
        new_xp = user['total_xp'] + xp_earned
        new_level = get_level_from_xp(new_xp)
        best_streak = max(user['best_streak'], streak)
        c.execute('''UPDATE users SET total_xp=?, level=?, quizzes_played=quizzes_played+1,
                     best_streak=? WHERE username=?''',
                  (new_xp, new_level, best_streak, username))
        conn.commit()
    conn.close()

def get_level_from_xp(xp):
    thresholds = [0,100,300,600,1000,1500,2200,3000,4000,5500,7500]
    for i in range(len(thresholds)-1, -1, -1):
        if xp >= thresholds[i]:
            return i + 1
    return 1

def get_level_title(level):
    titles = ["Rookie","Apprentice","Explorer","Scholar","Expert",
              "Master","Grandmaster","Legend","Mythic","Godlike","Omniscient"]
    return titles[min(level-1, len(titles)-1)]

def get_all_users(limit=100):
    conn = get_db()
    rows = conn.execute('SELECT * FROM users ORDER BY total_xp DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
