import os
import time
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

KEYWORDS = [
    "النادي الإفريقي",
    "الافريقي",
    "Club Africain",
    "Zamalek SC",
    "نادي الزمالك",
]
URL = "https://www.tazkarti.com/#/matches"


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception:
        pass


def check_stop_command():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        res = requests.get(url, timeout=10).json()
        results = res.get("result", [])
        if results:
            last_id = results[-1]["update_id"]
            requests.get(f"{url}?offset={last_id + 1}", timeout=10)
            for update in results:
                text = update.get("message", {}).get("text", "").lower()
                if "stop" in text or "خلاص" in text:
                    return True
    except Exception:
        pass
    return False


def start_alarm(found_keyword):
    while True:
        if check_stop_command():
            send_telegram("✅ تم إيقاف الإنذار. بالتوفيق في الحجز!")
            break
        send_telegram(
            f"🚨🚨 التذاكر نزلت حالاً ({found_keyword})! ادخل بسرعة:\n{URL}"
        )
        time.sleep(2)


def monitor():
    check_stop_command()

    start_time = time.time()
    max_duration = 270  # يراقب لمدة 4 دقائق ونصف في كل دورة

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        while time.time() - start_time < max_duration:
            try:
                page.goto(URL, timeout=30000)
                page.wait_for_timeout(4000)
                content = page.inner_text("body")

                for word in KEYWORDS:
                    if word.lower() in content.lower():
                        browser.close()
                        start_alarm(word)
                        return
            except Exception:
                pass

            time.sleep(10)

        browser.close()


if __name__ == "__main__":
    monitor()
