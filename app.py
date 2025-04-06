from flask import Flask, render_template, request, redirect, send_file, flash, session, url_for
from utils.wallet import send_test_transactions, create_wallet, get_live_balance
from utils.phishing import PHISHING_QUESTIONS
from utils.hygiene import HYGIENE_QUESTIONS
from utils.encryption import encrypt_key, decrypt_key
from utils.transaction import get_recent_transactions
from flask import jsonify
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from utils.validation import is_valid_xrpl_address
import os
import hashlib

load_dotenv()

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]  # Optional: a global limit
)

app.permanent_session_lifetime = timedelta(minutes=20)

app.secret_key = os.getenv("SECRET_KEY")
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.context_processor
def inject_wallet_info():
    address = session.get("wallet_address")
    balance = get_live_balance(address) if address else None
    print("[Context] Wallet Address in session:", address)
    return dict(
        wallet_address=address,
        wallet_balance=balance
    )

@app.route('/')
def index():
    phishing_score = session.get("phishing_score")
    hygiene_score = session.get("hygiene_score")

    try:
        phishing_score = int(phishing_score) if phishing_score is not None else None
    except ValueError:
        phishing_score = None

    try:
        hygiene_score = int(hygiene_score) if hygiene_score is not None else None
    except ValueError:
        hygiene_score = None

    all_done = phishing_score is not None and hygiene_score is not None

    # Wallet stats
    wallet_address = session.get("wallet_address")
    wallet_stats = {}
    recent_txs = []

    if wallet_address:
        try:
            wallet_stats["balance"] = get_live_balance(wallet_address)
            wallet_stats["address"] = wallet_address

            # Optional placeholder/fallback
            wallet_stats["age"] = "Testnet (n/a)"
            wallet_stats["tx_count"] = 0

            recent_txs = get_recent_transactions(wallet_address)
            wallet_stats["tx_count"] = len(recent_txs)

        except Exception as e:
            print("[Dashboard] Failed to fetch wallet info:", e)

    return render_template(
        "index.html",
        phishing_score=phishing_score,
        hygiene_score=hygiene_score,
        phishing_total=5,
        hygiene_total=4,
        all_done=all_done,
        wallet_stats=wallet_stats,
        recent_txs=recent_txs
    )


@app.route('/wallet-generator', methods=['GET', 'POST'])
def wallet_generator():
    from types import SimpleNamespace
    wallet = None

    if request.method == 'POST':
        session.permanent = True
        action = request.form.get('action')
        
        if action == 'generate':
            password = request.form.get('password', '').strip()

            # ✅ Check if password is actually provided *before hashing*
            if not password:
                flash("Password is required to encrypt your wallet.")
                return redirect(url_for('wallet_generator'))

            # ✅ Safe to hash and store after check
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            session['wallet_password_hash'] = hashed_pw

            wallet = create_wallet()
            if not wallet or not hasattr(wallet, "seed"):
                flash("Failed to generate wallet.")
                return redirect(url_for('wallet_generator'))

            encrypted_seed = encrypt_key(wallet.seed, password)

            session['wallet_address'] = wallet.address
            session['wallet_seed'] = encrypted_seed
            session['wallet_balance'] = wallet.balance
            session['wallet_password'] = password

            return redirect(url_for('wallet_generator'))

    # Show previously generated wallet
    if 'wallet_address' in session:
        wallet = SimpleNamespace(
            address=session.get('wallet_address'),
            seed=session.get('wallet_seed'),
            balance=session.get('wallet_balance')
        )

    return render_template('wallet_generator.html', wallet=wallet)

@limiter.limit("10 per minute")
@app.route('/decrypt-seed', methods=['POST'])
def decrypt_seed():
    data = request.get_json()
    password = data.get("password")
    client_hash = hashlib.sha256(password.encode()).hexdigest()
    if client_hash != session.get('wallet_password_hash'):
        return jsonify(success=False)

    encrypted = session.get('wallet_seed')  # ✅ Use stored encrypted seed
    if not encrypted or not password:
        return jsonify(success=False)

    try:
        decrypted = decrypt_key(encrypted, password)
        return jsonify(success=True, seed=decrypted)
    except Exception as e:
        print("Decryption error:", e)
        return jsonify(success=False)

@app.route('/phishing-quiz', methods=['GET', 'POST'])
def phishing_quiz():
    score = None
    if request.method == 'POST':
        correct = 0
        for i, q in enumerate(PHISHING_QUESTIONS):
            answer = request.form.get(f'q{i}')
            if answer == q['answer']:
                correct += 1
        score = correct
        session['phishing_score'] = str(score)
    return render_template('phishing_quiz.html', questions=PHISHING_QUESTIONS, score=score)

@app.route('/hygiene-check', methods=['GET', 'POST'])
def hygiene_check():
    score = None
    if request.method == 'POST':
        good = 0
        for i, q in enumerate(HYGIENE_QUESTIONS):
            answer = request.form.get(f'q{i}')
            if answer == q['answer']:
                good += 1
        score = good
        session['hygiene_score'] = str(score)
    return render_template('wallet_hygiene.html', questions=HYGIENE_QUESTIONS, score=score)

@app.route('/wallet-scanner', methods=['GET', 'POST'])
def wallet_scanner():
    transactions = []
    address = None

    if request.method == 'POST':
        address = request.form.get('wallet_address')
        if not is_valid_xrpl_address(address):
            flash("❌ Invalid XRPL address format.")
            return redirect(url_for('wallet_scanner'))
        
        try:
            transactions = get_recent_transactions(address)
        except Exception as e:
            flash(f"⚠️ Error fetching transactions: {str(e)}")
    else:
        address = session.get('wallet_address')  # Still show stored wallet on GET

    return render_template('wallet_scanner.html', transactions=transactions, address=address)

@app.route('/encrypt-key', methods=['GET', 'POST'])
def encrypt_key_route():
    encrypted_key = None

    if request.method == 'POST':
        secret = request.form.get('secret', '').strip()
        password = request.form.get('password', '').strip()

        if secret and password:
            try:
                encrypted_key = encrypt_key(secret, password)
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

@app.route('/logout')
def logout():
    session.clear()
    flash("Session cleared.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
