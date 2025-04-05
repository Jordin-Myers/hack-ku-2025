
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    from utils.phishing import QUESTIONS
    return render_template('quiz.html', questions=QUESTIONS)

@app.route('/pwned', methods=['GET', 'POST'])
def pwned():
    result = None
    if request.method == 'POST':
        email = request.form['email']
        from utils.pwned import check_email
        result = check_email(email)
    return render_template('pwned.html', result=result)

@app.route('/password', methods=['GET', 'POST'])
def password():
    result = None
    if request.method == 'POST':
        from utils.password import evaluate_password
        user_password = request.form['password']
        result = evaluate_password(user_password)
    return render_template('password.html', result=result)

@app.route('/iot')
def iot():
    from utils.iot_data import VULNS
    return render_template('iot.html', vulns=VULNS)

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    result = None
    return render_template('encrypt.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
