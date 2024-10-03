import argparse
import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = "https://api.coingecko.com/api/v3"
CURRENCY = 'usd'

def parse_args():
    """
    Parse command-line arguments and return holdings and days.
    """
    parser = argparse.ArgumentParser(description="Process a JSON file of holdings.")
    parser.add_argument('--holdings', type=str, required=True, help="Path to the holdings JSON file")
    parser.add_argument('--days', type=int, required=True, help="Number of days to analyze history for")
    args = parser.parse_args()

    if args.days <= 1:
        print(f"ERROR: Invalid number of days: {args.days}. 'days' must be an integer greater than 1.")
        sys.exit(1)

    try:
        with open(args.holdings, 'r') as file:
            holdings = json.load(file)
    except FileNotFoundError:
        print(f"ERROR: The file '{args.holdings}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: The file '{args.holdings}' is not a valid JSON file.")
        sys.exit(1)

    for coin, amount in holdings.items():
        if not isinstance(amount, (int, float)):
            print(f"ERROR: The amount for '{coin}' is not a valid number.")
            sys.exit(1)

    return holdings, args.days

def get_prices(holdings, days):
    """
    Fetch historical prices for each coin in holdings over the specified number of days.
    """
    prices = {}
    for coin in holdings:
        try:
            response = requests.get(
                f"{BASE_URL}/coins/{coin}/market_chart",
                params={'vs_currency': CURRENCY, 'days': days, 'interval': 'daily'}
            )
            response.raise_for_status()
            prices[coin] = [price[1] for price in response.json()['prices']]
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred for '{coin}': {http_err}")
            sys.exit(1)
        except requests.exceptions.RequestException as req_err:
            print(f"Request exception for '{coin}': {req_err}")
            sys.exit(1)
        except KeyError:
            print(f"Unexpected response format when fetching data for '{coin}'.")
            sys.exit(1)
    return prices

def get_portfolio_history(holdings, prices, days):
    """
    Calculate the daily total value of the portfolio over the specified number of days.
    """
    today = datetime.now()
    history = []
    for i in range(days):
        past_date = today - timedelta(days=days - i - 1)
        date = past_date.strftime('%Y-%m-%d')
        total = sum(prices[coin][i] * holdings[coin] for coin in holdings)
        history.append([date, total])
    return history

def main():
    holdings, days = parse_args()
    prices = get_prices(holdings, days)
    history = get_portfolio_history(holdings, prices, days)

    starting, ending = history[0][1], history[-1][1]
    total_return = (ending - starting) / starting * 100

    print(f"""
Portfolio Performance Over Last {days} Days:
---------------------------------------
Starting Portfolio Value: ${starting:,.2f}
Ending Portfolio Value:   ${ending:,.2f}
Total Return:             {total_return:+.2f}%
""")

    print("Daily Portfolio Values:")
    for date, total in history:
        print(f"{date}: ${total:,.2f}")

if __name__ == '__main__':
    main()
