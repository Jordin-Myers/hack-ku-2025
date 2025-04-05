# TrustRipple Flask App - app.py

from flask import Flask, render_template, request, redirect, send_file, flash
from utils.wallet import create_wallet
from utils.phishing import PHISHING_QUESTIONS
from utils.hygiene import evaluate_hygiene
from utils.encryption import encrypt_key
from utils.transaction import get_recent_transactions

app = Flask(__name__)
app.secret_key = 'trust_ripple_dev_key'  # Use a secure key in production

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wallet-generator', methods=['GET', 'POST'])
def wallet_generator():
    wallet = None
    if request.method == 'POST':
        wallet = create_wallet()
    return render_template('wallet_generator.html', wallet=wallet)

@app.route('/phishing-quiz', methods=['GET', 'POST'])
def phishing_quiz():
    score = None
    if request.method == 'POST':
        correct = 0
        for i, q in enumerate(PHISHING_QUESTIONS):
            answer = request.form.get(f'q{i}')
            if answer == q['answer']:
                correct += 1
        score = f"{correct} / {len(PHISHING_QUESTIONS)}"
    return render_template('phishing_quiz.html', questions=PHISHING_QUESTIONS, score=score)

@app.route('/transaction-scanner', methods=['GET', 'POST'])
def wallet_scanner():
    transactions = []
    address = None
    if request.method == 'POST':
        address = request.form['wallet_address']
        try:
            transactions = get_recent_transactions(address)
        except Exception as e:
            flash(f"Error fetching transactions: {str(e)}")
    return render_template('wallet_scanner.html', transactions=transactions, address=address)

@app.route('/wallet-hygiene', methods=['GET', 'POST'])
def hygiene_check():
    score = None
    if request.method == 'POST':
        seed = request.form['seed']
        backed_up = request.form.get('backed_up') == 'on'
        reused = request.form.get('reused') == 'on'
        score = evaluate_hygiene(seed, backed_up, reused)
    return render_template('wallet_hygiene.html', score=score)


@app.route('/encrypt-key', methods=['GET', 'POST'])
def encrypt_key_route():
    encrypted_key = None
    if request.method == 'POST':
        seed = request.form['seed']
        password = request.form['password']
        try:
            encrypted_key = encrypt_key(seed, password)
        except Exception as e:
            flash(f"Encryption failed: {str(e)}")
    return render_template('encrypt_key.html', encrypted_key=encrypted_key)

@app.route('/safety-checklist')
def safety_checklist():
    checklist = [
        "Double-check wallet addresses before sending funds",
        "Avoid clicking airdrop links from DMs",
        "Enable 2FA on wallet services",
        "Backup your seed phrase securely",
        "Verify DeFi platform contracts before use",
        "Use hardware wallets for large funds",
        "Don't reuse seed phrases"
    ]
    return render_template('safety_checklist.html', checklist=checklist)

if __name__ == '__main__':
    app.run(debug=True)
