import argparse
from turtledemo.penrose import start

import requests
import json
from datetime import datetime, timedelta

BASE_URL="https://api.coingecko.com/api/v3"
CURRENCY='usd'

def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def parse_args():
    parser = argparse.ArgumentParser(description="Process a JSON file of holdings.")
    parser.add_argument('--holdings', type=str, required=True, help="Path to the holdings JSON file")
    parser.add_argument('--days', type=int, required=True, help="Number of days to analyze history for")
    args = parser.parse_args()

    if args.days <= 1:
        print("ERROR: Inavlid number of days: {args.days}. days must an integer be greater than 1.")
    with open(args.holdings, 'r') as file:
        holdings = json.load(file)
    return holdings, args.days

def get_prices(holdings, days):
    params = {
        'vs_currency': CURRENCY,
        'days': days,
        'interval': 'daily'
    }

    prices = {}
    for coin in holdings:
        try:
            response = requests.get(f"{BASE_URL}/coins/{coin}/market_chart", params=params)
            response.raise_for_status()
            prices[coin] = [price[1] for price in response.json()['prices']]
        except Exception as e:
            print(f"Exception: {e}")
            exit(1)

    return prices

def get_portfolio_history(holdings, prices, days):
    today = datetime.now()
    history = []
    for i in range(days):
        past_date = today - timedelta(days=days) + timedelta(days=i)
        date = past_date.strftime('%Y-%m-%d')
        total = 0
        for coin in holdings:
            total += prices[coin][i] * holdings[coin]
        history.append([date, total])
    return history

def main():
    holdings, days = parse_args()
    prices = get_prices(holdings, days)
    history = get_portfolio_history(holdings, prices, days)

    starting, ending = history[0][1], history[-1][1]
    total_return = (ending - starting) / starting
    print(f"""
Portfolio Performance Over Last {days} Days:
---------------------------------------
Starting Portfolio Value: ${starting:,.2f}
Ending Portfolio Value: ${ending:,.2f}
Total Return: {total_return:+.2f}%
    """)
    print("Daily Portfolio Values:")
    for date, total in history:
        print(f"{date}: ${total:,.2f}")

if __name__ == '__main__':
    main()

