
    import pandas as pd
    import numpy as np
    import yfinance as yf

    class InvestmentSimulator:
        def __init__(self):
            pass

        def load_historical_price_data(self, company_names, start_date, end_date):
            historical_data = {}
            for name in company_names:
                ticker = yf.Ticker(name)
                data = ticker.history(start=start_date, end=end_date)
                historical_data[name] = data['Close']
            return historical_data

        def backtest_investment_strategies(self, historical_data, strategies):
            backtest_results = {}
            for strategy in strategies:
                portfolio_values = []
                for name, data in historical_data.items():
                    if strategy == 'equal_weight':
                        num_shares = 1000 // data.iloc[0]
                        portfolio_value = num_shares * data
                    elif strategy == 'momentum':
                        returns = data.pct_change()
                        signal = np.where(returns.rolling(window=50).mean() > returns.rolling(window=200).mean(), 1, 0)
                        num_shares = 1000 // data.iloc[0]
                        portfolio_value = num_shares * data * signal
                    elif strategy == 'mean_reversion':
                        returns = data.pct_change()
                        signal = np.where(returns.rolling(window=50).mean() < returns.rolling(window=200).mean(), 1, 0)
                        num_shares = 1000 // data.iloc[0]
                        portfolio_value = num_shares * data * signal
                    else:
                        raise ValueError(f"Unknown strategy: {strategy}")

                    portfolio_values.append(portfolio_value)

                backtest_results[strategy] = pd.concat(portfolio_values, axis=1).sum(axis=1)

            return backtest_results

        def evaluate_risk_return(self, backtest_results):
            risk_return_metrics = {}
            for strategy, returns in backtest_results.items():
                total_return = (returns.iloc[-1] - returns.iloc[0]) / returns.iloc[0]
                annual_return = (1 + total_return) ** (252 / len(returns)) - 1
                annual_volatility = returns.pct_change().std() * np.sqrt(252)
                sharpe_ratio = annual_return / annual_volatility

                risk_return_metrics[strategy] = {
                    'Total Return': total_return,
                    'Annual Return': annual_return,
                    'Annual Volatility': annual_volatility,
                    'Sharpe Ratio': sharpe_ratio
                }

            return risk_return_metrics

        def propose_optimal_strategy(self, risk_return_metrics):
            optimal_strategy = max(risk_return_metrics, key=lambda x: risk_return_metrics[x]['Sharpe Ratio'])
            return optimal_strategy
                        
    