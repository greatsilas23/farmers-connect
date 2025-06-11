from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pandas as pd
import pickle
import re
import os

app = Flask(__name__)
CORS(app)

# --- In-memory "database" for demo purposes ---
users_db = {}

# --- Load Models and Scalers ---
try:
    model_path = r'C:\Users\Silas\Downloads\Crop_Recommendation-main\Crop_Recommendation-main'
    model = pickle.load(open(os.path.join(model_path, 'model.pkl'), 'rb'))
    sc = pickle.load(open(os.path.join(model_path, 'standscaler.pkl'), 'rb'))
    mx = pickle.load(open(os.path.join(model_path, 'minmaxscaler.pkl'), 'rb'))
    print("[INFO] Crop recommendation model and scalers loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load crop model/scalers: {e}")
    model = sc = mx = None

try:
    with open("crop_price_model.pkl", "rb") as f:
        price_model = pickle.load(f)
    with open("le_market.pkl", "rb") as f:
        le_market = pickle.load(f)
    with open("le_commodity.pkl", "rb") as f:
        le_commodity = pickle.load(f)
    with open("le_unit.pkl", "rb") as f:
        le_unit = pickle.load(f)
    print("[INFO] Price prediction model and label encoders loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load price prediction components: {e}")
    price_model = le_market = le_commodity = le_unit = None

# --- Helper: Load Available Crop Price Options ---
def load_data():
    try:
        df = pd.read_csv("wfp_food_prices_ken.csv")
        df = df[1:]  # Skip duplicated header
        df = df.dropna(subset=["commodity", "market", "unit"])
        crops = sorted(df["commodity"].unique())
        markets = sorted(df["market"].unique())
        units = sorted(df["unit"].unique())
        return crops, markets, units
    except Exception as e:
        print(f"[ERROR] Failed to load options data: {e}")
        return [], [], []

available_crops, available_markets, available_units = load_data()

# --- Routes ---
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json(force=True)

        required_fields = ['email', 'first_name', 'last_name', 'password', 'is_farmer']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400

        email = data['email'].strip().lower()
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        password = data['password']
        is_farmer = bool(data['is_farmer'])

        # Validate email format
        if not re.match(r'^\S+@\S+\.\S+$', email):
            return jsonify({'message': 'Invalid email format'}), 400

        if email in users_db:
            return jsonify({'message': 'Email already registered'}), 400

        users_db[email] = {
            'first_name': first_name,
            'last_name': last_name,
            'password_hash': generate_password_hash(password),
            'is_farmer': is_farmer
        }

        print(f"[INFO] Registered new user: {email}")
        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        print(f"[ERROR] Register failed: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        user = users_db.get(email)
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        print(f"[INFO] Login success for: {email}")
        return jsonify({
            'success': True,
            'user': {
                'email': email,
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'is_farmer': user['is_farmer']
            }
        }), 200

    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/api/recommend_crop', methods=['POST'])
def recommend_crop():
    try:
        if not model or not sc or not mx:
            return jsonify({'error': 'Model not available'}), 500

        data = request.get_json(force=True)
        features = [
            float(data['Nitrogen']),
            float(data['Phosphorus']),
            float(data['Potassium']),
            float(data['Temperature']),
            float(data['Humidity']),
            float(data['pH']),
            float(data['Rainfall'])
        ]

        mx_features = mx.transform([features])
        sc_mx_features = sc.transform(mx_features)
        prediction = model.predict(sc_mx_features)

        crop_dict = {
            1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
            8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
            14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
            19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"
        }

        crop = crop_dict.get(prediction[0], "Unknown Crop")
        print(f"[INFO] Recommended crop: {crop}")
        return jsonify({'recommendation': f"{crop} is the best crop to be cultivated right there"})

    except Exception as e:
        print(f"[ERROR] Crop recommendation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/options', methods=['GET'])
def get_options():
    return jsonify({
        "crops": available_crops,
        "markets": available_markets,
        "units": available_units,
    })

@app.route('/api/predict', methods=['POST'])
def predict_price():
    try:
        if not price_model or not le_market or not le_commodity or not le_unit:
            return jsonify({'success': False, 'error': 'Model or encoders not available'}), 500

        data = request.get_json(force=True)
        market = data["market"]
        commodity = data["commodity"]
        unit = data["unit"]
        quantity = int(data["quantity"])
        year = int(data["year"])
        month = int(data["month"])

        market_enc = le_market.transform([market])[0]
        commodity_enc = le_commodity.transform([commodity])[0]
        unit_enc = le_unit.transform([unit])[0]

        features = np.array([[market_enc, commodity_enc, unit_enc, year, month]])
        predicted_price = price_model.predict(features)[0]
        total_price = predicted_price * quantity

        message = (
            f"Predicted price for {quantity} {unit}(s) of {commodity} in {market} "
            f"on {month}/{year} is KES {total_price:.2f}"
        )

        print(f"[INFO] Price prediction: {message}")
        return jsonify({"success": True, "message": message})

    except Exception as e:
        print(f"[ERROR] Price prediction failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

# --- Run Server ---
if __name__ == "__main__":
    app.run(debug=True)
