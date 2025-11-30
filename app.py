from flask import Flask, render_template, request, redirect, url_for
import json, os
from datetime import datetime, date

app = Flask(__name__)
DATA_FILE = "ATM_details.json"

# Create data file if missing
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def today_str():
    return date.today().isoformat()

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def find_user(data, acc_no):
    return next((u for u in data if u["acc_no"] == acc_no), None)

def ensure_user(user):
    # Initialize fields if missing & reset daily counters if new day
    changed = False
    if "transactions" not in user:
        user["transactions"] = []
        changed = True
    if "daily" not in user:
        user["daily"] = {
            "date": today_str(),
            "deposit": 0,
            "withdraw": 0,
            "wrong_attempts_date": today_str(),
            "wrong_attempts": 0
        }
        changed = True

    # Reset deposit/withdraw counters if day changed
    if user["daily"].get("date") != today_str():
        user["daily"]["date"] = today_str()
        user["daily"]["deposit"] = 0
        user["daily"]["withdraw"] = 0
        changed = True

    # Reset wrong attempts date
    if user["daily"].get("wrong_attempts_date") != today_str():
        user["daily"]["wrong_attempts_date"] = today_str()
        user["daily"]["wrong_attempts"] = 0
        changed = True

    return changed

def record_transaction(user, t_type, amount):
    # After updating balance.
    user["transactions"].append({
        "time": now_str(),
        "type": t_type,
        "amount": amount,
        "balance": user["balance"]
    })

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            acc = int(request.form.get("acc_no"))
        except:
            return render_template("failure.html", message="Transaction Failed – Invalid account number format\nTry Again")

        pin = request.form.get("pin", "")
        data = load_data()
        user = find_user(data, acc)
        if not user:
            return render_template("failure.html", message="Transaction Failed – Account does not exist\nTry Again")

        ensure_user(user)

        # Check login attempts
        if user["daily"]["wrong_attempts"] >= 3:
            save_data(data)
            return render_template("failure.html", message="Transaction Failed – Maximum login attempts reached for today\nTry Again")

        if user["pin"] == pin:
            # success: reset wrong attempts for today
            user["daily"]["wrong_attempts"] = 0
            user["daily"]["wrong_attempts_date"] = today_str()
            save_data(data)
            return redirect(url_for("options", acc_no=acc))
        else:
            user["daily"]["wrong_attempts"] = user["daily"].get("wrong_attempts", 0) + 1
            user["daily"]["wrong_attempts_date"] = today_str()
            save_data(data)
            if user["daily"]["wrong_attempts"] >= 3:
                return render_template("failure.html", message="Transaction Failed – Maximum login attempts reached for today\nTry Again")
            else:
                return render_template("failure.html", message="Transaction Failed – Invalid PIN\nTry Again")

    return render_template("login.html")

# ---------------- SET PIN / REGISTER ----------------
@app.route("/setpin", methods=["GET", "POST"])
def setpin():
    if request.method == "POST":
        try:
            acc = int(request.form.get("acc_no"))
        except:
            return render_template("failure.html", message="Transaction Failed – Invalid account number format\nTry Again")

        name = (request.form.get("name") or "").strip()
        pin1 = request.form.get("pin1")
        pin2 = request.form.get("pin2")

        if not name:
            return render_template("failure.html", message="Transaction Failed – Name required\nTry Again")

        if pin1 != pin2:
            # PIN mismatch -> show error and auto redirect to home after 5s
            return render_template("failure.html", message="Transaction Failed – PIN Mismatch\nTry Again")

        data = load_data()
        if find_user(data, acc):
            return render_template("failure.html", message="Transaction Failed – Account already exists\nTry Again")

        new_user = {
            "acc_no": acc,
            "name": name,
            "pin": pin1,
            "balance": 0,
            "transactions": [],
            "daily": {
                "date": today_str(),
                "deposit": 0,
                "withdraw": 0,
                "wrong_attempts_date": today_str(),
                "wrong_attempts": 0
            }
        }
        data.append(new_user)
        save_data(data)
        # show PIN created successfully message then auto-redirect (success)
        return render_template("success.html", message="PIN Created Successfully\nThank You, Visit Again")
    return render_template("setpin.html")

# ---------------- OPTIONS ----------------
@app.route("/options/<int:acc_no>")
def options(acc_no):
    data = load_data()
    user = find_user(data, acc_no)
    if not user:
        return redirect(url_for("home"))
    ensure_user(user)
    save_data(data)
    return render_template("options.html", user=user, acc_no=acc_no)

