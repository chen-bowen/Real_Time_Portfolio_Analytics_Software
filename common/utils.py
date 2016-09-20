import pandas as pd
import numpy as np
import datetime
from pandas_datareader import data
import cvxpy

def get_return_data(asset_list,
                    price_type='Open',
                    source='google',
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

def mvoptimization(df_return, risk_limit, wealth=1):
    expected_return = df_return.mean()
    covariance = df_return.cov()
    num_asset = len(covariance)
    name_asset = covariance.columns

    # Variables and Parameters
    w = cvxpy.Variable(num_asset)
    Ret = np.matrix(expected_return.values)
    Q = np.matrix(covariance.values)

    #
    risk = cvxpy.quad_form(w, Q)

    constraints = list()

    # Budget Constraint
    constraints.append(cvxpy.sum_entries(w) == 1)

    # Risk Contraint
    constraints.append(risk <= risk_limit)

    # Long only Constraint
    constraints.append(w >= 0)

    # Objective Function
    obj_func = cvxpy.Maximize(Ret*w)

    # Setting up the problem
    prob = cvxpy.Problem(obj_func, constraints)

    prob.solve(solver='CVXOPT', verbose=True)  # This should work as well

    print("Risk of: {0}".format(np.sqrt(risk.value)))

    weights = pd.DataFrame(w.value, index=name_asset, columns=['Holding'])

    return np.round(weights, decimals=2)


if __name__ == "__main__":
    result = get_return_data(['GOOG', 'AMZN', 'AAPL', 'TVIX'])
    print result['df_price'].tail(10)
    optimal_weights = mvoptimization(result['df_return'], 0.05)
    print optimal_weights
    # result['df_return'].to_csv('URL')