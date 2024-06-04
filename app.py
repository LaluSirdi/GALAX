from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merchandise')
def merchandise():
    return render_template('merchandise.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)