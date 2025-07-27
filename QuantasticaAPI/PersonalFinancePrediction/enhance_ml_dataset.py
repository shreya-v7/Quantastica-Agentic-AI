import json
import csv
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from collections import defaultdict

def create_enhanced_ml_dataset(csv_file):
    """
    Create an enhanced dataset with additional features derived from transaction data
    """
    # Read the basic CSV file
    df = pd.read_csv(csv_file)
    
    # Convert transaction_date to datetime
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Create additional features
    df['month'] = df['transaction_date'].dt.month
    df['year'] = df['transaction_date'].dt.year
    df['day_of_week'] = df['transaction_date'].dt.dayofweek
    df['day_of_month'] = df['transaction_date'].dt.day
    
    # Calculate transaction patterns per user
    user_features = []
    
    for user_id in df['user_id'].unique():
        user_data = df[df['user_id'] == user_id].copy()
        
        # Basic statistics
        total_transactions = len(user_data)
        total_credit = user_data[user_data['transaction_type'] == 1]['transaction_amount'].sum()
        total_debit = user_data[user_data['transaction_type'] == 2]['transaction_amount'].sum()
        avg_transaction_amount = user_data['transaction_amount'].mean()
        max_transaction_amount = user_data['transaction_amount'].max()
        min_transaction_amount = user_data['transaction_amount'].min()
        
        # Transaction type distribution
        credit_count = len(user_data[user_data['transaction_type'] == 1])
        debit_count = len(user_data[user_data['transaction_type'] == 2])
        installment_count = len(user_data[user_data['transaction_type'] == 6])
        interest_count = len(user_data[user_data['transaction_type'] == 4])
        others_count = len(user_data[user_data['transaction_type'] == 8])
        
        # Transaction mode distribution
        mode_counts = user_data['transaction_mode'].value_counts().to_dict()
        neft_count = mode_counts.get('NEFT', 0)
        imps_count = mode_counts.get('IMPS', 0)
        upi_count = mode_counts.get('OTHERS', 0)  # UPI transactions are in OTHERS
        ach_count = mode_counts.get('ACH', 0)
        ft_count = mode_counts.get('FT', 0)
        
        # Bank diversity
        unique_banks = user_data['bank'].nunique()
        primary_bank = user_data['bank'].value_counts().index[0] if len(user_data) > 0 else 'Unknown'
        
        # Balance patterns
        avg_balance = user_data['current_balance'].mean()
        max_balance = user_data['current_balance'].max()
        min_balance = user_data['current_balance'].min()
        
        # Monthly patterns
        monthly_avg_credit = user_data[user_data['transaction_type'] == 1].groupby('month')['transaction_amount'].sum().mean()
        monthly_avg_debit = user_data[user_data['transaction_type'] == 2].groupby('month')['transaction_amount'].sum().mean()
        
        user_features.append({
            'user_id': user_id,
            'total_transactions': total_transactions,
            'total_credit': total_credit,
            'total_debit': total_debit,
            'net_flow': total_credit - total_debit,
            'avg_transaction_amount': avg_transaction_amount,
            'max_transaction_amount': max_transaction_amount,
            'min_transaction_amount': min_transaction_amount,
            'credit_count': credit_count,
            'debit_count': debit_count,
            'installment_count': installment_count,
            'interest_count': interest_count,
            'others_count': others_count,
            'credit_debit_ratio': credit_count / debit_count if debit_count > 0 else 0,
            'neft_count': neft_count,
            'imps_count': imps_count,
            'upi_count': upi_count,
            'ach_count': ach_count,
            'ft_count': ft_count,
            'unique_banks': unique_banks,
            'primary_bank': primary_bank,
            'avg_balance': avg_balance,
            'max_balance': max_balance,
            'min_balance': min_balance,
            'monthly_avg_credit': monthly_avg_credit if not pd.isna(monthly_avg_credit) else 0,
            'monthly_avg_debit': monthly_avg_debit if not pd.isna(monthly_avg_debit) else 0
        })
    
    # Create user features DataFrame
    user_features_df = pd.DataFrame(user_features)
    
    # Save enhanced datasets
    df.to_csv('bank_transactions_detailed.csv', index=False)
    user_features_df.to_csv('bank_transactions_user_features.csv', index=False)
    
    print("Enhanced datasets created:")
    print(f"1. bank_transactions_detailed.csv - Detailed transaction data with additional date features")
    print(f"2. bank_transactions_user_features.csv - Aggregated user-level features for ML modeling")
    print(f"\nUser features dataset shape: {user_features_df.shape}")
    print(f"Detailed transactions dataset shape: {df.shape}")
    
    return df, user_features_df

def main():
    # Create enhanced ML dataset
    print("Creating enhanced ML datasets...")
    df, user_features_df = create_enhanced_ml_dataset('bank_transactions_ml_data.csv')
    
    print("\nSample user features:")
    print(user_features_df.head(3).to_string())

if __name__ == "__main__":
    main()
