import requests
import json
import time
import smtplib
from datetime import datetime

# Load config
with open("config.json") as config_file:
    config = json.load(config_file)

api_key = config["api_key"]
access_token = config["access_token"]
symbol = config["symbol"]
lots = config["lots"]
stop_loss = config["stop_loss"]
target = config["target"]
paper_mode = config["paper_mode"]
email_settings = config["email"]

# Dhan API base URL
BASE_URL = "https://api.dhan.co"

def send_email(subject, body):
    try:
        server = smtplib.SMTP(email_settings["smtp_server"], email_settings["smtp_port"])
        server.starttls()
        server.login(email_settings["email"], email_settings["password"])
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(email_settings["email"], email_settings["to_email"], message)
        server.quit()
        print("Email alert sent.")
    except Exception as e:
        print("Email failed:", e)

def get_ltp(symbol):
    url = f"{BASE_URL}/market/quotes"
    headers = {
        "access-token": access_token,
        "Content-Type": "application/json"
    }
    params = {"symbol": symbol}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        ltp = data.get("last_traded_price", 0)
        print(f"LTP for {symbol}: {ltp}")
        return ltp
    else:
        print("Error fetching LTP:", response.status_code, response.text)
        return None

def place_order(strike, option_type):
    order_details = {
        "transaction_type": "SELL",
        "exchange_segment": "NSE",
        "product_type": "INTRADAY",
        "order_type": "MARKET",
        "security_id": f"{symbol}{strike}{option_type}",
        "quantity": lots * 25,  # Assuming 1 lot = 25
        "price": 0  # Market order
    }
    if paper_mode:
        print(f"[PAPER] Would place order: {order_details}")
    else:
        url = f"{BASE_URL}/orders"
        headers = {
            "access-token": access_token,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=order_details)
        if response.status_code == 200:
            print("Order placed successfully!")
            send_email("Order Placed", f"Order placed: {order_details}")
        else:
            print("Order failed:", response.status_code, response.text)

def monitor_position(entry_price):
    while True:
        current_price = get_ltp(symbol)
        if current_price is None:
            time.sleep(10)
            continue
        if current_price >= entry_price + target:
            print("🎯 Target hit!")
            send_email("Target Achieved", f"Target reached for {symbol}")
            break
        elif current_price <= entry_price - stop_loss:
            print("🔴 Stop loss hit!")
            send_email("Stop Loss Hit", f"Stop loss triggered for {symbol}")
            break
        time.sleep(10)

def main():
    print("🚀 Starting BankNifty AutoBot...")
    price = get_ltp(symbol)
    if price:
        strike = round(price / 100) * 100
        print(f"Selected strike: {strike}")
        place_order(strike, "CE")
        monitor_position(price)
    else:
        print("❌ Failed to fetch LTP. Exiting.")

if __name__ == "__main__":
    main()
