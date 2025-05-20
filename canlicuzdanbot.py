import requests
import time

TELEGRAM_TOKEN = '7430286299:AAEGASrdF998IMtprJm_AP-jM-4iUUPKHWM'
CHAT_ID = '1006613602'
WALLET_ADDRESS = '0xc82b2e484b161d20eae386877d57c4e5807b5581'
ETHERSCAN_API_KEY = 'NU6IWSKQBWAJABSUCHP7JT5I81RYS1CGE5'
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



