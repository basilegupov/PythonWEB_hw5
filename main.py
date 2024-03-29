import json
import argparse
import asyncio
import aiohttp
import pprint
from datetime import datetime, timedelta


async def fetch_currency_rates(days, currency=None):
    async with aiohttp.ClientSession() as session:
        rates = []
        list_currency = ['USD', 'EUR']
        if currency:
            list_currency.append(currency)
        for i in range(days):
            date = (datetime.today() - timedelta(days=i)).strftime('%d.%m.%Y')
            async with session.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}') as response:
                data = await response.json()
                pprint.pprint(data)
                for cur in data['exchangeRate']:
                    currency = cur.get('currency')
                    if currency in list_currency:
                        purchase_rate = cur.get('purchaseRate')
                        sale_rate = cur.get('saleRate')
                        rates.append({date: {currency: {'sale': sale_rate, 'purchase': purchase_rate}}})
                    # rate = cur.get('purchaseRateNB') if len(data['exchangeRate']) > 0 else None
                # usd_rate = data['exchangeRate'][1].get('purchaseRateNB') if len(data['exchangeRate']) > 1 else None

        return rates


async def main(days, currency=None):
    rates = await fetch_currency_rates(days, currency)
    print(json.dumps(rates, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get currency rates from PrivatBank for the last few days.')
    parser.add_argument('days', type=int, help='Number of days to retrieve currency rates for (not more than 10)')
    # parser.add_argument('currency', type=str, help='List of currency\'s')
    args = parser.parse_args()
    if args.days > 10:
        print('Error: You can retrieve currency rates for up to 10 days only.')
    else:
        asyncio.run(main(args.days))
