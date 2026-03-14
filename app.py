from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from config import Config
from database.init_db import init_db
from services.user_service import (username_exists, create_user, get_user,
    update_user_xp, get_level_title, AVATAR_COLORS, get_all_users)
from services.badge_service import check_and_award_badges, get_user_badges
from services.quiz_service import (
    get_questions, generate_ai_questions, calculate_score, calculate_xp,
    get_badge_result, save_score, get_global_leaderboard, get_topic_leaderboard,
    get_user_history, get_user_stats, get_daily_questions, has_played_daily,
    save_daily_score, get_daily_leaderboard, get_all_scores, get_all_questions,
    add_question, toggle_question, delete_user
)
import json, time, functools

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

with app.app_context():
    init_db()

# ── Auth helpers ──────────────────────────────────────────────────────────────

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('username'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ── Public pages ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if session.get('username'):
        return redirect(url_for('home'))
    return render_template('index.html', colors=AVATAR_COLORS)

@app.route('/create-profile', methods=['POST'])
def create_profile():
    username = request.form.get('username','').strip()
    avatar_color = request.form.get('avatar_color', '#00f5ff')
    if not username or len(username) < 2:
        return render_template('index.html', colors=AVATAR_COLORS,
            error="Username must be at least 2 characters.")
    if len(username) > 20:
        return render_template('index.html', colors=AVATAR_COLORS,
            error="Username must be under 20 characters.")
    ok, msg = create_user(username, avatar_color)
    if not ok:
        return render_template('index.html', colors=AVATAR_COLORS, error=msg)
    session['username'] = username
    return redirect(url_for('home'))

@app.route('/join', methods=['POST'])
def join():
    username = request.form.get('username','').strip()
    if not username_exists(username):
        return render_template('index.html', colors=AVATAR_COLORS,
            error=f"Username '{username}' not found. Create a profile first.")
    session['username'] = username
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── Main app pages ────────────────────────────────────────────────────────────

@app.route('/home')
@login_required
def home():
    user = get_user(session['username'])
    return render_template('home.html', user=user,
        level_title=get_level_title(user['level']))

@app.route('/play')
@login_required
def play():
    user = get_user(session['username'])
    return render_template('play.html', user=user)

@app.route('/quiz')
@login_required
def quiz():
    topic = request.args.get('topic', 'general')
    difficulty = request.args.get('difficulty', 'medium')
    amount = int(request.args.get('amount', 10))
    mode = request.args.get('mode', 'trivia')
    amount = min(max(amount, 5), 15)

    if mode == 'ai':
        questions = generate_ai_questions(topic, difficulty, amount)
    else:
        questions = get_questions(topic, difficulty, amount)

    if not questions:
        return redirect(url_for('play'))

    session['questions'] = questions
    session['topic'] = topic
    session['difficulty'] = difficulty
    session['mode'] = mode
    session['start_time'] = int(time.time())

    user = get_user(session['username'])
    return render_template('quiz.html', total=len(questions), topic=topic,
        difficulty=difficulty, user=user, mode=mode)

@app.route('/result', methods=['POST'])
@login_required
def result():
    answers = request.form.to_dict()
    questions = session.get('questions', [])
    topic = session.get('topic', 'general')
    difficulty = session.get('difficulty', 'medium')
    mode = session.get('mode', 'trivia')
    username = session['username']
    time_taken = int(time.time()) - session.get('start_time', int(time.time()))

    score, results = calculate_score(answers, questions)
    streak = sum(1 for r in results if r['is_correct'])
    xp = calculate_xp(score, len(questions), difficulty, time_taken, streak)
    badge, badge_desc = get_badge_result(score, len(questions), streak)

    user = get_user(username)
    save_score(username, score, len(questions), topic, difficulty, xp, streak, time_taken, mode)
    update_user_xp(username, xp, streak)
    user_updated = get_user(username)
    new_badges = check_and_award_badges(username, score, len(questions),
        difficulty, time_taken, streak, mode, user)

    return render_template('result.html',
        score=score, total=len(questions), results=results,
        topic=topic, difficulty=difficulty, user=user_updated,
        xp=xp, level=user_updated['level'],
        title=get_level_title(user_updated['level']),
        badge=badge, badge_desc=badge_desc,
        time_taken=time_taken, streak=streak,
        new_badges=new_badges)

@app.route('/dashboard')
@login_required
def dashboard():
    username = session['username']
    user = get_user(username)
    history = get_user_history(username)
    badges = get_user_badges(username)
    stats = get_user_stats(username)
    xp_data = [{'quiz': i+1, 'xp': h['xp_earned']} for i, h in enumerate(reversed(history[-10:]))]
    return render_template('dashboard.html', user=user,
        history=history, badges=badges, stats=stats,
        xp_data=json.dumps(xp_data),
        level_title=get_level_title(user['level']))

@app.route('/badges')
@login_required
def badges():
    username = session['username']
    user = get_user(username)
    all_badges = get_user_badges(username)
    earned = [b for b in all_badges if b['earned']]
    locked = [b for b in all_badges if not b['earned']]
    return render_template('badges.html', user=user, earned=earned, locked=locked,
        level_title=get_level_title(user['level']))

@app.route('/leaderboard')
@login_required
def leaderboard():
    user = get_user(session['username'])
    global_lb = get_global_leaderboard()
    topics = ['Python','Science','History','Space','AI','Math','General']
    topic_data = {}
    for t in topics:
        topic_data[t] = get_topic_leaderboard(t, 5)
    return render_template('leaderboard.html', user=user,
        global_lb=global_lb, topic_data=topic_data, topics=topics,
        level_title=get_level_title(user['level']))

@app.route('/daily')
@login_required
def daily():
    username = session['username']
    user = get_user(username)
    already_played = has_played_daily(username)
    daily_lb = get_daily_leaderboard()
    if already_played:
        return render_template('daily.html', user=user, already_played=True,
            daily_lb=daily_lb, level_title=get_level_title(user['level']))
    questions = get_daily_questions()
    session['daily_questions'] = questions
    session['daily_start'] = int(time.time())
    return render_template('daily.html', user=user, already_played=False,
        total=len(questions), daily_lb=daily_lb,
        level_title=get_level_title(user['level']))

@app.route('/daily/submit', methods=['POST'])
@login_required
def daily_submit():
    username = session['username']
    if has_played_daily(username):
        return redirect(url_for('daily'))
    answers = request.form.to_dict()
    questions = session.get('daily_questions', [])
    time_taken = int(time.time()) - session.get('daily_start', int(time.time()))
    score, _ = calculate_score(answers, questions)
    save_daily_score(username, score, len(questions), time_taken)
    xp = calculate_xp(score, len(questions), 'medium', time_taken, 0)
    update_user_xp(username, xp, 0)
    return redirect(url_for('daily'))

# ── Admin ─────────────────────────────────────────────────────────────────────

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == Config.ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html', error="Wrong password")
    return render_template('admin_login.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    users = get_all_users()
    scores = get_all_scores()
    questions = get_all_questions()
    return render_template('admin.html', users=users, scores=scores, questions=questions)

@app.route('/admin/add-question', methods=['POST'])
@admin_required
def admin_add_question():
    add_question(
        request.form['topic'], request.form['difficulty'],
        request.form['question'], request.form['option_a'],
        request.form['option_b'], request.form['option_c'],
        request.form['option_d'], request.form['correct_answer']
    )
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle-question/<int:qid>/<int:active>')
@admin_required
def admin_toggle_question(qid, active):
    toggle_question(qid, active)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-user/<username>')
@admin_required
def admin_delete_user(username):
    delete_user(username)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

# ── API endpoints ─────────────────────────────────────────────────────────────

@app.route('/quiz/questions')
@login_required
def quiz_questions():
    """Return session questions as JSON for the quiz JS."""
    return jsonify(session.get('questions', []))

@app.route('/api/check-username')
def api_check_username():
    username = request.args.get('username','')
    return jsonify({'available': not username_exists(username)})

@app.route('/api/leaderboard')
def api_leaderboard():
    return jsonify(get_global_leaderboard())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
