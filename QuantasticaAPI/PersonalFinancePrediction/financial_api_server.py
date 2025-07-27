from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import traceback
from flask_cors import CORS
app = Flask(__name__)
CORS(app, origins="http://localhost:5173")

class FinancialAPI:
    def __init__(self):
        """Initialize the API with models and data"""
        try:
            # Load trained models
            self.expenditure_model = joblib.load('expenditure_model.pkl')
            self.savings_model = joblib.load('savings_model.pkl')
            self.scaler = joblib.load('scaler.pkl')
            self.label_encoder = joblib.load('label_encoder.pkl')
            
            # Load datasets
            self.transactions_df = pd.read_csv('bank_transactions_detailed.csv')
            self.user_features_df = pd.read_csv('bank_transactions_user_features.csv')
            self.monthly_df = pd.read_csv('monthly_financial_data.csv')
            
            # Convert transaction_date to datetime
            self.transactions_df['transaction_date'] = pd.to_datetime(self.transactions_df['transaction_date'])
            
            print("✅ Models and data loaded successfully!")
            print(f"Available users: {sorted(self.user_features_df['user_id'].unique())}")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            self.expenditure_model = None
            self.savings_model = None

# Initialize the API
financial_api = FinancialAPI()

@app.route('/', methods=['GET'])
def home():
    """API information endpoint"""
    return jsonify({
        "message": "Financial Prediction API",
        "version": "1.0",
        "endpoints": {
            "GET /users": "Get all available user IDs",
            "GET /transactions/<user_id>": "Get all transactions for a user",
            "POST /predict/expenditure": "Predict monthly expenditure for a user",
            "POST /predict/savings": "Predict monthly savings for a user",
            "POST /predict/both": "Predict both expenditure and savings for a user",
            "GET /user/<user_id>/profile": "Get user profile and statistics"
        }
    })

