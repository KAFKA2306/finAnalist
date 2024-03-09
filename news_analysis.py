
from transformers import pipeline

class NewsAnalyzer:
    def __init__(self):
        self.ner_pipeline = pipeline("ner", model="dslim/bert-base-NER")
        
    def extract_companies(self, news_articles):
        company_names = set()
        for article in news_articles:
            result = self.ner_pipeline(article['title'] + ' ' + article['description'])
            for entity in result:
                if entity['entity'] == 'B-ORG':
                    company_names.add(entity['word'])
        return list(company_names)

    def analyze_news_content(self, news_articles):
        # Claude APIを使用してニュース記事の内容を分析
        claude_api_key = self.api_keys['claude_api']
        analysis_results = []
        for article in news_articles:
            url = "https://api.anthropic.com/v1/complete"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": claude_api_key
            }
            data = {
                "prompt": f"Please analyze the following news article:\n\n{article['title']}\n{article['description']}\n\nProvide a summary of the key points and sentiment analysis.",
                "model": "claude-v1",
                "max_tokens_to_sample": 100
            }
            response = requests.post(url, headers=headers, json=data)
            analysis_results.append(response.json()['completion'])
        return analysis_results

    def save_news_analysis_results(self, results):
        with open("news_analysis_results.txt", "w") as file:
            for result in results:
                file.write(result + "\n\n")
