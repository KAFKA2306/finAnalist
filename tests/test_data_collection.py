
import unittest
from lib.data_collection import DataCollector

class TestDataCollector(unittest.TestCase):
   def setUp(self):
       self.data_collector = DataCollector()

   def test_collect_news_data(self):
       theme = "電気自動車"
       news_data = self.data_collector.collect_news_data(theme)
       self.assertIsInstance(news_data, list)
       self.assertGreater(len(news_data), 0)

   def test_collect_twitter_data(self):
       theme = "電気自動車"
       tweet_data = self.data_collector.collect_twitter_data(theme)
       self.assertIsInstance(tweet_data, list)
       self.assertGreater(len(tweet_data), 0)

   def test_collect_financial_data(self):
       companies = ["テスラ", "ゼネラルモーターズ", "フォード"]
       financial_data = self.data_collector.collect_financial_data(companies)
       self.assertIsInstance(financial_data, dict)
       self.assertEqual(len(financial_data), len(companies))

   def test_collect_stock_price_data(self):
       companies = ["テスラ", "ゼネラルモーターズ", "フォード"]
       stock_price_data = self.data_collector.collect_stock_price_data(companies)
       self.assertIsInstance(stock_price_data, dict)
       self.assertEqual(len(stock_price_data), len(companies))

if __name__ == '__main__':
   unittest.main()
