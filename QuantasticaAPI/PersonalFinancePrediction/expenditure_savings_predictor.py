import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import joblib

class ExpenditureSavingsPredictor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.expenditure_model = None
        self.savings_model = None
        self.feature_names = None
        
    def prepare_data(self, transactions_df, user_features_df):
        """
        Prepare data for training by creating monthly aggregations and features
        """
        # Convert transaction_date to datetime
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        transactions_df['year_month'] = transactions_df['transaction_date'].dt.to_period('M')
        
        # Create monthly aggregations for each user
        monthly_data = []
        
        for user_id in transactions_df['user_id'].unique():
            user_txns = transactions_df[transactions_df['user_id'] == user_id]
            user_profile = user_features_df[user_features_df['user_id'] == user_id].iloc[0]
            
            # Group by month
            for year_month, month_txns in user_txns.groupby('year_month'):
                # Calculate monthly expenditures (debits)
                monthly_expenditure = month_txns[month_txns['transaction_type'] == 2]['transaction_amount'].sum()
                
                # Calculate monthly income (credits)
                monthly_income = month_txns[month_txns['transaction_type'] == 1]['transaction_amount'].sum()
                
                # Calculate monthly savings (income - expenditure)
                monthly_savings = monthly_income - monthly_expenditure
                
                # Calculate other monthly features
                monthly_installments = month_txns[month_txns['transaction_type'] == 6]['transaction_amount'].sum()
                monthly_interest = month_txns[month_txns['transaction_type'] == 4]['transaction_amount'].sum()
                
                # Transaction patterns
                num_transactions = len(month_txns)
                avg_transaction_amount = month_txns['transaction_amount'].mean()
                
                # Mode of transactions
                neft_count = len(month_txns[month_txns['transaction_mode'] == 'NEFT'])
                imps_count = len(month_txns[month_txns['transaction_mode'] == 'IMPS'])
                upi_count = len(month_txns[month_txns['transaction_mode'] == 'OTHERS'])
                ach_count = len(month_txns[month_txns['transaction_mode'] == 'ACH'])
                
                # Balance information
                end_balance = month_txns['current_balance'].iloc[-1] if len(month_txns) > 0 else 0
                avg_balance = month_txns['current_balance'].mean()
                
                monthly_record = {
                    'user_id': user_id,
                    'year_month': str(year_month),
                    'month': year_month.month,
                    'year': year_month.year,
                    
                    # Target variables
                    'monthly_expenditure': monthly_expenditure,
                    'monthly_savings': monthly_savings,
                    'monthly_income': monthly_income,
                    
                    # Monthly features
                    'monthly_installments': monthly_installments,
                    'monthly_interest': monthly_interest,
                    'num_transactions': num_transactions,
                    'avg_transaction_amount': avg_transaction_amount,
                    'neft_count': neft_count,
                    'imps_count': imps_count,
                    'upi_count': upi_count,
                    'ach_count': ach_count,
                    'end_balance': end_balance,
                    'avg_balance': avg_balance,
                    
                    # User profile features
                    'total_credit': user_profile['total_credit'],
                    'total_debit': user_profile['total_debit'],
                    'credit_debit_ratio': user_profile['credit_debit_ratio'],
                    'unique_banks': user_profile['unique_banks'],
                    'primary_bank': user_profile['primary_bank'],
                    'user_avg_balance': user_profile['avg_balance'],
                    'user_max_balance': user_profile['max_balance'],
                    'user_min_balance': user_profile['min_balance']
                }
                
                monthly_data.append(monthly_record)
        
        monthly_df = pd.DataFrame(monthly_data)
        return monthly_df
    
    def create_features(self, monthly_df):
        """
        Create feature matrix for ML models
        """
        # Encode categorical features
        monthly_df_encoded = monthly_df.copy()
        monthly_df_encoded['primary_bank_encoded'] = self.label_encoder.fit_transform(monthly_df_encoded['primary_bank'])
        
        # Select features for modeling
        feature_columns = [
            'month', 'year', 'monthly_income', 'monthly_installments', 'monthly_interest',
            'num_transactions', 'avg_transaction_amount', 'neft_count', 'imps_count', 
            'upi_count', 'ach_count', 'end_balance', 'avg_balance',
            'total_credit', 'total_debit', 'credit_debit_ratio', 'unique_banks',
            'primary_bank_encoded', 'user_avg_balance', 'user_max_balance', 'user_min_balance'
        ]
        
        self.feature_names = feature_columns
        X = monthly_df_encoded[feature_columns]
        
        # Handle any missing values
        X = X.fillna(0)
        
        return X
    
    def train_models(self, monthly_df):
        """
        Train ML models for expenditure and savings prediction
        """
        # Prepare features
        X = self.create_features(monthly_df)
        
        # Target variables
        y_expenditure = monthly_df['monthly_expenditure']
        y_savings = monthly_df['monthly_savings']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_exp_train, y_exp_test, y_sav_train, y_sav_test = train_test_split(
            X_scaled, y_expenditure, y_savings, test_size=0.2, random_state=42
        )
        
        # Train expenditure model
        print("Training expenditure prediction model...")
        self.expenditure_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.expenditure_model.fit(X_train, y_exp_train)
        
        # Train savings model  
        print("Training savings prediction model...")
        self.savings_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.savings_model.fit(X_train, y_sav_train)
        
        # Evaluate models
        exp_pred = self.expenditure_model.predict(X_test)
        sav_pred = self.savings_model.predict(X_test)
        
        print("\nModel Performance:")
        print("Expenditure Model:")
        print(f"  MAE: {mean_absolute_error(y_exp_test, exp_pred):.2f}")
        print(f"  RMSE: {np.sqrt(mean_squared_error(y_exp_test, exp_pred)):.2f}")
        print(f"  R²: {r2_score(y_exp_test, exp_pred):.3f}")
        
        print("\nSavings Model:")
        print(f"  MAE: {mean_absolute_error(y_sav_test, sav_pred):.2f}")
        print(f"  RMSE: {np.sqrt(mean_squared_error(y_sav_test, sav_pred)):.2f}")
        print(f"  R²: {r2_score(y_sav_test, sav_pred):.3f}")
        
        # Feature importance
        self.plot_feature_importance()
        
        return X_test, y_exp_test, y_sav_test, exp_pred, sav_pred
    
    def plot_feature_importance(self):
        """
        Plot feature importance for both models
        """
        plt.figure(figsize=(15, 10))
        
        # Expenditure model feature importance
        plt.subplot(2, 1, 1)
        exp_importance = self.expenditure_model.feature_importances_
        sorted_idx = np.argsort(exp_importance)[-15:]  # Top 15 features
        plt.barh(range(len(sorted_idx)), exp_importance[sorted_idx])
        plt.yticks(range(len(sorted_idx)), [self.feature_names[i] for i in sorted_idx])
        plt.title('Top 15 Features - Expenditure Prediction Model')
        plt.xlabel('Feature Importance')
        
        # Savings model feature importance
        plt.subplot(2, 1, 2)
        sav_importance = self.savings_model.feature_importances_
        sorted_idx = np.argsort(sav_importance)[-15:]  # Top 15 features
        plt.barh(range(len(sorted_idx)), sav_importance[sorted_idx])
        plt.yticks(range(len(sorted_idx)), [self.feature_names[i] for i in sorted_idx])
        plt.title('Top 15 Features - Savings Prediction Model')
        plt.xlabel('Feature Importance')
        
        plt.tight_layout()
        plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
        print("\nFeature importance plot saved as 'feature_importance.png'")
        
    def predict_user_monthly(self, user_id, transactions_df, user_features_df, target_month, target_year):
        """
        Predict monthly expenditure and savings for a specific user
        """
        if self.expenditure_model is None or self.savings_model is None:
            raise ValueError("Models not trained yet. Call train_models() first.")
        
        # Get user profile
        user_profile = user_features_df[user_features_df['user_id'] == user_id].iloc[0]
        
        # Calculate recent patterns (last 2 months)
        recent_txns = transactions_df[
            (transactions_df['user_id'] == user_id) & 
            (pd.to_datetime(transactions_df['transaction_date']).dt.year >= target_year - 1)
        ]
        
        if len(recent_txns) == 0:
            print(f"No recent transaction data found for user {user_id}")
            return None, None
        
        # Calculate average monthly patterns from recent data
        recent_income = recent_txns[recent_txns['transaction_type'] == 1]['transaction_amount'].sum() / 2
        recent_installments = recent_txns[recent_txns['transaction_type'] == 6]['transaction_amount'].sum() / 2
        recent_interest = recent_txns[recent_txns['transaction_type'] == 4]['transaction_amount'].sum() / 2
        recent_num_txns = len(recent_txns) / 2
        recent_avg_txn_amount = recent_txns['transaction_amount'].mean()
        
        # Create feature vector
        features = {
            'month': target_month,
            'year': target_year,
            'monthly_income': recent_income,
            'monthly_installments': recent_installments,
            'monthly_interest': recent_interest,
            'num_transactions': recent_num_txns,
            'avg_transaction_amount': recent_avg_txn_amount,
            'neft_count': len(recent_txns[recent_txns['transaction_mode'] == 'NEFT']) / 2,
            'imps_count': len(recent_txns[recent_txns['transaction_mode'] == 'IMPS']) / 2,
            'upi_count': len(recent_txns[recent_txns['transaction_mode'] == 'OTHERS']) / 2,
            'ach_count': len(recent_txns[recent_txns['transaction_mode'] == 'ACH']) / 2,
            'end_balance': recent_txns['current_balance'].iloc[-1] if len(recent_txns) > 0 else 0,
            'avg_balance': recent_txns['current_balance'].mean(),
            'total_credit': user_profile['total_credit'],
            'total_debit': user_profile['total_debit'],
            'credit_debit_ratio': user_profile['credit_debit_ratio'],
            'unique_banks': user_profile['unique_banks'],
            'primary_bank_encoded': self.label_encoder.transform([user_profile['primary_bank']])[0],
            'user_avg_balance': user_profile['avg_balance'],
            'user_max_balance': user_profile['max_balance'],
            'user_min_balance': user_profile['min_balance']
        }
        
        # Create feature vector
        X_pred = np.array([list(features.values())])
        X_pred_scaled = self.scaler.transform(X_pred)
        
        # Make predictions
        predicted_expenditure = self.expenditure_model.predict(X_pred_scaled)[0]
        predicted_savings = self.savings_model.predict(X_pred_scaled)[0]
        
        return predicted_expenditure, predicted_savings
    
    def save_models(self):
        """
        Save trained models
        """
        joblib.dump(self.expenditure_model, 'expenditure_model.pkl')
        joblib.dump(self.savings_model, 'savings_model.pkl')
        joblib.dump(self.scaler, 'scaler.pkl')
        joblib.dump(self.label_encoder, 'label_encoder.pkl')
        print("Models saved successfully!")

