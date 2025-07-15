import argparse
import json
import pandas as pd
from datetime import datetime
from src.feature_engineering import compute_wallet_features
from src.scoring_model import score_wallets
import logging
from pathlib import Path

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def load_transactions(input_path: str) -> pd.DataFrame:
    with open(input_path, 'r') as f:
        data = json.load(f)

    # If the file is a dict with a single key, extract the list
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                data = v
                break

    # Normalize each record
    records = []
    for tx in data:
        # Defensive: skip if required fields are missing
        if 'userWallet' not in tx or 'action' not in tx or 'actionData' not in tx or 'timestamp' not in tx:
            continue
        action_data = tx['actionData']
        # Defensive: skip if nested fields are missing
        if 'amount' not in action_data or 'assetSymbol' not in action_data:
            continue
        # Convert amount to float (assume it's in wei, so divide by 1e18)
        try:
            amount = float(action_data['amount'])
            if amount > 1e18:  # Heuristic: if very large, assume it's in wei
                amount = amount / 1e18
        except Exception:
            amount = None
        # Convert timestamp to ISO string
        try:
            ts = int(tx['timestamp'])
            timestamp = datetime.utcfromtimestamp(ts).isoformat() + 'Z'
        except Exception:
            timestamp = None
        records.append({
            'wallet_address': tx['userWallet'],
            'action': tx['action'],
            'amount': amount,
            'token_symbol': action_data['assetSymbol'],
            'timestamp': timestamp
        })

    df = pd.DataFrame(records)
    required_columns = ['wallet_address', 'action', 'amount', 'token_symbol', 'timestamp']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def save_scores(scores_df: pd.DataFrame, output_path: str):
    try:
        scores_df.to_csv(output_path, index=False)
        logging.info(f"Scores saved to {output_path}")
    except Exception as e:
        logging.error(f"Error saving scores: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Aave Wallet Credit Scoring')
    parser.add_argument('--input', type=str, default='data/user-transactions.json',
                      help='Path to input JSON file containing transactions')
    parser.add_argument('--output', type=str, default='wallet_scores.csv',
                      help='Path to output CSV file for scores')
    
    args = parser.parse_args()
    setup_logging()
    
    try:
        logging.info(f"Loading transactions from {args.input}")
        transactions_df = load_transactions(args.input)
        
        logging.info("Computing wallet features...")
        features_df = compute_wallet_features(transactions_df, save_to_csv=True, csv_path='data/wallet_features.csv')
        
        logging.info("Calculating credit scores...")
        scores_df, score_distribution = score_wallets(features_df)
        
        logging.info(f"Saving scores to {args.output}")
        save_scores(scores_df, args.output)
        
        logging.info("\nScore Distribution:")
        for range_, count in score_distribution['score_distribution'].items():
            logging.info(f"{range_}: {count} wallets")
        
        logging.info("\nRisk Categories:")
        for category, count in score_distribution['risk_categories'].items():
            logging.info(f"{category}: {count} wallets")
            
        logging.info("\nScoring process completed successfully!")
        
    except Exception as e:
        logging.error(f"Error in scoring process: {str(e)}")
        raise

if __name__ == "__main__":
    main()
