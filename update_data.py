import yfinance as yf
import warnings
import time
import os
import json
from datetime import datetime

warnings.simplefilter("ignore", category=FutureWarning)

# Configuration
PAIRS = {
    'GU': {'symbol': 'GBPUSD=X', 'levels': [1.40, 1.31400], 'thresholds': [40, 100]},
    'GJ': {'symbol': 'GBPJPY=X', 'levels': [198.257, 191.897], 'thresholds': [50, 100]},
    'GC': {'symbol': 'GBPCAD=X', 'levels': [1.87790, 1.79829], 'thresholds': [50, 100]},
    'EU': {'symbol': 'EURUSD=X', 'levels': [1.20, 1.07330], 'thresholds': [40, 100]},
    'EJ': {'symbol': 'EURJPY=X', 'levels': [166.102, 160.984], 'thresholds': [60, 100]},
    'EG': {'symbol': 'EURGBP=X', 'levels': [0.85410, 0.82225], 'thresholds': [50, 100]},
    'AU': {'symbol': 'AUDUSD=X', 'levels': [0.65498, 0.59140], 'thresholds': [55, 100]},
    'AJ': {'symbol': 'AUDJPY=X', 'levels': [95.648, 90.590], 'thresholds': [45, 100]}
}

def calculate_pips(pair_key, quote):
    """Calculate pip distances with pair-specific multipliers"""
    pair = PAIRS[pair_key]
    if 'JPY' in pair_key:
        multiplier = 100  # JPY pairs
    else:
        multiplier = 10000  # Other pairs
        
    dis0 = (pair['levels'][0] - quote) * multiplier
    dis1 = (quote - pair['levels'][1]) * multiplier
    return round(dis0), round(dis1)

def get_status(value, thresholds):
    """Determine status based on thresholds"""
    if value <= thresholds[0]:
        return 'critical'
    elif value <= thresholds[1]:
        return 'warning'
    return 'normal'

def main():
    """Main function to fetch data and generate output"""
    try:
        # Download forex data
        symbols = [data['symbol'] for data in PAIRS.values()]
        df = yf.download(' '.join(symbols), period='1d', progress=False, auto_adjust=True)
        
        if df.empty or 'Close' not in df:
            raise ValueError("No data returned from Yahoo Finance")
            
        df = df['Close']
        results = {}
        timestamp = datetime.utcnow().isoformat()
        
        # Process each pair
        for pair_key, pair_data in PAIRS.items():
            symbol = pair_data['symbol']
            if symbol not in df or df[symbol].empty:
                continue
                
            quote = df[symbol][0]
            dis0, dis1 = calculate_pips(pair_key, quote)
            
            results[pair_key] = {
                'quote': quote,
                'distances': [
                    {'value': dis0, 'status': get_status(dis0, pair_data['thresholds'])},
                    {'value': dis1, 'status': get_status(dis1, pair_data['thresholds'])}
                ],
                'timestamp': timestamp
            }
        
        # Save results
        with open('data.json', 'w') as f:
            json.dump(results, f)
            
        print("Data updated successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        # Create empty data file to prevent frontend errors
        with open('data.json', 'w') as f:
            json.dump({}, f)

if __name__ == "__main__":
    main()