def main():
    # Load data
    print("Loading data...")
    transactions_df = pd.read_csv('bank_transactions_detailed.csv')
    user_features_df = pd.read_csv('bank_transactions_user_features.csv')
    
    # Initialize predictor
    predictor = ExpenditureSavingsPredictor()
    
    # Prepare monthly data
    print("Preparing monthly aggregated data...")
    monthly_df = predictor.prepare_data(transactions_df, user_features_df)
    
    print(f"Monthly data shape: {monthly_df.shape}")
    print("\nSample monthly data:")
    print(monthly_df[['user_id', 'year_month', 'monthly_expenditure', 'monthly_savings', 'monthly_income']].head())
    
    # Train models
    print("\nTraining ML models...")
    X_test, y_exp_test, y_sav_test, exp_pred, sav_pred = predictor.train_models(monthly_df)
    
    # Save models
    predictor.save_models()
    
    # Make sample predictions for each user
    print("\nSample predictions for next month:")
    print("-" * 80)
    print(f"{'User ID':<12} {'Predicted Expenditure':<20} {'Predicted Savings':<18} {'Net Flow':<10}")
    print("-" * 80)
    
    for user_id in transactions_df['user_id'].unique()[:5]:  # First 5 users
        try:
            pred_exp, pred_sav = predictor.predict_user_monthly(
                user_id, transactions_df, user_features_df, 8, 2024  # August 2024
            )
            if pred_exp is not None:
                net_flow = pred_sav
                print(f"{user_id:<12} {pred_exp:>18.2f} {pred_sav:>16.2f} {net_flow:>8.2f}")
        except Exception as e:
            print(f"{user_id:<12} Error: {str(e)}")
    
    # Save monthly data for further analysis
    monthly_df.to_csv('monthly_financial_data.csv', index=False)
    print(f"\nMonthly aggregated data saved as 'monthly_financial_data.csv'")

if __name__ == "__main__":
    main()
