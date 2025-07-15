import pandas as pd
import numpy as np
from datetime import datetime

def compute_wallet_features(df, save_to_csv=False, csv_path='../data/wallet_features.csv'):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    wallet_stats = df.groupby(['wallet_address', 'action'])['amount'].agg(['sum', 'count']).unstack(fill_value=0)
    
    features = pd.DataFrame()
    features['total_deposits'] = wallet_stats[('sum', 'deposit')]
    features['total_borrows'] = wallet_stats[('sum', 'borrow')]
    features['deposit_to_borrow_ratio'] = features['total_deposits'] / (features['total_borrows'] + 1e-6)
    
    features['num_repayments'] = wallet_stats[('count', 'repay')]
    features['num_liquidations'] = wallet_stats[('count', 'liquidationcall')]
    
    borrows = df[df['action'] == 'borrow'].copy()
    repays = df[df['action'] == 'repay'].copy()
    
    borrow_repay_pairs = pd.merge(
        borrows,
        repays,
        how='inner',
        left_on=['wallet_address', 'token_symbol'],
        right_on=['wallet_address', 'token_symbol'],
        suffixes=('_borrow', '_repay')
    )
    
    borrow_repay_pairs['duration'] = (borrow_repay_pairs['timestamp_repay'] - borrow_repay_pairs['timestamp_borrow']).dt.total_seconds() / (24 * 3600)
    
    avg_durations = borrow_repay_pairs.groupby('wallet_address')['duration'].mean()
    features['avg_borrow_duration'] = avg_durations.fillna(0)
    
    activity_span = df.groupby('wallet_address')['timestamp'].agg(['min', 'max'])
    features['activity_span_days'] = (activity_span['max'] - activity_span['min']).dt.total_seconds() / (24 * 3600)
    
    features['transaction_frequency'] = df.groupby('wallet_address').size() / features['activity_span_days'].clip(lower=1)
    
    features['redeem_to_deposit_ratio'] = wallet_stats[('count', 'redeemunderlying')] / (wallet_stats[('count', 'deposit')] + 1e-6)
    features['liquidation_ratio'] = features['num_liquidations'] / (wallet_stats[('count', 'borrow')] + 1e-6)
    
    latest_timestamp = df['timestamp'].max()
    last_activity = df.groupby('wallet_address')['timestamp'].max()
    features['last_activity_days_ago'] = (latest_timestamp - last_activity).dt.total_seconds() / (24 * 3600)
    
    features.index.name = 'wallet_address'
    result = features.reset_index()
    
    if save_to_csv:
        result.to_csv(csv_path, index=False)
    
    return result
