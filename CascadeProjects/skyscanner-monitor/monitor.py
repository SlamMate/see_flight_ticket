import os
import re
import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# Configuration
URL = "https://www.skyscanner.nl/transport/d/ams/2026-06-01/nyca/nyca/2026-06-02/dena/dena/2026-06-08/ams/?adultsv2=1&cabinclass=economy&childrenv2=&ref=home"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not set. Skipping message.")
        print("Message would have been:")
        print(message)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram message sent successfully.")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def get_flight_prices():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        stealth_sync(page)
        
        print(f"Navigating to {URL}")
        try:
            page.goto(URL, timeout=60000, wait_until="domcontentloaded")
            
            # Wait for some time to allow dynamic content to load
            # Skyscanner shows a loading screen, we need to wait for the results
            print("Waiting for results to load...")
            page.wait_for_timeout(15000)
            
            # Handle cookie banner if present
            try:
                cookie_btn = page.locator("button:has-text('Accepteren'), button:has-text('Accept'), button[id='acceptCookieButton']")
                if cookie_btn.count() > 0:
                    cookie_btn.first.click()
                    page.wait_for_timeout(2000)
            except Exception:
                pass

            # Scroll a bit to trigger lazy loading
            page.evaluate("window.scrollBy(0, 500)")
            page.wait_for_timeout(2000)
            
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            # Skyscanner prices often have specific classes or are within specific spans.
            # We will look for elements containing the Euro symbol '€' or 'prijs'
            # Let's extract all text and try to find the price blocks.
            
            # A common approach is to find all result cards.
            # They usually have an 'a' tag or 'div' with role='link' or similar.
            # Here we just look for all spans that contain '€'
            
            price_elements = soup.find_all(string=re.compile(r'€\s*\d+[.,]?\d*'))
            
            prices = []
            for el in price_elements:
                text = el.strip()
                # Clean up the price text
                match = re.search(r'€\s*(\d+[.,]?\d*)', text)
                if match:
                    prices.append(text)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_prices = []
            for p in prices:
                if p not in seen:
                    seen.add(p)
                    unique_prices.append(p)
            
            if not unique_prices:
                # Fallback: take screenshot for debugging
                page.screenshot(path="debug_screenshot.png")
                return None, "No prices found. Protection might be active or page structure changed. Check GitHub Actions artifacts."
            
            # Return top 5 prices
            return unique_prices[:5], None
            
        except Exception as e:
            page.screenshot(path="error_screenshot.png")
            return None, f"Error during scraping: {str(e)}"
        finally:
            browser.close()

def main():
    print("Starting flight price monitor...")
    top_prices, error = get_flight_prices()
    
    if error:
        msg = f"⚠️ <b>Skyscanner Monitor Error</b>\n\n{error}"
        send_telegram_message(msg)
    elif top_prices:
        msg = "✈️ <b>Skyscanner Price Update (Best Flights)</b>\n\n"
        msg += f"Route: AMS ➔ NYC ➔ DEN ➔ AMS\n"
        msg += f"Dates: Jun 1 - Jun 2 - Jun 8, 2026\n\n"
        msg += "<b>Top 5 Prices:</b>\n"
        for i, price in enumerate(top_prices, 1):
            msg += f"{i}. {price}\n"
        msg += f"\n<a href='{URL}'>View on Skyscanner</a>"
        
        send_telegram_message(msg)
        print("Extracted Prices:", top_prices)
    else:
        print("No data and no error?")

if __name__ == "__main__":
    main()
