from telegram.ext import *
from telegram import Update
import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio
    
print('Launching the bot...')

# Dictionary for tracking shipped goods
sent_products = {}

token = ""
application = Application.builder().token(token).build()

async def track_price(update: Update, context: CallbackContext) -> None:
    # List of sites and keywords
    sites = [
        {'name': 'Pepper', 'url': 'https://www.pepper.pl/nowe'},
        {'name': 'OtoMoto', 'url': 'https://otomotoklik.pl/oferty?priceType=price&priceFrom=12900&priceTo=40100&transmissionType=automatic'},
        {'name': 'OtoMoto_Osobowe', 'url': 'https://www.otomoto.pl/osobowe/od-2009?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_gearbox%5D=automatic&search%5Bfilter_enum_registered%5D=1&search%5Bfilter_float_mileage%3Ato%5D=250000&search%5Bfilter_float_price%3Ato%5D=20000&search%5Badvanced_search_expanded%5D=true'},
    ]

    send_message(token, update.message.chat_id, 'Hi! I am a bot for tracking the prices of goods.')

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                for site in sites:
                    # Getting the HTML code of the page
                    async with session.get(site['url']) as response:
                        html = await response.text()

                    soup = BeautifulSoup(html, 'html.parser')

                    # Search for a block with product information
                    if site['name'] == "Pepper":
                        procData(soup, site, 'cept-tt thread-link linkPlain thread-title--list js-thread-title', 'cept-tt thread-link linkPlain thread-title--list js-thread-title', 'thread-price text--b cept-tp size--all-l size--fromW3-xl', update, None)
                    if site['name'] == "OtoMoto":
                        procData(soup, site, 'offer-url', 'offer-name', 'price-value', update, 'https://otomotoklik.pl')
                    if site['name'] == "OtoMoto_Osobowe":
                        procData(soup, site, 'ev7e6t89 ooa-1xvnx1e er34gjf0 a', 'ev7e6t89 ooa-1xvnx1e er34gjf0', 'ev7e6t82 ooa-bz4efo er34gjf0', update, None)

        except Exception as e:
            await update.message.reply_text(f'Ошибка: {str(e)}')

        # Pause between iterations
        await asyncio.sleep(10)  # Pause for 10 seconds

def procData(soup, site, class1, class2, class3, update, addUrl):
    # If the block is found, we extract information about the product
    # Search for the link and title by the specified classes
    link_element = soup.find('a', class_=class1)
    link = link_element['href'] if link_element else 'Link not found'

    name_element = soup.find(class_=class2)
    name = name_element.text.strip() if name_element else 'Name not found'

    # Search for a price by the specified class
    price_element = soup.find(class_=class3)
    price = price_element.text.strip() if price_element else 'Price not found'

    # Generating a unique key based on the product name and price
    product_key = f'{name}_{price}'

    # Checking whether the product with such a key has already been shipped
    if product_key not in sent_products:
        # Sending the link, name and price to the chat
        text_to_send_in_channel = (f'📌 Website: {site["name"]}\n'
                           f'🛒 Product: {name}\n'
                           f'💵 Price: {price}\n\n'
                           f'🔗 Link: {addUrl}{link}' if addUrl else
                           f'📌 Website: {site["name"]}\n'
                           f'🛒 Product: {name}\n'
                           f'💵 Price: {price}\n\n'
                           f'🔗 Link: {link}')
        send_message(token, update.message.chat_id, text_to_send_in_channel)
        sent_products[product_key] = True

def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id,"text": text,}
    response = requests.post(url, json=params)
    if response.status_code == 200:
        print("The message was sent successfully")
    else:
        print("Error when sending a message")

if __name__ == '__main__':
    # Commands
    application.add_handler(CommandHandler('start', track_price))
    # Run bot
    print('The bot is running!')
    application.run_polling(1.0)