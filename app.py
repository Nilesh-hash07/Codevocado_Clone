# app.py
import sqlite3
from flask import Flask, render_template_string, request, session, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

# SQLite database initialization
def init_db():
    conn = sqlite3.connect('test_assessment.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            answer INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_answers():
    conn = sqlite3.connect('test_assessment.db')
    cursor = conn.cursor()
    cursor.execute('SELECT answer, timestamp FROM answers ORDER BY id DESC')
    answers = [{'answer': row[0], 'timestamp': row[1]} for row in cursor.fetchall()]
    conn.close()
    return answers

def add_answer(answer):
    conn = sqlite3.connect('test_assessment.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO answers (answer, timestamp) VALUES (?, ?)',
                   (answer, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# ENHANCED HTML template with front-page elements only
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Assessment</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            overflow-x: hidden;
        }
        .stars {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }
        .star {
            position: absolute;
            background: white;
            border-radius: 50%;
            animation: twinkle 2s infinite;
        }
        @keyframes twinkle {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
        }
        .container { 
            text-align: center; 
            position: relative;
            z-index: 2;
        }
        .tagline {
            font-size: 1.2rem;
            font-weight: 300;
            margin-bottom: 1rem;
            opacity: 0.9;
            letter-spacing: 2px;
        }
        h1 { 
            font-size: 4.5rem; 
            font-weight: 700;
            margin-bottom: 1rem; 
            text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .subtitle {
            font-size: 1.1rem;
            font-weight: 300;
            margin-bottom: 2rem;
            opacity: 0.8;
            max-width: 600px;
        }
        .login-btn { 
            position: absolute; 
            top: 30px; 
            right: 30px; 
            background: rgba(255,107,107,0.9); 
            color: white; 
            border: none; 
            padding: 14px 28px; 
            border-radius: 50px; 
            cursor: pointer; 
            font-size: 16px; 
            font-weight: 600;
            transition: all 0.4s ease;
            box-shadow: 0 4px 15px rgba(255,107,107,0.3);
        }
        .login-btn:hover { 
            background: #ff6b6b; 
            transform: scale(1.05) translateY(-2px);
            box-shadow: 0 8px 25px rgba(255,107,107,0.4);
        }
        .login-form, .assessment, .admin-panel { 
            background: rgba(255,255,255,0.15); 
            backdrop-filter: blur(20px); 
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 25px; 
            padding: 45px; 
            max-width: 500px; 
            width: 90%; 
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        .form-group { margin-bottom: 25px; }
        label { 
            display: block; 
            margin-bottom: 10px; 
            font-size: 18px; 
            font-weight: 500;
        }
        input[type="text"], input[type="password"], input[type="number"] { 
            width: 100%; 
            padding: 15px; 
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 15px; 
            font-size: 16px; 
            background: rgba(255,255,255,0.95);
            font-family: 'Poppins', sans-serif;
            transition: all 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #4ecdc4;
            box-shadow: 0 0 20px rgba(78,205,196,0.3);
        }
        .submit-btn { 
            background: linear-gradient(45deg, #4ecdc4, #44bdad); 
            color: white; 
            border: none; 
            padding: 18px 35px; 
            border-radius: 50px; 
            font-size: 18px; 
            font-weight: 600;
            cursor: pointer; 
            width: 100%; 
            transition: all 0.4s ease;
            box-shadow: 0 5px 20px rgba(78,205,196,0.3);
        }
        .submit-btn:hover { 
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(78,205,196,0.4);
        }
        .logout-btn { 
            background: linear-gradient(45deg, #ff6b6b, #ff5252); 
            color: white; 
            border: none; 
            padding: 12px 25px; 
            border-radius: 25px; 
            cursor: pointer; 
            margin-top: 25px;
            font-weight: 500;
            transition: all 0.3s;
        }
        .logout-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(255,107,107,0.4);
        }
        .question { 
            font-size: 2.2rem; 
            margin-bottom: 25px; 
            font-weight: 600;
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .answer-list { text-align: left; margin-top: 25px; }
        .answer-item { 
            background: rgba(255,255,255,0.2); 
            padding: 18px; 
            margin: 12px 0; 
            border-radius: 15px; 
            border-left: 4px solid #4ecdc4;
            transition: all 0.3s;
        }
        .answer-item:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        .hidden { display: none; }
        .error { 
            color: #ff8a8a; 
            margin-top: 15px; 
            font-weight: 500;
            background: rgba(255,138,138,0.2);
            padding: 10px;
            border-radius: 10px;
            border-left: 4px solid #ff6b6b;
        }
        .success { 
            color: #4ecdc4; 
            margin-top: 15px; 
            font-weight: 500;
            background: rgba(78,205,196,0.2);
            padding: 10px;
            border-radius: 10px;
            border-left: 4px solid #4ecdc4;
        }
        @media (max-width: 768px) {
            h1 { font-size: 3rem; }
            .login-btn { top: 15px; right: 15px; padding: 12px 20px; }
        }
    </style>
</head>
<body>
    <div class="stars" id="stars"></div>
    
    <div class="login-btn" onclick="showLogin()">Login</div>
    
    <div class="container">
        <div class="tagline">Welcome to Our Assessment Platform</div>
        <h1>Test Assessment</h1>
        <div class="subtitle">Empowering Learning Through Innovative Evaluation</div>
        
        <!-- Login Form -->
        <div id="loginForm" class="login-form hidden">
            <h2>{{ 'Admin Panel' if show_admin else 'Employee Login' }}</h2>
            <form method="POST" action="{{ url_for('login') }}">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit" class="submit-btn">Login</button>
            </form>
            <div class="error">{{ error }}</div>
            {% if show_admin %}
                <p style="margin-top: 25px;">
                    <a href="{{ url_for('index', show_admin=False) }}" style="color: #4ecdc4; text-decoration: none; font-weight: 500;">Employee Login</a>
                </p>
            {% else %}
                <p style="margin-top: 25px;">
                    <a href="{{ url_for('index', show_admin=True) }}" style="color: #4ecdc4; text-decoration: none; font-weight: 500;">Admin Login</a>
                </p>
            {% endif %}
        </div>
        
        <!-- Employee Assessment -->
        {% if session.user == 'emp123' %}
        <div class="assessment">
            <h2>Employee Assessment</h2>
            <div class="question">What is 2 + 2?</div>
            <form method="POST" action="{{ url_for('submit_answer') }}">
                <div class="form-group">
                    <label>Answer:</label>
                    <input type="number" name="answer" required>
                </div>
                <button type="submit" class="submit-btn">Submit Answer</button>
            </form>
            <div class="success">{{ success }}</div>
            <button class="logout-btn" onclick="window.location.href='{{ url_for('logout') }}'">Logout</button>
        </div>
        {% endif %}
        
        <!-- Admin Panel -->
        {% if session.user == 'ad123' %}
        <div class="admin-panel">
            <h2>Admin Panel</h2>
            <p>Employee Answers:</p>
            <div class="answer-list">
                {% if answers %}
                    {% for answer in answers %}
                    <div class="answer-item">
                        Answer: {{ answer.answer }} 
                        (Submitted: {{ answer.timestamp }})
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="text-align: center; opacity: 0.8;">No answers submitted yet.</p>
                {% endif %}
            </div>
            <button class="logout-btn" onclick="window.location.href='{{ url_for('logout') }}'">Logout</button>
        </div>
        {% endif %}
    </div>

    <script>
        // Animated stars background
        function createStars() {
            const starsContainer = document.getElementById('stars');
            for(let i = 0; i < 50; i++) {
                const star = document.createElement('div');
                star.className = 'star';
                star.style.left = Math.random() * 100 + '%';
                star.style.top = Math.random() * 100 + '%';
                star.style.width = star.style.height = (Math.random() * 3 + 1) + 'px';
                star.style.animationDelay = Math.random() * 2 + 's';
                starsContainer.appendChild(star);
            }
        }
        createStars();

        function showLogin() {
            document.getElementById('loginForm').classList.remove('hidden');
            document.querySelector('.tagline').style.display = 'none';
            document.querySelector('h1').style.display = 'none';
            document.querySelector('.subtitle').style.display = 'none';
        }
    </script>
</body>
</html>
'''

@app.route('/', defaults={'show_admin': False})
@app.route('/<int:show_admin>')
def index(show_admin):
    if 'user' in session:
        return render_template_string(HTML_TEMPLATE, 
                                    show_admin=show_admin, 
                                    error=None,
                                    success=session.get('success', ''),
                                    answers=get_answers())
    
    return render_template_string(HTML_TEMPLATE, 
                                show_admin=show_admin, 
                                error=session.get('error', ''))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username == 'emp123' and password == 'emp123':
        session['user'] = 'emp123'
        session.pop('error', None)
        session.pop('success', None)
        return redirect(url_for('index'))
    elif username == 'ad123' and password == 'ad123':
        session['user'] = 'ad123'
        session.pop('error', None)
        session.pop('success', None)
        return redirect(url_for('index'))
    else:
        session['error'] = 'Invalid username or password!'
        return redirect(url_for('index', show_admin=True))

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if session.get('user') == 'emp123':
        answer = int(request.form['answer'])
        add_answer(answer)
        session['success'] = 'Answer submitted successfully!'
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('success', None)
    session.pop('error', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
