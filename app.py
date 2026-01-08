import os
from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "dr_mitambo_pro_ultra_secret"

# Orodha ya Batani 10 za Dashibodi
buttons = [
    {'id': 'diag', 'title': 'AI Diagnosis', 'icon': 'fa-microchip', 'route': 'diagnosis', 'desc': 'CAT & Komatsu Experts'},
    {'id': 'elec', 'title': 'Electrical', 'icon': 'fa-bolt', 'route': 'electrical', 'desc': 'Wiring & Pinouts'},
    {'id': 'sys', 'title': 'Systems Op', 'icon': 'fa-cogs', 'route': 'systems_op', 'desc': 'Hydraulic & Engine Op'},
    {'id': 'trouble', 'title': 'Troubleshoot', 'icon': 'fa-wrench', 'route': 'troubleshooting', 'desc': 'Step-by-Step Guides'},
    {'id': 'serv', 'title': 'Service', 'icon': 'fa-calendar-check', 'route': 'maintenance', 'desc': 'Maintenance Logs'},
    {'id': 'man', 'title': 'Manuals', 'icon': 'fa-book', 'route': 'manuals', 'desc': 'Library ya Mitambo'},
    {'id': 'parts', 'title': 'Parts Book', 'icon': 'fa-search', 'route': 'parts', 'desc': 'Spare Parts Lookup'},
    {'id': 'calib', 'title': 'Calibration', 'icon': 'fa-sliders-h', 'route': 'calibration', 'desc': 'Sensor & Valve Cal'},
    {'id': 'harness', 'title': 'Harness Hub', 'icon': 'fa-project-diagram', 'route': 'harness', 'desc': 'Connector Views'},
    {'id': 'safety', 'title': 'Safety Op', 'icon': 'fa-hard-hat', 'route': 'safety', 'desc': 'Operation Safety'}
]

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html', buttons=buttons)

@app.route('/index')
def index():
    return home()

# Routes za Batani zote (Hapa unaweza kuongeza HTML zake baadaye)
@app.route('/diagnosis')
def diagnosis(): return render_template('diagnosis.html')

@app.route('/electrical')
def electrical(): return render_template('electrical.html')

@app.route('/systems_op')
def systems_op(): return "Ukurasa wa Systems Operation unakuja hivi punde..."

@app.route('/troubleshooting')
def troubleshooting(): return "Ukurasa wa Troubleshooting unakuja hivi punde..."

@app.route('/maintenance')
def maintenance(): return render_template('maintenance.html')

@app.route('/manuals')
def manuals(): return "Library ya Manuals inatengenezwa..."

# Ongeza routes nyingine hapa chini...

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
