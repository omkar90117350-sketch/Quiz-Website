def get_topic_leaderboard(topic, limit=10):
    conn = get_db()
    # Use GROUP BY username to ensure unique entries
    # Use MAX(score) to get their highest achievement
    rows = conn.execute('''
        SELECT 
            username, 
            MAX(score) as best, 
            total, 
            MAX(xp_earned) as xp,
            MAX(date) as last_played
        FROM scores 
        WHERE topic LIKE ? 
        GROUP BY username 
        ORDER BY best DESC, xp DESC 
        LIMIT ?''',
        (f"%{topic}%", limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
