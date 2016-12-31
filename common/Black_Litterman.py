import numpy as np
from scipy import linalg
from Return_Data_Collector import get_asset_return_data,get_SP500, get_market_portfolio_weights,get_price_changes_data
import cvxpy
import pandas as pd

def find_relative_strength_index(stock):
    # find the gains and losses in stocks
    stock = stock.diff()
    # assemble the gains in one column
    stock['gain'] = np.where(stock[stock.columns[0]]>0, stock[stock.columns[0]], 0)
    # assemble the losses in one column
    stock['loss'] = np.where(stock[stock.columns[0]]<0, stock[stock.columns[0]], 0)
    # take the absolute value of losses
    stock['loss'] = stock['loss'].apply(lambda x: abs(x))
    # find the 14 day moving average of gains and losses
    stock['average gain'] = stock['gain'].rolling(window = 14,center = False).mean()
    stock['average loss'] = stock['loss'].rolling(window = 14,center = False).mean()
    # find the ration of RS by Average gain/Average loss
    stock['RS'] = (stock['average gain']*1.0)/stock['average loss']
    # find RSI by 100 - 100/RS
    stock['RSI'] = 100 - 100/(1+stock['RS'])

    return stock['RSI']

def get_RSI_assets(assets):
    # Get the RSI values for each stock in list_assets
    for i in assets.columns:
        assets[i] = find_relative_strength_index(assets[i].to_frame())
    return assets

def find_stochastic_osciliator(high,low,close):
    high_14 = high.rolling(window=20, center = False).max()
    low_14 = low.rolling(window=20, center = False).min()
    stochastic_oscillator = (close-low_14)*100.0/(high_14-low_14)
    return stochastic_oscillator


def update_relevant_assets_RSI(RSI):
    largest_rsi_stock = RSI[-1:].idxmax(axis=1)[0]
    smallest_rsi_stock = RSI[-1:].idxmin(axis=1)[0]
    largest_rsi = RSI[-1:].max(axis=1)[0]
    smallest_rsi = RSI[-1:].min(axis=1)[0]

    relevant_assets = []
    relevant_assets.append(largest_rsi_stock)
    relevant_assets.append(smallest_rsi_stock)
    P_views_values = []
    Q_views_values = []

    if (largest_rsi >= 80) & (smallest_rsi <= 20):
        P_views_values.append(-1)
        P_views_values.append(1)
        Q_views_values.append(0.03)
    else:
        P_views_values.append(0)
        P_views_values.append(0)
        Q_views_values.append(0)

    return [relevant_assets, P_views_values, Q_views_values, [largest_rsi_stock, largest_rsi], [smallest_rsi_stock, smallest_rsi]]


def update_relevant_assets_Stochastic(STO):
    largest_STO_stock = STO[-1:].idxmax(axis=1)[0]
    smallest_STO_stock = STO[-1:].idxmin(axis=1)[0]
    largest_STO = STO[-1:].max(axis=1)[0]
    smallest_STO = STO[-1:].min(axis=1)[0]

    relevant_assets = []
    relevant_assets.append(largest_STO_stock)
    relevant_assets.append(smallest_STO_stock)
    P_views_values = []
    Q_views_values = []

    if (largest_STO >= 80) & (smallest_STO <= 20):
        P_views_values.append(-1)
        P_views_values.append(1)
        Q_views_values.append(0.01)
    else:
        P_views_values.append(0)
        P_views_values.append(0)
        Q_views_values.append(0)

    return [relevant_assets, P_views_values, Q_views_values, [largest_STO_stock, largest_STO], [smallest_STO_stock, smallest_STO]]

def combine_momentum_oscilator_views(RSI_views, STO_views):
    relevant_assets = [RSI_views[0],STO_views[0]]
    P_views_values = [RSI_views[1],STO_views[1]]
    Q_views_values = [RSI_views[2],STO_views[2]]

    return [relevant_assets, P_views_values, Q_views_values]


def update_views(list_assets, relevant_assets, P_views_values, Q_views_values):
    num_views = len(relevant_assets)
    P = np.zeros((num_views, len(list_assets)))
    # Update the pick matrix P
    P_views_index = []
    for i in range(num_views):
        view_i_index = []
        for j in relevant_assets[i]:
            view_i_index.append(list_assets.index(j))
        P_views_index.append(view_i_index)

    for i in range(num_views):
        for j in range(len(P_views_index[i])):
            index = P_views_index[i][j]
            P[i, index] = P_views_values[i][j]
    # update views matrix Q
    Q = np.array([Q_views_values[i] for i in range(len(Q_views_values))]).reshape(num_views, 1)

    return [P, Q]


