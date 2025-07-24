import argparse
from calculator import compute_recommendation
import datetime
import pandas as pd
import sys
from finance_calendars import finance_calendars
import time  # For rate limiting
from utils import filter_stocks  # Added import

def get_earnings_for_date(date_str=None):
    """
    Fetch all tickers with earnings for the specified date using yahoo_earnings_calendar.
    If no date is provided, use today's date.
    """
    
    if date_str is None:
        date = datetime.date.today()
        # Format for display
        date_display = date.strftime('%b %d %Y')
    else:
        try:
            # Try to parse in YYYY-MM-DD format first
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            date_display = date.strftime('%b %d %Y')
        except ValueError:
            print(f"Error: Invalid date format. Please use YYYY-MM-DD or Month Day Year (e.g., 'Jul 24 2025')")
            return []
            
    try:
        # Use finance_calendars to get earnings data
        earnings_df = finance_calendars.get_earnings_by_date(date)
        
        # Set the date range for the earnings (start of day to end of day)
        date_from = datetime.datetime.combine(date, datetime.datetime.min.time())
        date_to = datetime.datetime.combine(date, datetime.datetime.max.time())
        
        print(f"Fetching earnings for {date_display}...")
        
        # Check if earnings_df is valid
        if earnings_df.empty:
            print(f"\nNo earnings data found for {date_display}")
            print("This could be because:")
            print("1. The market is closed on this date")
            print("2. Earnings data isn't yet available")
            print("3. The date is too far in future")
            return []
            
        # Convert DataFrame to list of symbol/time dicts
        tickers = []
        for symbol, row in earnings_df.iterrows():
            # Extract time from the row
            time = row.get('time', 'time-not-supplied')
            tickers.append({
                'symbol': symbol,
                'time': time
            })
            
        if tickers:
            print(f"Successfully found {len(tickers)} earnings reports for {date_display}")
            return tickers
            
        else:
            print(f"\nNo earnings data found for {date_display}")
            print("Possible reasons:")
            print("1. Market closed on this date")
            print("2. Earnings data unavailable")
            print("3. Date too far in future")
            return []
            
    except Exception as e:
        print(f"\nError fetching earnings data: {str(e)}")
        return []

def analyze_earnings_plays(tickers):
    """
    Analyze each ticker using the calculator logic and categorize them.
    """
    recommended = []
    consider = []
    avoid = []
    errors = []
    
    total = len(tickers)
    for idx, ticker_info in enumerate(tickers, 1):
        symbol = ticker_info['symbol']
        print(f"\rAnalyzing {symbol} ({idx}/{total})...", end="", flush=True)
        
        try:
            result = compute_recommendation(symbol)
            # Add delay to avoid rate limiting (1 second per request)
            time.sleep(1)
            
            if isinstance(result, dict):  # Successful analysis
                avg_volume_bool = result['avg_volume']
                iv30_rv30_bool = result['iv30_rv30']
                ts_slope_bool = result['ts_slope_0_45']
                expected_move = result['expected_move']
                
                recommendation = "Recommended" if (avg_volume_bool and iv30_rv30_bool and ts_slope_bool) else \
                              "Consider" if (ts_slope_bool and ((avg_volume_bool and not iv30_rv30_bool) or (iv30_rv30_bool and not avg_volume_bool))) else "Avoid"
                
                ticker_info = {
                    'symbol': symbol,
                    'time': ticker_info['time'],
                    'expected_move': expected_move,
                    'recommendation': recommendation
                }
                
                if recommendation == "Recommended":
                    recommended.append(ticker_info)
                elif recommendation == "Consider":
                    consider.append(ticker_info)
                else:
                    avoid.append(ticker_info)
                    
        except Exception as e:
            errors.append((symbol, str(e)))
            continue
    
    print("\n")  # New line after progress indicator
    return recommended, consider, avoid, errors

def print_results(recommended, consider, errors):
    """
    Print the analysis results in a formatted way.
    """
    print("\nEarnings Analysis Results")
    print("=" * 50)
    
    # Print recommended plays
    print("\nRECOMMENDED PLAYS:")
    print("-" * 50)
    if not recommended:
        print("None")
    for ticker_info in recommended:
        print(f"\nSymbol: {ticker_info['symbol']} | Time: {ticker_info['time']}")
        print(f"Expected Move: {ticker_info['expected_move']}")
        print(f"Recommendation: {ticker_info['recommendation']}")
    
    # Print consider plays
    print("\nCONSIDER PLAYS:")
    print("-" * 50)
    if not consider:
        print("None")
    for ticker_info in consider:
        print(f"\nSymbol: {ticker_info['symbol']} | Time: {ticker_info['time']}")
        print(f"Expected Move: {ticker_info['expected_move']}")
        print(f"Recommendation: {ticker_info['recommendation']}")
    
    # Print errors
    if errors:
        print("\nErrors encountered:")
        print("-" * 50)
        for symbol, error in errors:
            print(f"{symbol}: {error}")

def main():
    parser = argparse.ArgumentParser(description='Analyze stocks with earnings on a specific date')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format (default: today)', required=False)
    
    args = parser.parse_args()
    
    # Get earnings tickers
    earnings_tickers = get_earnings_for_date(args.date)
    
    if not earnings_tickers:
        return
    
    print(f"\nFound {len(earnings_tickers)} stocks with earnings before filter")
    # Filter stocks without options
    earnings_tickers = filter_stocks(earnings_tickers, rules={'use_static_list': True})
    
    print(f"\nFound {len(earnings_tickers)} stocks with earnings")
    
    # Analyze tickers
    recommended, consider, avoid, errors = analyze_earnings_plays(earnings_tickers)
    all_relevant = recommended + consider
    print_results(recommended, consider, errors)

if __name__ == "__main__":
    main()
