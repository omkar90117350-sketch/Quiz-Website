def get_topic_leaderboard(topic, limit=10):
    conn = get_db()
    rows = conn.execute('''
        SELECT id, username, score as best, total, xp_earned as xp
        FROM scores WHERE topic LIKE ? ORDER BY score DESC LIMIT ?''',
        (f"%{topic}%", limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
