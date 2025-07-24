import yfinance as yf
import time

def get_static_stocks():
    with open('static_stocks.txt', 'r') as f:
        return [line.strip() for line in f.readlines()]

def filter_stocks(tickers, rules=None):
    """
    Filters a list of tickers based on a set of rules.
    
    Args:
        tickers (list): A list of dictionaries, where each dictionary contains
                        'symbol' and 'time' for an earnings ticker.
        rules (dict): A dictionary of rules to apply. Currently supports:
                      - 'use_static_list': bool, if True, filters against a static list of stocks.
    
    Returns:
        list: A filtered list of tickers that meet all specified rules.
    """
    if rules is None:
        rules = {}
    
    static_stocks = []
    if rules.get('use_static_list'):
        static_stocks = get_static_stocks()

    filtered_tickers = []
    
    for ticker_info in tickers:
        symbol = ticker_info['symbol']
        include_ticker = True
        
        if rules.get('use_static_list') and symbol not in static_stocks:
            include_ticker = False
        
        if include_ticker:
            filtered_tickers.append(ticker_info)
    
    return filtered_tickers