import pandas as pd
import numpy as np
from typing import Tuple

def score_wallets(feature_df: pd.DataFrame) -> pd.DataFrame:
    scores = pd.DataFrame({
        'wallet_address': feature_df['wallet_address'],
        'score': 500
    })
    
    scores.loc[feature_df['deposit_to_borrow_ratio'] > 1.5, 'score'] += 200
    scores.loc[feature_df['num_repayments'] > feature_df['total_borrows'], 'score'] += 100
    scores.loc[feature_df['liquidation_ratio'] > 0.5, 'score'] -= 300
    scores.loc[feature_df['avg_borrow_duration'] > 10, 'score'] += 50
    scores.loc[feature_df['last_activity_days_ago'] < 1, 'score'] -= 100
    scores.loc[feature_df['activity_span_days'] > 90, 'score'] += 50
    
    scores['score'] = scores['score'].clip(0, 1000)
    score_distribution = analyze_score_distribution(scores)
    
    return scores, score_distribution

def analyze_score_distribution(scores_df: pd.DataFrame) -> dict:
    return {
        'score_distribution': {
            '0-200': len(scores_df[(scores_df['score'] >= 0) & (scores_df['score'] < 200)]),
            '200-400': len(scores_df[(scores_df['score'] >= 200) & (scores_df['score'] < 400)]),
            '400-600': len(scores_df[(scores_df['score'] >= 400) & (scores_df['score'] < 600)]),
            '600-800': len(scores_df[(scores_df['score'] >= 600) & (scores_df['score'] < 800)]),
            '800-1000': len(scores_df[(scores_df['score'] >= 800) & (scores_df['score'] <= 1000)])
        },
        'risk_categories': {
            'high_risk': len(scores_df[scores_df['score'] < 400]),
            'medium_risk': len(scores_df[(scores_df['score'] >= 400) & (scores_df['score'] < 600)]),
            'low_risk': len(scores_df[scores_df['score'] >= 600])
        }
    }

def get_score_reasons(wallet_address: str, feature_df: pd.DataFrame, scores_df: pd.DataFrame) -> dict:
    wallet_features = feature_df[feature_df['wallet_address'] == wallet_address]
    wallet_score = scores_df[scores_df['wallet_address'] == wallet_address]
    
    reasons = []
    
    if wallet_features['deposit_to_borrow_ratio'].iloc[0] > 1.5:
        reasons.append(('+200', 'High deposit-to-borrow ratio'))
    if wallet_features['num_repayments'].iloc[0] > wallet_features['total_borrows'].iloc[0]:
        reasons.append(('+100', 'Good repayment history'))
    if wallet_features['liquidation_ratio'].iloc[0] > 0.5:
        reasons.append(('-300', 'High liquidation risk'))
    if wallet_features['avg_borrow_duration'].iloc[0] > 10:
        reasons.append(('+50', 'Long-term borrow duration'))
    if wallet_features['last_activity_days_ago'].iloc[0] < 1:
        reasons.append(('-100', 'Potential bot activity'))
    if wallet_features['activity_span_days'].iloc[0] > 90:
        reasons.append(('+50', 'Long-term activity'))
    
    return {
        'wallet_address': wallet_address,
        'final_score': wallet_score['score'].iloc[0],
        'reasons': reasons
    }
