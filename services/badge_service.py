from database.db import get_db

ALL_BADGES = {
    'first_quiz':    {'icon':'🎯','name':'First Blood',      'desc':'Complete your first quiz'},
    'perfect_score': {'icon':'💎','name':'Diamond Mind',     'desc':'Get 100% on any quiz'},
    'streak_5':      {'icon':'🔥','name':'On Fire',          'desc':'Get a 5-answer streak'},
    'streak_10':     {'icon':'⚡','name':'Lightning',        'desc':'Get a 10-answer streak'},
    'hard_mode':     {'icon':'💀','name':'Skull Crusher',    'desc':'Complete a Hard quiz'},
    'speed_demon':   {'icon':'🚀','name':'Speed Demon',      'desc':'Finish a quiz in under 60s'},
    'scholar':       {'icon':'📚','name':'Scholar',          'desc':'Play 10 quizzes'},
    'master':        {'icon':'🏆','name':'Quiz Master',      'desc':'Play 25 quizzes'},
    'ai_explorer':   {'icon':'🤖','name':'AI Explorer',      'desc':'Complete an AI-generated quiz'},
    'daily_hero':    {'icon':'📅','name':'Daily Hero',       'desc':'Complete the daily challenge'},
    'daily_streak3': {'icon':'🗓️','name':'Consistent',       'desc':'Complete daily challenge 3 days in a row'},
    'top3':          {'icon':'🥇','name':'Podium',           'desc':'Reach top 3 on any leaderboard'},
    'level5':        {'icon':'⭐','name':'Rising Star',      'desc':'Reach Level 5'},
    'level10':       {'icon':'👑','name':'Omniscient',       'desc':'Reach Level 10'},
    'xp1000':        {'icon':'💫','name':'XP Hunter',        'desc':'Earn 1000 total XP'},
}

def award_badge(username, badge_id):
    if badge_id not in ALL_BADGES:
        return False
    conn = get_db()
    try:
        conn.execute('INSERT OR IGNORE INTO user_badges (username, badge_id) VALUES (?,?)',
                     (username, badge_id))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def get_user_badges(username):
    conn = get_db()
    rows = conn.execute('SELECT badge_id, earned_at FROM user_badges WHERE username=? ORDER BY earned_at DESC',
                        (username,)).fetchall()
    conn.close()
    earned_ids = {r['badge_id'] for r in rows}
    result = []
    for bid, info in ALL_BADGES.items():
        result.append({
            'id': bid,
            'icon': info['icon'],
            'name': info['name'],
            'desc': info['desc'],
            'earned': bid in earned_ids,
        })
    return result

def check_and_award_badges(username, score, total, difficulty, time_taken, streak, mode, user):
    new_badges = []
    def award(bid):
        if award_badge(username, bid):
            new_badges.append(ALL_BADGES[bid])

    if user['quizzes_played'] == 0:
        award('first_quiz')
    if score == total:
        award('perfect_score')
    if streak >= 5:
        award('streak_5')
    if streak >= 10:
        award('streak_10')
    if difficulty == 'hard':
        award('hard_mode')
    if time_taken < 60:
        award('speed_demon')
    if user['quizzes_played'] >= 9:
        award('scholar')
    if user['quizzes_played'] >= 24:
        award('master')
    if mode == 'ai':
        award('ai_explorer')
    if user['level'] >= 5:
        award('level5')
    if user['level'] >= 10:
        award('level10')
    if user['total_xp'] >= 1000:
        award('xp1000')

    return new_badges
