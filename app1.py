from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pandas as pd
import pickle
import re
import os

app = Flask(__name__)
CORS(app)

# --- Database configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farmers_connect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_farmer = db.Column(db.Boolean, default=True)

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    nitrogen = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    rainfall = db.Column(db.Float, nullable=False)
    recommended_crop = db.Column(db.String(50), nullable=False)

# --- Initialize DB ---
with app.app_context():
    db.create_all()

# --- Load ML Models and Scalers ---
model_path = r'C:\Users\Silas\Downloads\Crop_Recommendation-main\Crop_Recommendation-main'

try:
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

# --- Load Options ---
def load_data():
    try:
        df = pd.read_csv("wfp_food_prices_ken.csv")
        df = df[1:]
        df = df.dropna(subset=["commodity", "market", "unit"])
        return sorted(df["commodity"].unique()), sorted(df["market"].unique()), sorted(df["unit"].unique())
    except Exception as e:
        print(f"[ERROR] Failed to load options data: {e}")
        return [], [], []

available_crops, available_markets, available_units = load_data()

# --- Register API ---
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json(force=True)
        required = ['email', 'first_name', 'last_name', 'password', 'is_farmer']
        if not all(k in data for k in required):
            return jsonify({'message': 'Missing required fields'}), 400

        email = data['email'].strip().lower()
        if not re.match(r'^\S+@\S+\.\S+$', email):
            return jsonify({'message': 'Invalid email format'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 400

        new_user = User(
            email=email,
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            password_hash=generate_password_hash(data['password']),
            is_farmer=bool(data['is_farmer'])
        )
        db.session.add(new_user)
        db.session.commit()
        print(f"[INFO] Registered new user: {email}")
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        print(f"[ERROR] Register failed: {e}")
        return jsonify({'message': 'Internal server error'}), 500

# --- Login API ---
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        print(f"[INFO] Login success for: {email}")
        return jsonify({
            'success': True,
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_farmer': user.is_farmer
            }
        }), 200
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

# --- Crop Recommendation API ---
@app.route('/api/recommend_crop', methods=['POST'])
def recommend_crop():
    try:
        if not model or not sc or not mx:
            return jsonify({'error': 'Model not available'}), 500

        data = request.get_json(force=True)
        input_fields = ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall']
        if not all(field in data for field in input_fields):
            return jsonify({'error': 'Missing input fields'}), 400

        features = [float(data[field]) for field in input_fields]
        features_scaled = sc.transform(mx.transform([features]))
        prediction = model.predict(features_scaled)[0]

        crop_dict = {
            1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
            8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
            14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
            19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"
        }
        crop = crop_dict.get(prediction, "Unknown Crop")

        new_crop = Crop(
            name=crop,
            nitrogen=features[0],
            phosphorus=features[1],
            potassium=features[2],
            temperature=features[3],
            humidity=features[4],
            ph=features[5],
            rainfall=features[6],
            recommended_crop=crop
        )
        db.session.add(new_crop)
        db.session.commit()

        print(f"[INFO] Recommended crop: {crop}")
        return jsonify({'recommendation': f"{crop} is the best crop to be cultivated right there"})
    except Exception as e:
        print(f"[ERROR] Crop recommendation failed: {e}")
        return jsonify({'error': str(e)}), 500

# --- Get Crop/Market Options ---
@app.route('/api/options', methods=['GET'])
def get_options():
    return jsonify({
        "crops": available_crops,
        "markets": available_markets,
        "units": available_units,
    })

# --- Price Prediction API ---
@app.route('/api/predict', methods=['POST'])
def predict_price():
    try:
        if not price_model or not le_market or not le_commodity or not le_unit:
            return jsonify({'success': False, 'error': 'Model or encoders not available'}), 500

        data = request.get_json(force=True)
        required = ['market', 'commodity', 'unit', 'quantity', 'year', 'month']
        if not all(k in data for k in required):
            return jsonify({'success': False, 'error': 'Missing input fields'}), 400

        market_enc = le_market.transform([data['market']])[0]
        commodity_enc = le_commodity.transform([data['commodity']])[0]
        unit_enc = le_unit.transform([data['unit']])[0]

        features = np.array([[market_enc, commodity_enc, unit_enc, int(data['year']), int(data['month'])]])
        predicted_price = price_model.predict(features)[0]
        total_price = predicted_price * int(data['quantity'])

        message = (
            f"Predicted price for {data['quantity']} {data['unit']}(s) of {data['commodity']} in {data['market']} "
            f"on {data['month']}/{data['year']} is KES {total_price:.2f}"
        )
        print(f"[INFO] Price prediction: {message}")
        return jsonify({"success": True, "message": message})
    except Exception as e:
        print(f"[ERROR] Price prediction failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

# --- Run the App ---
if __name__ == "__main__":
    app.run(debug=True)
