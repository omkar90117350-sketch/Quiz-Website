import requests, html, random, json, re
from database.db import get_db
from config import Config

# ── Question Service ──────────────────────────────────────────────────────────

TOPIC_MAP = {
    "science":9, "history":23, "math":19, "sports":21,
    "geography":22, "music":12, "movies":11, "computers":18, "general":9,
}

def get_questions_api(topic, difficulty, amount):
    try:
        cat = TOPIC_MAP.get(topic.lower(), 9)
        r = requests.get(Config.OPEN_TRIVIA_API,
            params={"amount":amount,"category":cat,"difficulty":difficulty.lower(),"type":"multiple"},
            timeout=5)
        data = r.json()
        if data.get("response_code") != 0:
            return []
        out = []
        for item in data["results"]:
            opts = [html.unescape(o) for o in item["incorrect_answers"]]
            correct = html.unescape(item["correct_answer"])
            opts.append(correct); random.shuffle(opts)
            out.append({"question":html.unescape(item["question"]),
                "option_a":opts[0],"option_b":opts[1],"option_c":opts[2],"option_d":opts[3],
                "correct_answer":correct,"topic":topic,"difficulty":difficulty})
        return out
    except:
        return []

def get_questions_db(topic, difficulty, amount):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM questions WHERE topic LIKE ? AND difficulty=? AND active=1 ORDER BY RANDOM() LIMIT ?",
        (f"%{topic}%", difficulty, amount)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_questions(topic="general", difficulty="medium", amount=10):
    q = get_questions_api(topic, difficulty, amount)
    if len(q) < 5:
        q = get_questions_db(topic, difficulty, amount)
    if not q:
        conn = get_db()
        rows = conn.execute("SELECT * FROM questions WHERE active=1 ORDER BY RANDOM() LIMIT ?", (amount,)).fetchall()
        conn.close()
        q = [dict(r) for r in rows]
    return q[:amount]

