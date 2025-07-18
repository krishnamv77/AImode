import requests
import json
import time
import smtplib
from datetime import datetime
from dhan import Client  # pip install dhan  

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

# Initialize Dhan client
client = Client(api_key, access_token)

def send_email(subject, body):
    try:
        server = smtplib.SMTP(email_settings["smtp_server"], email_settings["smtp_port"])
        server.starttls()
        server.login(email_settings["email"], email_settings["password"])
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(email_settings["email"], email_settings["to_email"], message)
        server.quit()
    except Exception as e:
        print("Email failed:", e)

def get_option_strike(price, step=100):
    return round(price / step) * step

def place_order(strike, option_type):
    if paper_mode:
        print(f"[PAPER] Sell {lots} lots of {symbol} {strike}{option_type}")
    else:
        print(f"Placing live order: Sell {lots} lots of {symbol} {strike}{option_type}")
        # Add actual Dhan API call here to place order

def monitor_position():
    entry_price = 100  # simulate entry
    while True:
        current_price = 95  # simulate market price
        if current_price >= entry_price + target:
            print("Target hit!")
            send_email("Target Achieved", f"Target reached for {symbol}")
            break
        elif current_price <= entry_price - stop_loss:
            print("Stop loss hit!")
            send_email("Stop Loss Hit", f"Stop loss triggered for {symbol}")
            break
        time.sleep(10)

def main():
    print("Starting BankNifty AutoBot...")
    price = client.get_ltp(symbol)
    strike = get_option_strike(price)
    place_order(strike, "CE")
    monitor_position()

if __name__ == "__main__":
    main()
