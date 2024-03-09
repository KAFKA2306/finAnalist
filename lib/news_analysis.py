# -*- coding: utf-8 -*-
import json
import openai
import anthropic

class NewsAnalyzer:
    def __init__(self, openai_api_key, claude_api_key):
        self.openai = openai
        self.openai.api_key = openai_api_key
        self.claude = anthropic.Client(claude_api_key)

    def extract_related_companies(self, news_data):
        # OpenAI APIを使用して関連企業を抽出
        related_companies = []
        for article in news_data:
            prompt = f"次のニュース記事から関連する企業名を抽出してください。\n\n{article['title']}\n{article['description']}"
            response = self.openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.7,
            )
            companies = response.choices[0].text.strip().split(", ")
            related_companies.extend(companies)

        # Claude APIを使用して関連企業を抽出
        for article in news_data:
            prompt = f"次のニュース記事から関連する企業名を抽出してください。\n\n{article['title']}\n{article['description']}"
            response = self.claude.complete(
                prompt=prompt,
                stop_sequences=[],
                max_tokens_to_sample=100,
            )
            companies = response.completion.strip().split(", ")
            related_companies.extend(companies)

        return list(set(related_companies))

    def perform_sentiment_analysis(self, news_data):
        # OpenAI APIを使用してセンチメント分析を実施
        sentiment_scores = {"positive": 0, "negative": 0, "neutral": 0}
        for article in news_data:
            prompt = f"次のニュース記事のセンチメントを分析してください。\n\n{article['title']}\n{article['description']}\n\nセンチメント:"
            response = self.openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=1,
                n=1,
                stop=None,
                temperature=0.7,
            )
            sentiment = response.choices[0].text.strip().lower()
            if sentiment in sentiment_scores:
                sentiment_scores[sentiment] += 1

        # Claude APIを使用してセンチメント分析を実施
        for article in news_data:
            prompt = f"次のニュース記事のセンチメントを分析してください。\n\n{article['title']}\n{article['description']}\n\nセンチメント:"
            response = self.claude.complete(
                prompt=prompt,
                stop_sequences=[],
                max_tokens_to_sample=1,
            )
            sentiment = response.completion.strip().lower()
            if sentiment in sentiment_scores:
                sentiment_scores[sentiment] += 1

        return sentiment_scores

    def save_analysis_results(self, results, file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)