@app.route('/users', methods=['GET'])
def get_users():
    """Get all available user IDs"""
    try:
        users = sorted(financial_api.user_features_df['user_id'].unique().tolist())
        return jsonify({
            "success": True,
            "users": users,
            "count": len(users)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/transactions/<user_id>', methods=['GET'])
def get_user_transactions(user_id):
    """Get all transactions for a specific user"""
    try:
        user_id = int(user_id)
        
        # Check if user exists
        if user_id not in financial_api.user_features_df['user_id'].values:
            return jsonify({
                "success": False,
                "error": f"User {user_id} not found"
            }), 404
        
        # Get user transactions
        user_transactions = financial_api.transactions_df[
            financial_api.transactions_df['user_id'] == user_id
        ].copy()
        
        if len(user_transactions) == 0:
            return jsonify({
                "success": False,
                "error": f"No transactions found for user {user_id}"
            }), 404
        
        # Convert datetime to string for JSON serialization
        user_transactions['transaction_date'] = user_transactions['transaction_date'].dt.strftime('%Y-%m-%d')
        
        # Convert to dict format
        transactions = user_transactions.to_dict('records')
        
        # Get transaction summary
        total_credit = user_transactions[user_transactions['transaction_type'] == 1]['transaction_amount'].sum()
        total_debit = user_transactions[user_transactions['transaction_type'] == 2]['transaction_amount'].sum()
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "transaction_count": len(transactions),
            "summary": {
                "total_credit": float(total_credit),
                "total_debit": float(total_debit),
                "net_flow": float(total_credit - total_debit),
                "date_range": {
                    "from": user_transactions['transaction_date'].min(),
                    "to": user_transactions['transaction_date'].max()
                }
            },
            "transactions": transactions
        })
        
    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid user ID format. Please provide a numeric user ID."
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/user/<user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    """Get user profile and statistics"""
    try:
        user_id = int(user_id)
        
        # Check if user exists
        if user_id not in financial_api.user_features_df['user_id'].values:
            return jsonify({
                "success": False,
                "error": f"User {user_id} not found"
            }), 404
        
        # Get user profile
        user_profile = financial_api.user_features_df[
            financial_api.user_features_df['user_id'] == user_id
        ].iloc[0]
        
        # Get monthly history
        user_monthly = financial_api.monthly_df[
            financial_api.monthly_df['user_id'] == user_id
        ]
        
        monthly_history = []
        if len(user_monthly) > 0:
            for _, row in user_monthly.iterrows():
                monthly_history.append({
                    "month": row['year_month'],
                    "expenditure": float(row['monthly_expenditure']),
                    "savings": float(row['monthly_savings']),
                    "income": float(row['monthly_income'])
                })
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "profile": {
                "primary_bank": user_profile['primary_bank'],
                "total_transactions": int(user_profile['total_transactions']),
                "total_credit": float(user_profile['total_credit']),
                "total_debit": float(user_profile['total_debit']),
                "net_flow": float(user_profile['net_flow']),
                "avg_balance": float(user_profile['avg_balance']),
                "max_balance": float(user_profile['max_balance']),
                "min_balance": float(user_profile['min_balance']),
                "unique_banks": int(user_profile['unique_banks']),
                "credit_debit_ratio": float(user_profile['credit_debit_ratio'])
            },
            "monthly_history": monthly_history
        })
        
    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid user ID format. Please provide a numeric user ID."
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/predict/expenditure', methods=['POST'])
def predict_expenditure():
    """Predict monthly expenditure for a user"""
    try:
        if financial_api.expenditure_model is None:
            return jsonify({
                "success": False,
                "error": "Expenditure model not loaded"
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        user_id = data.get('user_id')
        target_month = data.get('month', datetime.now().month)
        target_year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400
        
        # Make prediction
        prediction = make_prediction(int(user_id), target_month, target_year)
        if prediction is None:
            return jsonify({
                "success": False,
                "error": f"Could not make prediction for user {user_id}"
            }), 404
        
        predicted_expenditure, predicted_savings = prediction
        
        return jsonify({
            "success": True,
            "user_id": int(user_id),
            "prediction": {
                "expenditure": float(predicted_expenditure),
                "month": int(target_month),
                "year": int(target_year)
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/predict/savings', methods=['POST'])
def predict_savings():
    """Predict monthly savings for a user"""
    try:
        if financial_api.savings_model is None:
            return jsonify({
                "success": False,
                "error": "Savings model not loaded"
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        user_id = data.get('user_id')
        target_month = data.get('month', datetime.now().month)
        target_year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400
        
        # Make prediction
        prediction = make_prediction(int(user_id), target_month, target_year)
        if prediction is None:
            return jsonify({
                "success": False,
                "error": f"Could not make prediction for user {user_id}"
            }), 404
        
        predicted_expenditure, predicted_savings = prediction
        
        return jsonify({
            "success": True,
            "user_id": int(user_id),
            "prediction": {
                "savings": float(predicted_savings),
                "month": int(target_month),
                "year": int(target_year)
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/predict/both', methods=['POST'])
def predict_both():
    """Predict both monthly expenditure and savings for a user"""
    try:
        if financial_api.expenditure_model is None or financial_api.savings_model is None:
            return jsonify({
                "success": False,
                "error": "Models not loaded"
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        user_id = data.get('user_id')
        target_month = data.get('month', datetime.now().month)
        target_year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400
        
        # Make prediction
        prediction = make_prediction(int(user_id), target_month, target_year)
        if prediction is None:
            return jsonify({
                "success": False,
                "error": f"Could not make prediction for user {user_id}"
            }), 404
        
        predicted_expenditure, predicted_savings = prediction
        predicted_income = predicted_expenditure + predicted_savings
        savings_rate = (predicted_savings / predicted_income * 100) if predicted_income > 0 else 0
        
        return jsonify({
            "success": True,
            "user_id": int(user_id),
            "prediction": {
                "expenditure": float(predicted_expenditure),
                "savings": float(predicted_savings),
                "income": float(predicted_income),
                "savings_rate": float(savings_rate),
                "month": int(target_month),
                "year": int(target_year)
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

def make_prediction(user_id, target_month, target_year):
    """Helper function to make ML predictions"""
    try:
        # Check if user exists
        if user_id not in financial_api.user_features_df['user_id'].values:
            return None
        
        # Get user data
        user_profile = financial_api.user_features_df[
            financial_api.user_features_df['user_id'] == user_id
        ].iloc[0]
        
        user_transactions = financial_api.transactions_df[
            financial_api.transactions_df['user_id'] == user_id
        ]
        
        if len(user_transactions) == 0:
            return None
        
        # Calculate recent patterns (last 10 transactions)
        recent_txns = user_transactions.tail(10)
        
        # Calculate monthly averages from recent data
        num_months = 2  # Assume 2 months of data
        
        recent_income = recent_txns[recent_txns['transaction_type'] == 1]['transaction_amount'].sum() / num_months
        recent_installments = recent_txns[recent_txns['transaction_type'] == 6]['transaction_amount'].sum() / num_months
        recent_interest = recent_txns[recent_txns['transaction_type'] == 4]['transaction_amount'].sum() / num_months
        recent_num_txns = len(recent_txns) / num_months
        recent_avg_txn_amount = recent_txns['transaction_amount'].mean()
        
        # Transaction mode counts
        neft_count = len(recent_txns[recent_txns['transaction_mode'] == 'NEFT']) / num_months
        imps_count = len(recent_txns[recent_txns['transaction_mode'] == 'IMPS']) / num_months
        upi_count = len(recent_txns[recent_txns['transaction_mode'] == 'OTHERS']) / num_months
        ach_count = len(recent_txns[recent_txns['transaction_mode'] == 'ACH']) / num_months
        
        # Balance information
        end_balance = recent_txns['current_balance'].iloc[-1] if len(recent_txns) > 0 else 0
        avg_balance = recent_txns['current_balance'].mean()
        
        # Encode primary bank
        try:
            primary_bank_encoded = financial_api.label_encoder.transform([user_profile['primary_bank']])[0]
        except ValueError:
            primary_bank_encoded = 0
        
        # Create feature vector
        features = np.array([
            target_month,
            target_year,
            recent_income,
            recent_installments,
            recent_interest,
            recent_num_txns,
            recent_avg_txn_amount,
            neft_count,
            imps_count,
            upi_count,
            ach_count,
            end_balance,
            avg_balance,
            user_profile['total_credit'],
            user_profile['total_debit'],
            user_profile['credit_debit_ratio'],
            user_profile['unique_banks'],
            primary_bank_encoded,
            user_profile['avg_balance'],
            user_profile['max_balance'],
            user_profile['min_balance']
        ]).reshape(1, -1)
        
        # Scale features
        features_scaled = financial_api.scaler.transform(features)
        
        # Make predictions
        predicted_expenditure = max(0, financial_api.expenditure_model.predict(features_scaled)[0])
        predicted_savings = financial_api.savings_model.predict(features_scaled)[0]
        
        return predicted_expenditure, predicted_savings
        
    except Exception as e:
        print(f"Prediction error for user {user_id}: {e}")
        return None

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Financial Prediction API...")
    print("📊 Available endpoints:")
    print("  GET  /users - Get all user IDs")
    print("  GET  /transactions/<user_id> - Get user transactions")
    print("  GET  /user/<user_id>/profile - Get user profile")
    print("  POST /predict/expenditure - Predict expenditure")
    print("  POST /predict/savings - Predict savings") 
    print("  POST /predict/both - Predict both")
    print()
    app.run(host='0.0.0.0', port=5001, debug=True)
