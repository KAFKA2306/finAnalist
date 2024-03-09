# -*- coding: utf-8 -*-
import configparser
import requests

class DataCollector:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config/config.ini', encoding='utf-8')
        self.api_keys = config['API_KEYS']
        


    def collect_news_data(self, theme):
        # NewsAPIを使用してニュース記事を収集
        url = f"https://newsapi.org/v2/everything?q={theme}&apiKey={self.api_keys['NEWS_API_KEY']}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['articles']
        else:
            return None

    def collect_twitter_data(self, theme):
        # Twitter APIを使用してツイートを収集
        url = f"https://api.twitter.com/2/tweets/search/recent?query={theme}"
        headers = {
            "Authorization": f"Bearer {self.api_keys['TWITTER_API_KEY']}",
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['data']
        else:
            return None

    def collect_financial_data(self, companies):
        # Alpha Vantage API、Finnhub API、Polygon APIを使用して財務データを収集
        financial_data = {}

        for company in companies:
            # Alpha Vantage APIを使用して財務データを取得
            alpha_vantage_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={company}&apikey={self.api_keys['ALPHA_VANTAGE_API_KEY']}"
            response = requests.get(alpha_vantage_url)
            if response.status_code == 200:
                data = response.json()
                financial_data[company] = data

            # Finnhub APIを使用して財務データを取得
            finnhub_url = f"https://finnhub.io/api/v1/stock/metric?symbol={company}&metric=all&token={self.api_keys['FINNHUB_API_KEY']}"
            response = requests.get(finnhub_url)
            if response.status_code == 200:
                data = response.json()
                financial_data[company].update(data)

            # Polygon APIを使用して財務データを取得
            polygon_url = f"https://api.polygon.io/v2/reference/financials/{company}?apiKey={self.api_keys['POLYGON_API_KEY']}"
            response = requests.get(polygon_url)
            if response.status_code == 200:
                data = response.json()
                financial_data[company].update(data)

        return financial_data

    def collect_stock_price_data(self, companies):
        # Alpha Vantage API、Finnhub API、Polygon APIを使用して株価データを収集
        stock_price_data = {}

        for company in companies:
            # Alpha Vantage APIを使用して株価データを取得
            alpha_vantage_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={company}&apikey={self.api_keys['ALPHA_VANTAGE_API_KEY']}"
            response = requests.get(alpha_vantage_url)
            if response.status_code == 200:
                data = response.json()
                stock_price_data[company] = data['Time Series (Daily)']

            # Finnhub APIを使用して株価データを取得
            finnhub_url = f"https://finnhub.io/api/v1/stock/candle?symbol={company}&resolution=D&from=1572651390&to=1575243390&token={self.api_keys['FINNHUB_API_KEY']}"
            response = requests.get(finnhub_url)
            if response.status_code == 200:
                data = response.json()
                stock_price_data[company].update(data)

            # Polygon APIを使用して株価データを取得
            polygon_url = f"https://api.polygon.io/v2/aggs/ticker/{company}/range/1/day/2022-01-01/2023-03-09?apiKey={self.api_keys['POLYGON_API_KEY']}"
            response = requests.get(polygon_url)
            if response.status_code == 200:
                data = response.json()
                stock_price_data[company].update(data)

        return stock_price_data