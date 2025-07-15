# Aave V2 Wallet Credit Scoring System

## Project Overview

This project implements a credit scoring system for Aave V2 protocol wallets. The system analyzes historical transaction behavior to assign credit scores between 0 and 1000, where higher scores indicate more responsible and reliable usage patterns. The scoring system helps identify potential risks and responsible users in the Aave lending protocol.

## Dataset Description

The system uses raw transaction data from Aave V2 protocol, containing the following fields:
- `wallet_address`: Unique identifier for each wallet
- `action`: Type of transaction (deposit, borrow, repay, redeemunderlying, liquidationcall)
- `amount`: Transaction amount
- `token_symbol`: Token involved in the transaction
- `timestamp`: Transaction timestamp

The dataset contains approximately 100K raw transactions from various wallets interacting with the Aave V2 protocol.

## Features Used for Scoring

The scoring system analyzes the following features for each wallet:

1. **Transaction Behavior**
   - `total_deposits`: Total amount deposited
   - `total_borrows`: Total amount borrowed
   - `deposit_to_borrow_ratio`: Ratio of deposits to borrows
   - `num_repayments`: Number of repayment transactions
   - `num_liquidations`: Number of liquidation calls

2. **Time-based Metrics**
   - `avg_borrow_duration`: Average duration of borrow periods
   - `activity_span_days`: Time between first and last transaction
   - `transaction_frequency`: Number of transactions per active day
   - `last_activity_days_ago`: Days since last activity

3. **Risk Indicators**
   - `liquidation_ratio`: Ratio of liquidations to borrows
   - `redeem_to_deposit_ratio`: Ratio of redeems to deposits

## Scoring Formula Summary

The scoring formula starts with a baseline score of 500 and adjusts based on the following criteria:

- **Positive Factors**
  - +200 if deposit_to_borrow_ratio > 1.5
  - +100 if num_repayments > num_borrows
  - +50 if avg_borrow_duration > 10 days
  - +50 if activity_span_days > 90 days

- **Negative Factors**
  - -300 if liquidation_ratio > 0.5
  - -100 if last_activity_days_ago < 1 (potential bot activity)

The final score is clamped between 0 and 1000.

## How to Run the Project

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run the Scoring Pipeline**
```bash
python src/main.py --input data/user-transactions.json --output wallet_scores.csv
```

3. **Analyze Results**
- Open `notebooks/EDA.ipynb` in Jupyter Notebook
- Run all cells to analyze score distribution and wallet behavior

## Project Structure
```
aave-credit-scoring/
├── src/
│   ├── feature_engineering.py    # Feature extraction logic
│   ├── scoring_model.py         # Credit scoring model implementation
│   └── main.py                  # Main pipeline execution
├── data/
│   └── user-transactions.json   # Raw transaction data
├── notebooks/
│   └── EDA.ipynb               # Exploratory Data Analysis
├── analysis/
│   └── score_distribution.png  # Score distribution visualization
└── requirements.txt           # Project dependencies
```

## Output Files

1. `wallet_scores.csv`: Contains wallet addresses and their credit scores
2. `analysis/score_distribution.png`: Visualization of score distribution
3. Score distribution statistics and risk categorization in the EDA notebook

## Risk Categories

Based on the score ranges:
- 0-399: High Risk (Potential bots or high-risk behavior)
- 400-599: Medium Risk (Needs monitoring)
- 600-1000: Low Risk (Responsible users)

## Requirements

- Python 3.8+
- Required packages (specified in requirements.txt):
  - pandas
  - numpy
  - scikit-learn
  - matplotlib
  - seaborn
  - python-dotenv

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"# DeFi" 