# ---------------- DEPOSIT ----------------
@app.route("/deposit/<int:acc_no>", methods=["GET", "POST"])
def deposit(acc_no):
    data = load_data()
    user = find_user(data, acc_no)
    if not user:
        return render_template("failure.html", message="Transaction Failed – Account not found\nTry Again")

    ensure_user(user)

    if request.method == "POST":
        try:
            amount = int(request.form.get("amount"))
        except:
            return render_template("failure.html", message="Transaction Failed – Invalid amount\nTry Again")

        if amount <= 0:
            return render_template("failure.html", message="Transaction Failed – Invalid amount\nTry Again")

        if amount > 49999:
            return render_template("failure.html", message="Transaction Failed – Maximum deposit per transaction is ₹49,999\nTry Again")

        if user["daily"]["deposit"] + amount > 49999:
            return render_template("failure.html", message="Transaction Failed – Daily deposit limit reached (₹49,999)\nTry Again")

        # perform deposit
        user["balance"] += amount
        user["daily"]["deposit"] += amount
        user["daily"]["date"] = today_str()
        record_transaction(user, "Deposit", amount)
        save_data(data)

        # Show success page then auto redirect to home
        return render_template("success.html", message="Transaction Successful\nThank You, Visit Again")

    return render_template("deposit.html", acc_no=acc_no, user=user)

# ---------------- WITHDRAW ----------------
@app.route("/withdraw/<int:acc_no>", methods=["GET", "POST"])
def withdraw(acc_no):
    data = load_data()
    user = find_user(data, acc_no)
    if not user:
        return render_template("failure.html", message="Transaction Failed – Account not found\nTry Again")

    ensure_user(user)

    if request.method == "POST":
        try:
            amount = int(request.form.get("amount"))
        except:
            return render_template("failure.html", message="Transaction Failed – Invalid amount\nTry Again")

        if amount <= 0:
            return render_template("failure.html", message="Transaction Failed – Invalid amount\nTry Again")

        if user["balance"] < amount:
            return render_template("failure.html", message="Transaction Failed – Insufficient Balance\nTry Again")

        if user["daily"]["withdraw"] + amount > 20000:
            return render_template("failure.html", message="Transaction Failed – Daily withdrawal limit reached (₹20,000)\nTry Again")

        # perform withdraw
        user["balance"] -= amount
        user["daily"]["withdraw"] += amount
        user["daily"]["date"] = today_str()
        record_transaction(user, "Withdraw", amount)
        save_data(data)

        return render_template("success.html", message="Transaction Successful\nThank You, Visit Again")

    return render_template("withdraw.html", acc_no=acc_no, user=user)

# ---------------- MINI STATEMENT ----------------
@app.route("/mini/<int:acc_no>")
def mini(acc_no):
    data = load_data()
    user = find_user(data, acc_no)
    if not user:
        return redirect(url_for("home"))
    ensure_user(user)
    save_data(data)
    return render_template("mini.html", user=user)

# ---------------- BALANCE ----------------
@app.route("/balance/<int:acc_no>")
def balance(acc_no):
    data = load_data()
    user = find_user(data, acc_no)
    if not user:
        return redirect(url_for("home"))
    ensure_user(user)
    save_data(data)
    # Show balance success page (user wanted transaction-success message after check balance)
    # But user specifically wanted check balance to show current balance and then "Transaction Successful Visit again".
    # We'll show balance page and also a success message page redirecting after 5s.
    # To keep balance visible, we show the balance page (no redirect) but also offer a "Done" button that goes to success redirect.
    return render_template("balance.html", user=user)

# ---------------- CHANGE PIN ----------------
@app.route("/change_pin/<int:acc_no>", methods=["GET", "POST"])
def change_pin(acc_no):
    data = load_data()
    user = find_user(data, acc_no)
    if not user:
        return render_template("failure.html", message="Transaction Failed – Account not found\nTry Again")

    ensure_user(user)

    if request.method == "POST":
        old = request.form.get("old_pin")
        new1 = request.form.get("new_pin1")
        new2 = request.form.get("new_pin2")

        if user["pin"] != old:
            return render_template("failure.html", message="Transaction Failed – Wrong Old PIN\nTry Again")

        if new1 != new2:
            return render_template("failure.html", message="Transaction Failed – PIN Mismatch\nTry Again")

        user["pin"] = new1
        save_data(data)
        return render_template("success.html", message="PIN Changed Successfully\nThank You, Visit Again")

    return render_template("change_pin.html", acc_no=acc_no, user=user)

# ---------------- FAILURE PAGE ----------------
@app.route("/failure")
def failure_page():
    return render_template("failure.html", message="Transaction Failed\nTry Again")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
