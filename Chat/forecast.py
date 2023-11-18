from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
import yfinance as yf

class Forecast:
    def __init__(self, ticker) -> None:
        self.ticker = ticker
        self.dfYahoo = yf.Ticker(ticker).history(period="5y", interval = "1mo")
        self.pred = None
        self.df = None
        
    def make_LagDF(self):
        self.df = pd.DataFrame(self.dfYahoo["Close"])
        self.df.index = self.df.index.date
        self.df['Time'] = np.arange(len(self.df.index))
        self.df['Lag_1'] = self.df['Close'].shift(3)
        self.df['Lag_2'] = self.df['Close'].shift(6)
        self.df['Lag_3'] = self.df['Close'].shift(12)
        self.df.fillna(method="backfill",inplace=True)

    def make_TimeDF(self):
        self.df = pd.DataFrame(self.dfYahoo["Close"])
        self.df.index = self.df.index.date
        self.df['Time'] = np.arange(len(self.df.index))

    def get_LagRegYearStockForecast(self):
        """ Creates time series multivariable regression with 3 lags(3, 6, 12 moths) for given ticker
            Args :
                years : number of years in forecast
            
            Returns :
                predDF : dataframe in whith index is date and pred is predicted value
        """
        self.make_LagDF()
        X = self.df.loc[:, ['Time','Lag_1' , 'Lag_2', "Lag_3"]]
        y = self.df.loc[:, 'Close']
        y, X = y.align(X, join='inner')

        model = LinearRegression()
        model.fit(X, y)
        
        rng = np.arange(12) + len(self.df.index)
        start = pd.to_datetime(self.df.index.max())
        index = pd.date_range(start, periods=12, freq='M')
        predDF = pd.DataFrame({"Time" : rng})
        predDF.index = index
        
        predDF = pd.concat([self.df, predDF])
        predDF['Lag_1'] = predDF['Close'].shift(3)
        predDF['Lag_2'] = predDF['Close'].shift(6)
        predDF['Lag_3'] = predDF['Close'].shift(12)
        predDF.fillna(method="ffill",inplace=True)
        predDF = predDF[self.df["Time"].max() <= predDF["Time"]]
        
        y_pred = pd.Series(model.predict(predDF[["Time", 'Lag_1', 'Lag_2', 'Lag_3']]), index=predDF.index)
        
        predDF.drop(["Time", 'Lag_1', 'Lag_2', 'Lag_3', 'Close'], axis=1, inplace=True)
        predDF["pred"] = y_pred
        
        return predDF
    
    def get_TimeRegYearStockForecast(self, years = 3):
        """ Creates simple time series linear regresion for given ticker
            Args :
                years : number of years in forecast
            
            Returns :
                predDF : dataframe in whith index is date and pred is predicted value
        """
        self.make_TimeDF()
        X = self.df.loc[:, ['Time']]
        y = self.df.loc[:, 'Close']
        model = LinearRegression()
        model.fit(X, y)
        
        rng = np.arange(years * 12) + len(self.df.index)
        start = pd.to_datetime(self.df.index.max())
        index = pd.date_range(start, periods=years * 12, freq='M')
        predDF = pd.DataFrame({"Time" : rng})
        predDF.index = index
        y_pred = pd.Series(model.predict(predDF), index = predDF.index)
        
        predDF.drop("Time", axis=1, inplace=True)
        predDF["pred"] = y_pred
        
        return predDF
    


