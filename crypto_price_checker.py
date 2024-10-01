import argparse
import requests
import json

BASE_URL="https://api.coingecko.com/api/v3"
CURRENCY='usd'

def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def get_holdings():
    parser = argparse.ArgumentParser(description="Process a JSON file of holdings.")
    parser.add_argument('--holdings', type=str, required=True, help="Path to the holdings JSON file")
    args = parser.parse_args()
    with open(args.holdings, 'r') as file:
        holdings = json.load(file)
    return holdings

def get_prices(holdings):
    params = {
        'ids': ','.join(holdings.keys()),
        'vs_currencies': CURRENCY
    }
    response = requests.get(f"{BASE_URL}/simple/price", params=params)
    if response.status_code != 200:
        print(f"ERROR: Network error. Status code: {response.status_code}")
        exit(1)
    response = response.json()

    for coin, val in holdings.items():
        if coin not in response:
            print(f"ERROR: Invalid coin name: {coin}.")
            exit(1)
        if not is_numeric(val):
            print(f"ERROR: Value {val} is invalid.")
            exit(1)
        holdings[coin] = float(val)

    return response


def main():
    holdings = get_holdings()
    prices = get_prices(holdings)

    total = 0
    print("Portfolio Summary\n----------------")
    for coin, price in prices.items():
        value_owned = price[CURRENCY] * holdings[coin]
        print(f"{coin}:")
        print(f"Quantity owned: {holdings[coin]}")
        print(f"Current price: ${price[CURRENCY]:,.2f}")
        print(f"Total value: ${value_owned}")
        print()
        total += value_owned

    print(f"Total value: ${total}")

if __name__ == '__main__':
    main()