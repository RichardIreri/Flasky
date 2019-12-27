# Rendering templates
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.route('/')
def List():
    l = [10, 20, 30, 40, 50]
    for elem in l:
        return render_template('user.html', comments=l)