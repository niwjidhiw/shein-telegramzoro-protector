import json
import requests
import time
import random
import threading
import os

# =========================
# TELEGRAM CONFIG
# =========================

BOT_TOKEN = "8605688562:AAEi0DDbquavVTJ2DLaj0wiXUFHEoABnRlo"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# =========================
# SETTINGS
# =========================

CHECK_INTERVAL = 220
DATA_FILE = "users_codes.json"
MAX_CODES = 50

# =========================
# GLOBAL STORAGE
# =========================

users = {}
check_counts = {}

# =========================
# VOUCHER VALUES
# =========================

VOUCHER_VALUES = {
    "SVH": 4000,
    "SVD": 2000,
    "SVC": 1000,
    "SVI": 500
}

# =========================
# LOAD USERS
# =========================

def load_data():
    global users
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            users = json.load(f)

# =========================
# SAVE USERS
# =========================

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

# =========================
# LOAD COOKIES
# =========================

def load_cookies():
    with open("cookies.json", "r") as f:
        raw = f.read().strip()

    try:
        cookie_dict = json.loads(raw)
        return "; ".join(f"{k}={v}" for k, v in cookie_dict.items())
    except:
        return raw

# =========================
# ORIGINAL SAFE HEADERS
# =========================

def get_headers(cookie_string):

    return {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://www.sheinindia.in",
        "pragma": "no-cache",
        "referer": "https://www.sheinindia.in/cart",
        "sec-ch-ua": "\"Chromium\";v=\"142\", \"Google Chrome\";v=\"142\", \"Not_A Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36",
        "x-tenant-id": "shein",
        "cookie": cookie_string
    }

# =========================
# TELEGRAM SEND
# =========================

def send_message(user_id, text):

    try:
        requests.post(
            f"{API_URL}/sendMessage",
            data={
                "chat_id": user_id,
                "text": text
            }
        )
    except:
        pass

# =========================
# GET VALUE
# =========================

def get_value(code):
    return VOUCHER_VALUES.get(code[:3], 0)

# =========================
# CHECK VOUCHER
# =========================

def check_voucher(session, code, headers):

    url = "https://www.sheinindia.in/api/cart/apply-voucher"

    payload = {
        "voucherId": code,
        "device": {"client_type": "web"}
    }

    try:
        r = session.post(url, json=payload, headers=headers, timeout=30)
        data = r.json()

        if "errorMessage" in data:
            return False

        return True

    except:
        return False

# =========================
# RESET VOUCHER
# =========================

def reset_voucher(session, code, headers):

    url = "https://www.sheinindia.in/api/cart/reset-voucher"

    payload = {
        "voucherId": code,
        "device": {"client_type": "web"}
    }

    try:
        session.post(url, json=payload, headers=headers)
    except:
        pass

# =========================
# MAIN CHECKER LOOP (FIXED SESSION ONLY)
# =========================

def checker_loop():

    while True:

        try:

            cookie = load_cookies()
            headers = get_headers(cookie)

            safe_users = list(users.keys())

            for user_id in safe_users:

                codes = users.get(user_id, [])

                if not codes:
                    continue

                if user_id not in check_counts:
                    check_counts[user_id] = 0

                check_counts[user_id] += 1

                session = requests.Session()

                valid = []
                total = 0

                current_time = time.strftime("%H:%M:%S")

                for code in codes:

                    ok = check_voucher(session, code, headers)

                    if ok:

                        value = get_value(code)
                        valid.append((code, value))
                        total += value

                    reset_voucher(session, code, headers)
                    time.sleep(random.uniform(3,6))

                # FORMAT MESSAGE

                msg = "ðŸ’Ž YOUR COUPONS\n\n"
                grouped = {}

                for code in codes:

                    value = get_value(code)

                    if value not in grouped:
                        grouped[value] = []

                    if any(code == v[0] for v in valid):
                        grouped[value].append(f"âœ… {code}")
                    else:
                        grouped[value].append(f"âŒ {code}")

                for value in sorted(grouped.keys(), reverse=True):

                    msg += f"â‚¹{value} Coupons :\n"

                    for line in grouped[value]:
                        msg += f"{line}\n"

                    msg += "\n"

                msg += f"ðŸ’° Total Potential Value : â‚¹{total}"
                msg += "\n\nmade by @ItzzZoro01"

                send_message(user_id, msg)

                session.close()   # âœ… Only one close now

        except Exception as e:
            print("Checker error:", e)

        time.sleep(CHECK_INTERVAL)

# =========================
# TELEGRAM LOOP
# =========================

def telegram_loop():

    offset = None
    load_data()

    while True:

        try:

            r = requests.get(
                f"{API_URL}/getUpdates",
                params={"offset": offset}
            )

            data = r.json()

            if data["ok"]:

                for update in data["result"]:

                    offset = update["update_id"] + 1

                    msg = update.get("message")

                    if not msg:
                        continue

                    user_id = str(msg["chat"]["id"])
                    text = msg.get("text","").strip()

                    if user_id not in users:
                        users[user_id] = []

                    if text == "/start":

                        send_message(
                            user_id,
                            "Send coupon codes\nmade by @ItzzZoro01"
                        )

                    elif text == "/list":

                        if users[user_id]:
                            send_message(user_id, "\n".join(users[user_id]))
                        else:
                            send_message(user_id, "No codes saved")

                    elif text.startswith("/remove"):

                        parts = text.split()

                        if len(parts) == 2:

                            code = parts[1]

                            if code in users[user_id]:

                                users[user_id].remove(code)
                                save_data()

                                send_message(user_id, f"Removed {code}")

                    elif text == "/clear":

                        users[user_id] = []
                        save_data()

                        send_message(user_id, "All codes cleared")

                    else:

                        new_codes = text.split()
                        added = 0

                        for code in new_codes:

                            if (
                                code not in users[user_id]
                                and len(users[user_id]) < MAX_CODES
                            ):

                                users[user_id].append(code)
                                added += 1

                        save_data()

                        send_message(
                            user_id,
                            f"Added {added} codes\nTotal: {len(users[user_id])}"
                        )

        except Exception as e:
            print("Telegram error:", e)

        time.sleep(2)

# =========================
# MAIN
# =========================

def main():

    print("SHEIN TELEGRAM PROTECTOR STARTED")

    threading.Thread(
        target=checker_loop,
        daemon=True
    ).start()

    telegram_loop()

if __name__ == "__main__":
    main()