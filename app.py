import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "doctor_mitambo_2026_key"

# Mpangilio wa kadi kwenye Dashboard (Home)
huduma_zetu = [
    {'title': 'Diagnosis AI', 'icon': 'fa-user-md', 'link': 'diagnosis'},
    {'title': 'Electrical', 'icon': 'fa-bolt', 'link': 'electrical'},
    {'title': 'Maintenance', 'icon': 'fa-tools', 'link': 'maintenance'},
    {'title': 'Training Hub', 'icon': 'fa-graduation-cap', 'link': 'index'}
]

@app.route('/')
def index():
    # Flask itatafuta index.html ndani ya templates/
    return render_template('index.html', huduma=huduma_zetu)

@app.route('/diagnosis')
def diagnosis():
    return render_template('diagnosis.html')

@app.route('/electrical')
def electrical():
    return render_template('electrical.html')

@app.route('/maintenance')
def maintenance():
    # Tunatuma data za mfano kuzuia makosa ya 'Undefined Variable'
    fleet = [
        {"model": "CAT 336D", "sn": "MBD0254", "status": "Operational", "hours": "4250"},
        {"model": "D8R", "sn": "9EM0124", "status": "Breakdown", "hours": "8900"}
    ]
    return render_template('maintenance.html', fleet=fleet)

if __name__ == '__main__':
    # Hii ni muhimu kwa ajili ya Koyeb kutambua Port
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

