import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()  # .env dosyasını oku

CUSTOM_MESSAGE = os.getenv('CUSTOM_MESSAGE')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
LAST_TX_HASH = None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def check_token_transactions():
    global LAST_TX_HASH
    url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={WALLET_ADDRESS}&sort=desc&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()

    if response.get('status') != '1':
        print("Token işlemleri alınamadı:", response.get('message'))
        return

    txs = response['result']
    if not txs:
        return

    latest_tx = txs[0]
    tx_hash = latest_tx['hash']
    if tx_hash != LAST_TX_HASH:
        LAST_TX_HASH = tx_hash
        token_symbol = latest_tx['tokenSymbol']
        token_name = latest_tx['tokenName']
        value = int(latest_tx['value']) / (10 ** int(latest_tx['tokenDecimal']))
        from_address = latest_tx['from']
        to_address = latest_tx['to']
        direction = '📥 Alındı' if to_address.lower() == WALLET_ADDRESS.lower() else '📤 Gönderildi'

        message = (
            f"🚨 Yeni Token İşlemi\n"
            f"Token: {token_symbol} ({token_name})\n"
            f"{direction}: {value:.4f} {token_symbol}\n"
            f"Tx Link: https://etherscan.io/tx/{tx_hash}"
        )
        send_telegram_message(message)

while True:
    check_token_transactions()
    time.sleep(30)
