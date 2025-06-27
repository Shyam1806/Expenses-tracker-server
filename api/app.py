# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return "Hello Expense Tracker!"

# if __name__ == "__main__":
#     app.run(debug=True)
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient
load_dotenv()

app = Flask(__name__)
MONGO_URI = os.getenv("MONGO_URI")

# 🔌 MongoDB connection (local)
client = MongoClient("mongodb://localhost:27017")  # Or replace with Atlas URI
db = client["expenses_db"]
collection = db["expenses"]

# 🏠 Home route
@app.route('/')
def home():
    return "📊 Expense Tracker API Running!"

# ➕ Add a new expense
@app.route('/add-expense', methods=['POST'])
def add_expense():
    data = request.get_json()
    if not data or 'title' not in data or 'amount' not in data:
        return jsonify({"error": "Missing fields"}), 400
    
    collection.insert_one(data)
    return jsonify({"msg": "Expense added!"}), 201

# 📄 Get all expenses
@app.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = list(collection.find({}, {'_id': 0}))
    return jsonify(expenses)
@app.route('/summary', methods=['GET'])
def summary():
    # total expenses
    exp_pipeline = [
        {"$match": {"type": "expense"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    exp_res = list(collection.aggregate(exp_pipeline))
    total_exp = exp_res[0]['total'] if exp_res else 0

    # total income
    inc_pipeline = [
        {"$match": {"type": "income"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    inc_res = list(collection.aggregate(inc_pipeline))
    total_inc = inc_res[0]['total'] if inc_res else 0

    # balance
    balance = total_inc - total_exp

    return jsonify({
        "total_expenses": total_exp,
        "total_income": total_inc,
        "balance": balance
    })

# ⚙️ Run only when executed directly
if __name__ == "__main__":
    app.run(debug=True)