def generate_ai_questions(topic, difficulty="medium", count=10):
    if not Config.GEMINI_API_KEY:
        return get_questions(topic, difficulty, count)
    prompt = f"""Generate {count} quiz questions about "{topic}" at {difficulty} difficulty.
Return ONLY a valid JSON array, no markdown, no explanation.
[{{"question":"...","option_a":"...","option_b":"...","option_c":"...","option_d":"...","correct_answer":"..."}}]
Rules: correct_answer must EXACTLY match one option. Make all options plausible."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={Config.GEMINI_API_KEY}"
        r = requests.post(url, headers={"Content-Type":"application/json"},
            json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=20)
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        text = re.sub(r"```(?:json)?","",text).strip()
        qs = json.loads(text)
        for q in qs:
            q["topic"] = topic; q["difficulty"] = difficulty
        return qs
    except Exception as e:
        print(f"Gemini error: {e}")
        return get_questions(topic, difficulty, count)

# ── Quiz Engine ───────────────────────────────────────────────────────────────

def calculate_score(answers, questions):
    correct = 0
    results = []
    for i, q in enumerate(questions):
        user_ans = answers.get(str(i), "")
        is_correct = user_ans.strip().lower() == q["correct_answer"].strip().lower()
        if is_correct: correct += 1
        results.append({"question":q["question"],"user_answer":user_ans,
            "correct_answer":q["correct_answer"],"is_correct":is_correct})
    return correct, results

def calculate_xp(score, total, difficulty, time_taken, streak):
    base = score * 10
    mult = {"easy":1,"medium":1.5,"hard":2}.get(difficulty,1)
    time_bonus = max(0, 50 - time_taken // 10)
    streak_bonus = streak * 5
    return int(base * mult + time_bonus + streak_bonus)

def get_badge_result(score, total, streak):
    pct = score/total if total else 0
    if pct == 1.0: return "🏆 Perfect Score","Every single answer correct!"
    elif pct >= 0.8: return "🔥 On Fire","Outstanding performance!"
    elif pct >= 0.6: return "⚡ Sharp Mind","Solid effort!"
    elif pct >= 0.4: return "📚 Scholar","Keep going!"
    else: return "🌱 Rising Star","You'll improve!"

# ── Leaderboard Service ───────────────────────────────────────────────────────

def save_score(username, score, total, topic, difficulty, xp, streak, time_taken, mode):
    conn = get_db()
    conn.execute('''INSERT INTO scores
        (username,score,total,topic,difficulty,xp_earned,streak,time_taken,mode)
        VALUES (?,?,?,?,?,?,?,?,?)''',
        (username,score,total,topic,difficulty,xp,streak,time_taken,mode))
    conn.commit(); conn.close()

def get_global_leaderboard(limit=20):
    conn = get_db()
    rows = conn.execute('''
        SELECT u.username, u.avatar_color, u.total_xp, u.level, u.quizzes_played,
               u.best_streak, MAX(s.score) as best_score
        FROM users u LEFT JOIN scores s ON u.username=s.username
        GROUP BY u.username ORDER BY u.total_xp DESC LIMIT ?''', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_topic_leaderboard(topic, limit=10):
    conn = get_db()
    rows = conn.execute('''
        SELECT username, MAX(score) as best, total, MAX(xp_earned) as xp
        FROM scores WHERE topic LIKE ? GROUP BY username ORDER BY best DESC LIMIT ?''',
        (f"%{topic}%", limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_history(username, limit=20):
    conn = get_db()
    rows = conn.execute('''SELECT * FROM scores WHERE username=?
        ORDER BY created_at DESC LIMIT ?''', (username, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_stats(username):
    conn = get_db()
    row = conn.execute('''SELECT COUNT(*) as games, SUM(xp_earned) as total_xp,
        MAX(score*1.0/total) as best_pct, AVG(score*1.0/total) as avg_pct,
        MAX(streak) as best_streak FROM scores WHERE username=?''', (username,)).fetchone()
    conn.close()
    return dict(row) if row else {}

# ── Daily Challenge ───────────────────────────────────────────────────────────
import datetime

def get_today():
    return datetime.date.today().isoformat()

def get_daily_questions():
    today = get_today()
    conn = get_db()
    row = conn.execute('SELECT questions FROM daily_challenge WHERE date=?', (today,)).fetchone()
    if row:
        conn.close()
        return json.loads(row['questions'])
    # Generate new daily questions
    qs = get_questions("general","medium",10)
    if not qs:
        conn.close(); return []
    conn.execute('INSERT OR REPLACE INTO daily_challenge (date,questions) VALUES (?,?)',
                 (today, json.dumps(qs)))
    conn.commit(); conn.close()
    return qs

def has_played_daily(username):
    today = get_today()
    conn = get_db()
    row = conn.execute('SELECT id FROM daily_scores WHERE username=? AND date=?',
                       (username, today)).fetchone()
    conn.close()
    return row is not None

def save_daily_score(username, score, total, time_taken):
    today = get_today()
    conn = get_db()
    try:
        conn.execute('INSERT INTO daily_scores (username,date,score,total,time_taken) VALUES (?,?,?,?,?)',
                     (username,today,score,total,time_taken))
        conn.commit()
    except: pass
    conn.close()

def get_daily_leaderboard():
    today = get_today()
    conn = get_db()
    rows = conn.execute('''SELECT ds.username, u.avatar_color, ds.score, ds.total, ds.time_taken
        FROM daily_scores ds LEFT JOIN users u ON ds.username=u.username
        WHERE ds.date=? ORDER BY ds.score DESC, ds.time_taken ASC LIMIT 20''', (today,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Admin ─────────────────────────────────────────────────────────────────────

def get_all_scores(limit=50):
    conn = get_db()
    rows = conn.execute('SELECT * FROM scores ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_questions():
    conn = get_db()
    rows = conn.execute('SELECT * FROM questions ORDER BY topic, difficulty').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_question(topic, difficulty, question, a, b, c, d, correct):
    conn = get_db()
    conn.execute('''INSERT INTO questions (topic,difficulty,question,option_a,option_b,option_c,option_d,correct_answer)
        VALUES (?,?,?,?,?,?,?,?)''', (topic,difficulty,question,a,b,c,d,correct))
    conn.commit(); conn.close()

def toggle_question(qid, active):
    conn = get_db()
    conn.execute('UPDATE questions SET active=? WHERE id=?', (active, qid))
    conn.commit(); conn.close()

def delete_user(username):
    conn = get_db()
    conn.execute('DELETE FROM users WHERE username=?', (username,))
    conn.execute('DELETE FROM scores WHERE username=?', (username,))
    conn.execute('DELETE FROM user_badges WHERE username=?', (username,))
    conn.commit(); conn.close()
