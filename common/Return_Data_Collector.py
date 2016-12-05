import pandas as pd
import datetime
from pandas_datareader import data
import datapackage
from dateutil.relativedelta import relativedelta

def get_asset_return_data(asset_list,
                          price_type='Close',
                          source='yahoo',
                          start_date='2013-01-01',
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
        # df_price = df_price.drop('NEE', 1)
        df_price.dropna(inplace=True)
        df_return = df_price.resample('M').apply(lambda x: x[-1]).pct_change()
        df_momentum = df_price.resample('M').apply(lambda x: x[-1]).diff()
    except Exception as e:
        raise RuntimeError(e)

    return {'df_price': df_price,
            'df_return': df_return,
            'momentum':df_momentum}


def get_price_changes_data(asset_list,
                           price_type='Close',
                           source='yahoo',
                           start_date=datetime.datetime.today() - relativedelta(months=1),
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
        # df_price = df_price.drop('NEE', 1)
        df_price.dropna(inplace=True)

    except Exception as e:
        raise RuntimeError(e)

    return df_price

def get_SP500():
    dp = datapackage.DataPackage('http://data.okfn.org/data/core/s-and-p-500-companies/datapackage.json')
    SP500 = pd.DataFrame(dp.resources[1].data)
    SP500 = SP500[['Symbol', 'Name', 'Sector', 'Price', 'Dividend Yield', 'Price/Earnings', 'Earnings/Share',
                   'Book Value', '52 week low', '52 week high', 'Market Cap', 'EBITDA', 'Price/Sales', 'Price/Book',
                   'SEC Filings']]
    SP500 = SP500[SP500['Symbol'] <> 'NEE']
    SP500 = SP500[SP500['Symbol'] <> 'PSX']

    return SP500


def get_market_portfolio_weights_customized(SP500, chosen_assets):
    # Find the market portfolio constituents and it weights from S&P 500


    SP500 = SP500.drop(list(SP500[SP500['Market Cap'].isnull()].index.values))

    Portfolio = []

    for i in chosen_assets:
        Selected_stock = SP500[SP500['Symbol'] == i]

        Portfolio.append(Selected_stock)

    Portfolio = pd.concat(Portfolio)
    total_market_cap = Portfolio['Market Cap'].apply(float).sum()
    Portfolio['market portfolio weights'] = Portfolio['Market Cap'].apply(float) / total_market_cap

    portflio_weights = Portfolio[['Symbol', 'market portfolio weights']]

    return portflio_weights


def get_market_portfolio_weights(SP500, assets_per_sector):
    # Find the market portfolio constituents and it weights from S&P 500


    SP500 = SP500.drop(list(SP500[SP500['Market Cap'].isnull()].index.values))

    SP500_sectorspecific = SP500.groupby('Sector')
    Sectors = SP500_sectorspecific['Sector'].unique()

    Portfolio = []

    for sector in Sectors:
        Selected_stock = SP500_sectorspecific.get_group(sector[0]).sort_values(by=['Earnings/Share'],
                                                                               ascending=[0]).head(assets_per_sector)
        Portfolio.append(Selected_stock)

    Portfolio = pd.concat(Portfolio)
    total_market_cap = Portfolio['Market Cap'].apply(float).sum()
    Portfolio['market portfolio weights'] = Portfolio['Market Cap'].apply(float) / total_market_cap

    portflio_weights = Portfolio[['Symbol', 'market portfolio weights']]

    return portflio_weights


if __name__ == "__main__":
    SP500 = get_SP500()
    market_portflio_weights = get_market_portfolio_weights(SP500,3)
    chosen_assets = ["GOOGL", "AAPL", "AMZN", "FB", "TSLA", "UWTI", "NFLX", "TVIX"]
    custom_market_portflio_weights = get_market_portfolio_weights_customized(SP500, chosen_assets)
    print custom_market_portflio_weights
    list_assets = list(market_portflio_weights['Symbol'])

    result = get_asset_return_data(list_assets)['df_return']




 #   result['df_return'].to_csv('URL')
