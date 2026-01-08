import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
# Secret key ni lazima ili session ifanye kazi
app.secret_key = "dr_mitambo_key_secret_99"

# Hifadhi ya muda (Itafutika ukiredeploy, lakini itakubali ukiwa hewani)
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
        # Debug: Inasaidia kuona kama data inafika (itaonekana kwenye Logs)
        print(f"Jaribio la Login: {username}") 
        
        if username in users and users[username] == password:
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
        if username and password:
            users[username] = password
            print(f"Mtumiaji mpya: {username}")
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

# Routes za kurasa nyingine
@app.route('/diagnosis')
def diagnosis(): return render_template('diagnosis.html')

@app.route('/electrical')
def electrical(): return render_template('electrical.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