def Black_Litterman(return_data, alpha, P, Q, wmkt):
        # P indicates which of the asset is relevant to the investor's view, right now it is hard coded
        # Q represent the value of the views

        # set tau scalar
        tau = 0.0001
        # find the covariance matrix according to the return data
        sigma = return_data.cov().as_matrix()
        # pre-calculate the product fo tau and sigma
        scaled_sigma = tau*sigma
        # pre-calculate [tau*sigma]^-1
        scaled_sigma_inv = linalg.inv(scaled_sigma)

        name_asset = return_data.columns
        # The implied return of the asset, calculated from CAPM asset pricing model
        pi = (alpha*sigma).dot(wmkt)

        # The standard error in investor's views
        Omega = (P.dot(scaled_sigma).dot(P.T)) * np.eye(Q.shape[0])
        try:
            Omega_inv = linalg.inv(Omega)
        except:
            Omega_inv = Omega

        # Find combined returns and combined covariance for the updated quadratic optimization
        combined_return = linalg.inv(scaled_sigma_inv + P.T.dot(Omega_inv).dot(P)).dot(np.dot(scaled_sigma_inv,pi).reshape(len(sigma), 1) + np.dot(np.dot(P.T,Omega_inv),Q))
        combined_covariance = sigma + linalg.inv(scaled_sigma_inv + P.T.dot(Omega_inv).dot(P))

        num_asset = len(sigma)
        w = cvxpy.Variable(num_asset) #30 assets

        constraints = []
        constraints.append(w >= 0)
        constraints.append(cvxpy.sum_entries(w) == 1)

        objective = cvxpy.Maximize(combined_return.T * w - 0.5 * alpha * cvxpy.quad_form(w, combined_covariance))
        problem = cvxpy.Problem(objective, constraints)
        problem.solve(verbose=True)

        Return = (combined_return.T * w - 0.5 * alpha * cvxpy.quad_form(w, combined_covariance)).value
        pd.options.display.float_format = '{:.4f}%'.format
        weights = pd.DataFrame(w.value, index=name_asset, columns=['Holding'])
        weights['Holding'] =  weights['Holding'].apply(lambda x : x*100)
        return [weights, Return]

'''
    # Calculate the weights
    w = (1/alpha)*((combined_cov_inv).dot(combined_return))


'''
if __name__ == "__main__":
    SP500 = get_SP500()
    # chosen_assets = ["GOOGL", "AAPL", "AMZN", "FB", "NFLX"]
    # market_portfolio_weights = get_market_portfolio_weights_customized(SP500,chosen_assets)
    market_portfolio_weights = get_market_portfolio_weights(SP500, 3)
    list_assets = list(market_portfolio_weights['Symbol'])
    return_data = get_asset_return_data(list_assets)['df_return']
    # momentum = get_asset_return_data(list_assets)['momentum']
    market_weights = np.array(market_portfolio_weights['market portfolio weights'])
    Close_prices = get_price_changes_data(list_assets)
    High_prices = get_price_changes_data(list_assets,price_type='High')
    Low_prices = get_price_changes_data(list_assets,price_type='Low')
    RSI = get_RSI_assets(Close_prices)
    STO = find_stochastic_osciliator(High_prices,Low_prices,Close_prices)
    alpha = 2.5

    RSI_views = update_relevant_assets_RSI(RSI)
    STO_views = update_relevant_assets_Stochastic(STO)

    relevant_assets = combine_momentum_oscilator_views(RSI_views, STO_views)[0]
    P_views_values = combine_momentum_oscilator_views(RSI_views, STO_views)[1]
    Q_views_values = combine_momentum_oscilator_views(RSI_views, STO_views)[2]
    Views_Matrices = update_views(list_assets, relevant_assets, P_views_values, Q_views_values)
    P = Views_Matrices[0]
    Q = Views_Matrices[1]
    result = Black_Litterman(return_data, alpha, P, Q, market_weights)

    print result[0]
    print"Return of ", ((1+result[1])**12 -1)*100, "%"



