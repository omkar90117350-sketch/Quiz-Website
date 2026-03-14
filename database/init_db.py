import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db import get_db

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Users (unique username profiles)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        avatar_color TEXT DEFAULT '#00f5ff',
        total_xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        quizzes_played INTEGER DEFAULT 0,
        best_streak INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Scores
    c.execute('''CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        score INTEGER NOT NULL,
        total INTEGER NOT NULL,
        topic TEXT,
        difficulty TEXT,
        xp_earned INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0,
        time_taken INTEGER DEFAULT 0,
        mode TEXT DEFAULT 'trivia',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Badges
    c.execute('''CREATE TABLE IF NOT EXISTS user_badges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        badge_id TEXT NOT NULL,
        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(username, badge_id)
    )''')

    # Daily challenge
    c.execute('''CREATE TABLE IF NOT EXISTS daily_challenge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE NOT NULL,
        questions TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS daily_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        date TEXT NOT NULL,
        score INTEGER NOT NULL,
        total INTEGER NOT NULL,
        time_taken INTEGER DEFAULT 0,
        UNIQUE(username, date)
    )''')

    # Questions bank
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        difficulty TEXT,
        question TEXT NOT NULL,
        option_a TEXT, option_b TEXT, option_c TEXT, option_d TEXT,
        correct_answer TEXT NOT NULL,
        source TEXT DEFAULT 'custom',
        active INTEGER DEFAULT 1
    )''')

    # Seed questions
    seeds = [
        ("Python","easy","What does 'def' do in Python?","Defines a variable","Defines a function","Defines a class","Defines a module","Defines a function"),
        ("Python","easy","What is the output of print(type([]))?","<class 'tuple'>","<class 'list'>","<class 'dict'>","<class 'set'>","<class 'list'>"),
        ("Python","medium","What does 'self' refer to in a class?","The class itself","The parent class","The current instance","A static variable","The current instance"),
        ("Python","hard","What is a Python decorator?","A UI element","A function that wraps another function","A type of loop","A class method","A function that wraps another function"),
        ("Science","easy","Chemical symbol for water?","WA","HO","H2O","OH2","H2O"),
        ("Science","medium","Speed of light (approx)?","3x10^6 m/s","3x10^8 m/s","3x10^10 m/s","3x10^4 m/s","3x10^8 m/s"),
        ("Science","hard","What is Schrodinger's equation used for?","Calculating speed","Quantum wave functions","Chemical reactions","Thermal dynamics","Quantum wave functions"),
        ("History","easy","First US President?","Thomas Jefferson","John Adams","George Washington","Benjamin Franklin","George Washington"),
        ("History","medium","World War II ended in?","1943","1944","1945","1946","1945"),
        ("History","hard","The Treaty of Westphalia was signed in?","1618","1648","1688","1702","1648"),
        ("Space","easy","Closest planet to the Sun?","Venus","Earth","Mars","Mercury","Mercury"),
        ("Space","medium","How many moons does Mars have?","0","1","2","3","2"),
        ("Space","hard","What is a Lagrange point?","A black hole","A gravitational equilibrium point","A type of star","A solar flare","A gravitational equilibrium point"),
        ("AI","easy","AI stands for?","Automated Intelligence","Artificial Intelligence","Advanced Interface","Analog Input","Artificial Intelligence"),
        ("AI","medium","Which is used for classification?","Linear Regression","K-Means","Random Forest","PCA","Random Forest"),
        ("AI","hard","What does backpropagation do in neural networks?","Feeds data forward","Updates weights using gradients","Initializes weights","Normalizes inputs","Updates weights using gradients"),
        ("Math","easy","Value of Pi (approx)?","2.14","3.14","4.14","1.14","3.14"),
        ("Math","medium","Derivative of x^2?","x","2x","x^2","2","2x"),
        ("Math","hard","What is Euler's identity?","e^i = -1","e^(i*pi) + 1 = 0","i^2 = 1","pi^e = 1","e^(i*pi) + 1 = 0"),
        ("General","easy","How many continents are there?","5","6","7","8","7"),
        ("General","medium","Capital of Australia?","Sydney","Melbourne","Canberra","Brisbane","Canberra"),
    ]
    for s in seeds:
        c.execute('''INSERT OR IGNORE INTO questions
            (topic,difficulty,question,option_a,option_b,option_c,option_d,correct_answer)
            VALUES (?,?,?,?,?,?,?,?)''', s)

    conn.commit()
    conn.close()
    print("✅ SaaS Database initialized!")

if __name__ == '__main__':
    init_db()
