from datetime import datetime
from datetime import timedelta
from decimal import Decimal

import requests

from cluecoins.storage import Storage

API_URL = 'https://api.currencybeacon.com'


class QuoteCache:
    def __init__(self, storage: Storage) -> None:
        self._storage = storage
        self._quote_currencies: set[str] = set()

    def _fetch_quotes(
        self,
        date: datetime,
        base_currency: str,
    ) -> None:
        """Getting quotes from the Exchangerate API and writing them to the local database"""
        _key = 'BF178aNPAdfPW6YjqbYGL5CmztO4qLNY'

        # url = f'{API_URL}/list?access_key={_key}'
        # print(url)
        # response = requests.get(url=url).json()
        # import time
        # time.sleep(100)
        # print(response)
        # latest_rates = response['currencies']
        # if base_currency not in latest_rates or quote_currency not in latest_rates:
        #     raise Exception(f'No currency {base_currency} or {quote_currency} in response')

        start_date = date - timedelta(days=180)
        params = {
            'api_key': _key,
            # FIXME: Overkill
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': date.strftime('%Y-%m-%d'),
            'base': base_currency,
            'symbols': ','.join(self._quote_currencies),
        }
        response = requests.get(
            url=f'{API_URL}/v1/timeseries',
            params=params,
        )
        response_json = response.json()
        for quote_date, items in response_json['response'].items():
            for quote_currency, price in items.items():
                self._storage.add_quote(
                    datetime.strptime(quote_date, '%Y-%m-%d'),
                    base_currency,
                    quote_currency,
                    Decimal(str(price)),
                )

    # FIXME: Cache me
    def get_price(
        self,
        date: datetime,
        base_currency: str,
        quote_currency: str,
    ) -> Decimal:
        if base_currency == quote_currency:
            return Decimal('1')

        price = self._storage.get_quote(date, base_currency, quote_currency)
        if not price:
            self._quote_currencies.add(quote_currency)
            self._fetch_quotes(date, base_currency)
            price = self._storage.get_quote(date, base_currency, quote_currency)

        if not price:
            raise Exception(f'No quote for {date} {base_currency} {quote_currency}')

        return price
