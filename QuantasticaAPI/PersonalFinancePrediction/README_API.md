# Financial Prediction API Server

## 🚀 Quick Start

### 1. Start the Server
```bash
python financial_api_server.py
```

The server will start on `http://localhost:5000`

### 2. Available Endpoints

#### GET Endpoints:
- `GET /` - API information and available endpoints
- `GET /users` - Get all available user IDs
- `GET /transactions/<user_id>` - Get all transactions for a specific user
- `GET /user/<user_id>/profile` - Get user profile and statistics

#### POST Endpoints (JSON payload required):
- `POST /predict/expenditure` - Predict monthly expenditure
- `POST /predict/savings` - Predict monthly savings  
- `POST /predict/both` - Predict both expenditure and savings

## 📋 API Usage Examples

### Get All Users
```bash
curl http://localhost:5000/users
```

### Get User Transactions
```bash
curl http://localhost:5000/transactions/1010101010
```

### Get User Profile
```bash
curl http://localhost:5000/user/1010101010/profile
```

### Predict Expenditure
```bash
curl -X POST http://localhost:5000/predict/expenditure \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1010101010, "month": 8, "year": 2024}'
```

### Predict Savings
```bash
curl -X POST http://localhost:5000/predict/savings \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1010101010, "month": 8, "year": 2024}'
```

### Predict Both Expenditure and Savings
```bash
curl -X POST http://localhost:5000/predict/both \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1010101010, "month": 8, "year": 2024}'
```

## 🐍 Python Usage Example

```python
import requests
import json

# Get all users
response = requests.get('http://localhost:5000/users')
users = response.json()['users']
print(f"Available users: {users}")

# Get transactions for a user
user_id = users[0]
response = requests.get(f'http://localhost:5000/transactions/{user_id}')
transactions_data = response.json()
print(f"User {user_id} has {transactions_data['transaction_count']} transactions")

# Make prediction
payload = {
    "user_id": user_id,
    "month": 8,    # August
    "year": 2024
}

response = requests.post('http://localhost:5000/predict/both', json=payload)
result = response.json()

if result['success']:
    prediction = result['prediction']
    print(f"Predictions for {prediction['month']}/{prediction['year']}:")
    print(f"  Expenditure: ₹{prediction['expenditure']:,.2f}")
    print(f"  Savings: ₹{prediction['savings']:,.2f}")
    print(f"  Income: ₹{prediction['income']:,.2f}")
    print(f"  Savings Rate: {prediction['savings_rate']:.1f}%")
else:
    print(f"Error: {result['error']}")
```

## 🧪 Test the API

Run the test client:
```bash
python api_test_client.py test
```

Or see usage examples:
```bash
python api_test_client.py
```

## 📊 Available Users

The system has data for the following user IDs:
- 1010101010 (State Bank of India)
- 1212121212 (Punjab National Bank) 
- 1313131313 (HDFC Bank)
- 1414141414 (ICICI Bank)
- 2020202020 (Kotak Mahindra Bank)
- 2121212121 (Union Bank)
- 2222222222 (IDFC First Bank)
- 2525252525 (IDFC Bank)
- 3333333333 (State Bank of India)
- 4444444444 (HDFC Bank)
- 5555555555 (ICICI Bank)
- 6666666666 (Punjab National Bank)
- 7777777777 (Kotak Mahindra Bank)
- 8888888888 (Union Bank)

## 📝 Request/Response Format

### Prediction Request Format:
```json
{
    "user_id": 1010101010,
    "month": 8,      // Optional, defaults to current month
    "year": 2024     // Optional, defaults to current year
}
```

### Prediction Response Format:
```json
{
    "success": true,
    "user_id": 1010101010,
    "prediction": {
        "expenditure": 45000.50,
        "savings": 25000.25,
        "income": 70000.75,
        "savings_rate": 35.7,
        "month": 8,
        "year": 2024
    }
}
```

## ⚡ Model Performance

- **Expenditure Model**: 98.7% accuracy (R² = 0.987)
- **Savings Model**: 94.8% accuracy (R² = 0.948)
- Based on transaction patterns, bank relationships, and user behavior
- Uses 21 features including transaction types, amounts, modes, and balances

## 🛠️ Files Required

Make sure these files exist before starting the server:
- `expenditure_model.pkl` - Trained expenditure prediction model
- `savings_model.pkl` - Trained savings prediction model
- `scaler.pkl` - Feature scaling transformer
- `label_encoder.pkl` - Bank name encoder
- `bank_transactions_detailed.csv` - Transaction data with date features
- `bank_transactions_user_features.csv` - User profile features
- `monthly_financial_data.csv` - Monthly aggregated data

Run `python expenditure_savings_predictor.py` first if these files don't exist.
