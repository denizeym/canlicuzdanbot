import requests
import time
import threading
from flask import Flask, request
import os
from dotenv import load_dotenv

# .env dosyasını oku
load_dotenv()

# Değişkenler
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
LAST_TX_HASH = None

# Flask app (Webhook için)
app = Flask(__name__)

# Abone kontrolü
def chat_id_exists(chat_id):
    try:
        with open('subscribers.txt', 'r') as f:
            return chat_id in f.read()
    except FileNotFoundError:
        return False

# Abone kaydetme
def save_chat_id(chat_id):
    with open('subscribers.txt', 'a') as f:
        f.write(chat_id + '\n')

# Telegram'dan gelen mesajı yakala
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    chat_id = str(data['message']['chat']['id'])
    if not chat_id_exists(chat_id):
        save_chat_id(chat_id)
        send_telegram_message(chat_id, "✅ Abone oldun! Yeni token işlemleri bildirilecek.")
    return 'ok'

# Tek kişiye mesaj
def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, data=payload)

# Tüm abonelere mesaj
def send_telegram_message_to_all(message):
    try:
        with open('subscribers.txt', 'r') as f:
            chat_ids = f.read().splitlines()
        for chat_id in chat_ids:
            send_telegram_message(chat_id, message)
    except Exception as e:
        print("Mesaj gönderme hatası:", e)

# Token işlemlerini kontrol et
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
        send_telegram_message_to_all(message)

# Flask server'ı başlat (background thread)
def start_flask():
    app.run(host='0.0.0.0', port=8080)

# İşlem kontrol döngüsü
def start_bot():
    while True:
        check_token_transactions()
        time.sleep(30)

# Eşzamanlı başlat dddddd
if __name__ == '__main__':
    threading.Thread(target=start_flask).start()
    start_bot()
