
import pandas as pd
from sklearn.ensemble import IsolationForest

class FinancialAnalyzer:
    def __init__(self):
        pass

    def calculate_valuation_metrics(self, financial_data):
        valuation_metrics = {}
        for name, data in financial_data.items():
            revenue = [d['revenue'] for d in data if 'revenue' in d]
            profit = [d['profit'] for d in data if 'profit' in d]
            market_cap = [d['market_cap'] for d in data if 'market_cap' in d]
            if revenue and profit and market_cap:
                pe_ratio = market_cap[-1] / profit[-1]
                ps_ratio = market_cap[-1] / revenue[-1]
                valuation_metrics[name] = {
                    'pe_ratio': pe_ratio,
                    'ps_ratio': ps_ratio
                }
        return valuation_metrics
    
    def compare_with_industry_average(self, valuation_metrics):
        # 業種平均との比較分析
        industry_averages = {
            'pe_ratio': 20,
            'ps_ratio': 2
        }
        comparison_results = {}
        for name, metrics in valuation_metrics.items():
            pe_ratio_diff = (metrics['pe_ratio'] - industry_averages['pe_ratio']) / industry_averages['pe_ratio']
            ps_ratio_diff = (metrics['ps_ratio'] - industry_averages['ps_ratio']) / industry_averages['ps_ratio']
            comparison_results[name] = {
                'pe_ratio_diff': pe_ratio_diff,
                'ps_ratio_diff': ps_ratio_diff
            }
        return comparison_results

    def perform_dcf_valuation(self, financial_data, growth_forecast):
        dcf_valuation_results = {}
        for name, data in financial_data.items():
            # 将来のキャッシュフロー予測
            cash_flows = [d['free_cash_flow'] for d in data if 'free_cash_flow' in d]
            forecast_period = 5
            forecast_cash_flows = [cash_flows[-1] * (1 + growth_forecast) ** i for i in range(1, forecast_period + 1)]
            
            # 割引率の設定
            discount_rate = 0.08
            
            # 割引現在価値の計算
            discount_factors = [(1 + discount_rate) ** i for i in range(1, forecast_period + 1)]
            discounted_cash_flows = [cf / df for cf, df in zip(forecast_cash_flows, discount_factors)]
            
            # 企業価値の計算
            terminal_value = discounted_cash_flows[-1] * (1 + growth_forecast) / (discount_rate - growth_forecast)
            enterprise_value = sum(discounted_cash_flows) + terminal_value
            
            # 株主価値の計算
            net_debt = data[-1]['total_debt'] - data[-1]['cash_and_equivalents']
            equity_value = enterprise_value - net_debt
            dcf_valuation_results[name] = equity_value
        
        return dcf_valuation_results
    
    def detect_anomalies(self, financial_data):
        # 財務データの異常値検知
        anomalies = {}
        for name, data in financial_data.items():
            df = pd.DataFrame(data)
            clf = IsolationForest(contamination=0.1)
            clf.fit(df)
            anomaly_scores = clf.decision_function(df)
            anomalies[name] = list(df[anomaly_scores < 0].index)
        
        return anomalies

    def save_financial_analysis_results(self, results):
        with open("financial_analysis_results.txt", "w") as file:
            for name, result in results.items():
                file.write(f"Company: {name}\n")
                file.write(str(result) + "\n\n")
