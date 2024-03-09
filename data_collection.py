
import configparser
import requests

class DataCollector:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.api_keys = config['API_KEYS']

    def collect_news_data(self, theme):
        # Google News APIを使用してニュース記事を収集
        google_news_api_key = self.api_keys['google_news_api']
        url = f"https://newsapi.org/v2/everything?q={theme}&apiKey={google_news_api_key}"
        response = requests.get(url)
        news_data = response.json()
        return news_data['articles']

    def collect_company_data(self, company_names):
        # QuickFSを使用して企業情報を収集
        quick_fs_api_key = self.api_keys['quick_fs_api']
        company_data = {}
        for name in company_names:
            url = f"https://quickfs.net/api/v1/data/company/{name}?api_key={quick_fs_api_key}"
            response = requests.get(url)
            company_data[name] = response.json()
        return company_data

    def collect_financial_data(self, company_names):
        # Bloomberg APIを使用して財務データを収集
        bloomberg_api_key = self.api_keys['bloomberg_api']
        financial_data = {}
        for name in company_names:
            url = f"https://www.bloomberg.com/markets/api/bulk-time-series/price/{name}:JP?timeFrame=5_YEAR&period=daily&volumePeriod=daily&currency=JPY&apiKey={bloomberg_api_key}"
            response = requests.get(url)
            financial_data[name] = response.json()
        return financial_data
