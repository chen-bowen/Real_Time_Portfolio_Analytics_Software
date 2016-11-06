import pandas as pd
import datetime
from pandas_datareader import data
import datapackage


def get_asset_return_data(asset_list,
                    price_type='Open',
                    source='yahoo',
                    start_date='1990-01-01',
                    end_date=datetime.datetime.today()):


    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    date_range = pd.bdate_range(start_date, end_date)
    try:
        df_price = pd.DataFrame(index=date_range, columns=asset_list)
        for ls in asset_list:
            try:
                price_data = data.DataReader(ls, source, start_date, end_date)[price_type]
                price_data.rename(ls, inplace=True)
                df_price[ls] = price_data.T
            except Exception as dr:
                pass
        df_price.dropna(inplace=True)
        df_return = df_price.pct_change()
    except Exception as e:
        raise RuntimeError(e)

    return {'df_price': df_price,
            'df_return': df_return}

def get_SP500():
    dp = datapackage.DataPackage('http://data.okfn.org/data/core/s-and-p-500-companies/datapackage.json')
    SP500 = pd.DataFrame(dp.resources[1].data)
    SP500 = SP500[['Symbol','Name','Sector','Price',	'Dividend Yield','Price/Earnings','Earnings/Share',
                   'Book Value',	'52 week low',	'52 week high','Market Cap',	'EBITDA','Price/Sales',	'Price/Book',	'SEC Filings']]

    return SP500

def get_market_portfolio(SP500):
    #Find the market portfolio constituents from S&P 500

    SP500_sectorspecific = SP500.groupby('Sector')
    Sectors = SP500_sectorspecific['Sector'].unique()
    Portfolio = []

    for sector in Sectors:
        Selected_stock = SP500_sectorspecific.get_group(sector[0]).sort_values(by =['Earnings/Share'], ascending=[0]).head(4)
        Portfolio.append(Selected_stock)

    Portfolio = pd.concat(Portfolio)

    return Portfolio

if __name__ == "__main__":
    result = get_return_data(['GOOG', 'AMZN', 'AAPL', 'TVIX'])
    SP500 = get_SP500()
    print SP500.head(5)
    market_portfolio = get_market_portfolio(SP500)
    print market_portfolio.head(5)


 #   result['df_return'].to_csv('URL')
