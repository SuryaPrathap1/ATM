# 💳 ATM Management System (Flask + JSON)

This project is a simple **ATM Management Web Application** built using **Flask** and **JSON file storage**.  
It simulates core ATM functionalities such as:

- Creating an account (Set PIN)
- Login using Account Number & PIN
- Deposit money
- Withdraw money
- Change PIN
- Check Balance
- Mini Statement (Transaction History)
- Auto redirect success & failure pages
- Daily deposit/withdraw limits
- Login attempt limits

Everything is stored in a local JSON file (`ATM_details.json`) which acts as a lightweight database.

---

## 🚀 Features

### 🔐 **Authentication**
- Set PIN (Account registration)
- Login with account number and PIN
- Only **3 wrong login attempts per day**

### 💸 **Transactions**
- Deposit (max ₹49,999 per transaction & per day)
- Withdraw (max ₹20,000 per day)
- Balance check
- Mini statement (with date, time, amount, balance)

### 🔁 **Transaction History**
Each transaction stores:
- Timestamp  
- Transaction Type (Deposit / Withdraw)
- Amount  
- Updated Balance  

### 🟦 **ATM-style UI**
- SBI-styled blue & white design  
- Clean and responsive  
- ATM-like button layout  
- Success/Failure pages auto-redirect in 5 seconds  

### ⚙️ **Error Handling**
- PIN mismatch → failure page  
- Daily limit exceeded → failure page  
- Insufficient balance → failure page  
- All errors redirect automatically to home page  

---

## 🛠️ Tech Stack

| Component | Technology |
|----------|------------|
| Backend  | Flask (Python) |
| Storage  | JSON file (`ATM_details.json`) |
| Frontend | HTML, CSS, Jinja Templates |
| UI Theme | Blue/White ATM Style |
| Runtime  | Python 3 |



