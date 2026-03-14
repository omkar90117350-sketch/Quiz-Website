# ⚡ QUIZR SaaS — God-Level Quiz Platform

A full SaaS-style quiz application with unique user profiles, XP system,
daily challenges, topic leaderboards, badge collection, and admin panel.

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
python app.py
# Open → http://localhost:5000
```

---

## 🔑 Enable Free AI Questions (Gemini)

1. Go to **https://aistudio.google.com/apikey**
2. Sign in with Google → Create API Key → Copy it
3. Open `config.py` and paste your key:

```python
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'PASTE_YOUR_KEY_HERE')
```

---

## 🛡️ Admin Panel

Go to **http://localhost:5000/admin**
Default password: `admin123`

Change it in `config.py`:
```python
ADMIN_PASSWORD = 'your_new_password'
```

Admin features:
- View all users + delete accounts
- View all scores
- Add / hide / show questions
- Platform overview stats

---

## 🎮 Features

| Feature | Details |
|---|---|
| 👤 Unique Profiles | Pick username + avatar color. Stored permanently. |
| ⚡ XP + Levels | 10 levels from Rookie → Omniscient |
| 🔥 Streaks | Consecutive correct answers, bonus XP |
| ⏱ Timer | 20s animated SVG countdown per question |
| 📅 Daily Challenge | Same 10 questions for everyone, resets midnight |
| 🎖 Badges | 15 earnable badges for achievements |
| 🏆 Leaderboard | Global XP ranks + per-topic best scores |
| 📊 Dashboard | Personal stats, XP chart, quiz history |
| 🤖 AI Mode | Gemini generates questions on ANY topic |
| 🌐 Trivia DB | Free Open Trivia DB API fallback |
| 🎵 Sounds | Chimes on correct, tones on wrong, ambient music |
| 🎊 Confetti | Burst animation on 70%+ scores |
| 🛡️ Admin Panel | Manage users, scores, questions |
| 5/10/15 Questions | User chooses quiz length |

---

## 🗂 Project Structure

```
quizr_saas/
├── app.py                    ← Flask server, all routes
├── config.py                 ← Settings, API keys, admin password
├── requirements.txt
├── database/
│   ├── db.py                 ← SQLite connection
│   └── init_db.py            ← Tables + seed questions
├── services/
│   ├── user_service.py       ← Profile creation, XP, levels
│   ├── badge_service.py      ← 15 badges, award logic
│   └── quiz_service.py       ← Questions, scoring, leaderboard, daily
├── static/
│   ├── css/
│   │   ├── base.css          ← Full cyberpunk theme
│   │   └── quiz.css          ← Quiz UI components
│   └── js/
│       ├── effects.js        ← Particles, sounds, confetti, music
│       └── quiz.js           ← Quiz engine controller
└── templates/
    ├── base.html             ← Shared navbar layout
    ├── index.html            ← Landing + profile creation
    ├── home.html             ← User home dashboard
    ├── play.html             ← Quiz setup
    ├── quiz.html             ← Quiz interface
    ├── result.html           ← Score + badges result
    ├── dashboard.html        ← Personal stats + XP chart
    ├── badges.html           ← Badge collection
    ├── leaderboard.html      ← Global + topic leaderboards
    ├── daily.html            ← Daily challenge
    ├── admin_login.html      ← Admin login
    └── admin.html            ← Admin panel
```

---

## 🚀 Deploy Free Online (Railway)

1. Create account at **railway.app**
2. Click "New Project" → "Deploy from GitHub"
3. Push this folder to GitHub first, then connect
4. Add environment variable: `GEMINI_API_KEY=your_key`
5. Done — live URL in 2 minutes!

---

**Level: 9/10 — SaaS Ready** 🚀
