
import requests
from bs4 import BeautifulSoup
import time
import os

BOT_TOKEN = "7747932663:AAGjBtgIp9di9aLZ09bk8-Gm5k802RfozCs"
CHAT_ID = "1101436924"

CATEGORY_URLS = {
    'Steam аккаунты': 'https://lzt.market/category/2-gaming-accounts/',
    'Epic Games': 'https://lzt.market/category/5-epic-games/',
    'Social': 'https://lzt.market/category/6-social-accounts/',
}

KEYWORDS = ['gta', 'steam', 'csgo']
MIN_PRICE = 100
MAX_PRICE = 1000

seen_links = set()

def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in escape_chars else c for c in text)

def send_telegram_message(title, link, price, category):
    title_md = escape_markdown(title)
    link_md = escape_markdown(link)
    category_md = escape_markdown(category)

    message = (
        f"🆕 Новое в категории *{category_md}*\n"
        f"[{title_md}]({link_md})\n"
        f"*Цена:* {price} ₽"
    )

    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'MarkdownV2'
    }
    requests.post(url, data=data)

def extract_price(text):
    digits = ''.join(filter(str.isdigit, text))
    return int(digits) if digits else 0

def parse_category(name, url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.select('a.market-item')

    new_items = []
    for item in items:
        title_elem = item.select_one('.title')
        price_elem = item.select_one('.price')
        if not title_elem or not price_elem:
            continue

        title = title_elem.get_text(strip=True).lower()
        price_text = price_elem.get_text(strip=True)
        price = extract_price(price_text)
        link = 'https://lzt.market' + item['href']

        if link in seen_links:
            continue

        if any(keyword in title for keyword in KEYWORDS) and MIN_PRICE <= price <= MAX_PRICE:
            seen_links.add(link)
            new_items.append({'title': title, 'price': price, 'link': link, 'category': name})

    return new_items

def monitor_all_categories():
    while True:
        try:
            for name, url in CATEGORY_URLS.items():
                new_items = parse_category(name, url)
                for item in new_items:
                    send_telegram_message(item['title'], item['link'], item['price'], item['category'])
            time.sleep(60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(60)

if __name__ == '__main__':
    monitor_all_categories()
