import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Data hizi zitaingia moja kwa moja kwenye HTML (Dynamic Content)
    huduma_zetu = [
        {"icon": "fa-chart-line", "kichwa": "Ukuaji wa Biashara", "maelezo": "Mbinu za kuongeza mauzo."},
        {"icon": "fa-bullhorn", "kichwa": "Digital Marketing", "maelezo": "Matangazo ya mitandao ya kijamii."},
        {"icon": "fa-laptop-code", "kichwa": "Mifumo ya IT", "maelezo": "Kutengeneza Apps na Websites."},
        {"icon": "fa-handshake", "kichwa": "Ushauri wa Kitaalamu", "maelezo": "Miongozo ya uwekezaji."},
    ]
    return render_template('index.html', huduma=huduma_zetu)

if __name__ == '__main__':
    # Muhimu kwa Koyeb: Inasoma Port inayotolewa na server
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

