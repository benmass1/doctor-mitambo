import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "dr_mitambo_super_secret_2026"

# Database ya muda (Inafanya kazi ukiwa hewani)
# Kumbuka: Ukirestart server Koyeb, data hizi hufutika mpaka tutakapoweka SQL
users = {"admin": "1234"} 

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if users.get(username) == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash("Username au Password si sahihi!")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users:
            flash("Username tayari imetumika!")
        else:
            users[username] = password
            flash("Usajili umekamilika! Ingia sasa.")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Kurasa nyingine
@app.route('/diagnosis')
def diagnosis(): return render_template('diagnosis.html')

@app.route('/electrical')
def electrical(): return render_template('electrical.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
