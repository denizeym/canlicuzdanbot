import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()  # .env dosyasını oku

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
LAST_TX_HASH = None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def check_transactions():
    global LAST_TX_HASH
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={WALLET_ADDRESS}&sort=desc&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()
    txs = response['result']
    if txs:
        latest_tx = txs[0]
        tx_hash = latest_tx['hash']
        if tx_hash != LAST_TX_HASH:
            LAST_TX_HASH = tx_hash
            value = int(latest_tx['value']) / 1e18
            send_telegram_message(f"Yeni İşlem 🚨\nTx Hash: {tx_hash}\nMiktar: {value:.4f} ETH")

while True:
    check_transactions()
    time.sleep(30)  # her 30 saniyede bir kontrol



