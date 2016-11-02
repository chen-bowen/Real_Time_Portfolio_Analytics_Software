import numpy as np
from scipy import linalg
import datetime
import pandas as pd
from pandas_datareader import data
#import cvxpy

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
            
def Black_Litterman(return_data, alpha, P, Q, wmkt):
    tau = 0.05
#    std = return_data.std().as_matrix()
    sigma = return_data.cov().as_matrix()
    scaled_sigma = tau*sigma
    scaled_sigma_inv = linalg.inv(scaled_sigma)
    
    pi = (alpha*sigma).dot(wmkt)
    
    Omega = (P.dot(scaled_sigma).dot(P.T)) * np.eye(Q.shape[0])
    Omega_inv= linalg.inv(Omega)
    
    combined_return = linalg.inv(scaled_sigma_inv + P.T.dot(Omega_inv).dot(P)).dot(np.dot(scaled_sigma_inv,pi) + np.dot(np.dot(P.T,Omega_inv),Q))
    combined_covariance = sigma + linalg.inv(scaled_sigma_inv + P.T.dot(Omega_inv).dot(P))
    combined_cov_inv = linalg.inv(combined_covariance)
    
    w = (1/alpha)*((combined_cov_inv).dot(combined_return))
    
    return [w,combined_return]

if __name__ == "__main__":
    return_data = get_return_data(['GOOG', 'AMZN', 'AAPL', 'TVIX'])['df_return']
  #  print return_data['df_price'].tail(10)
    wmkt = np.array([0.615,0.0783,0.1827,0.124])
    
    alpha = 2.5
    P1 = np.array([0,  -.295, 1.00, -.705])
    P2 = np.array([0, 1.0, 0, -1.0 ])
    P = np.array([P1,P2])
    
    Q1 = 0.05
    Q2 = 0.03
    Q=np.array([Q1,Q2])
    
    result =  Black_Litterman(return_data, alpha, P, Q, wmkt)
    
    
    '''
    expected_return = result['df_return'].mean().as_matrix()
    std = result['df_return'].std().as_matrix()
    covariance = result['df_return'].cov().as_matrix()
    
    #def Black_Litterman(std,P)
    tau = 0.05
    std = np.array([0.160, 0.203, 0.248, 0.271, 0.210, 0.200, 0.187])
    
    
    wmkt = np.array([0.016,0.022,0.052,0.055,0.116,0.124,0.615])
    
    
    Corr = np.array([ [1.000, 0.488, 0.478, 0.515, 0.439, 0.512, 0.491],
                      [0.488, 1.000, 0.664, 0.655, 0.310, 0.608, 0.779],
                      [0.478, 0.664, 1.000, 0.861, 0.355, 0.783, 0.668],
                      [0.515, 0.655, 0.861, 1.000, 0.354, 0.777, 0.653],
                      [0.439, 0.310, 0.355, 0.354, 1.000, 0.405, 0.306],
                      [0.512, 0.608, 0.783, 0.777, 0.405, 1.000, 0.652],
                      [0.491, 0.779, 0.668, 0.653, 0.306, 0.652, 1.000]])
    
    
    
    sigma = np.outer(std,std)*Corr
    scaled_sigma = tau*sigma
    scaled_sigma_inv = linalg.inv(scaled_sigma)
    
    
    alpha = 2.5
    pi = (alpha*sigma).dot(wmkt)
    
    P1 = np.array([0, 0, -.295, 1.00, 0, -.705, 0 ])
    P2 = np.array([0, 1.0, 0, 0, 0, 0, -1.0 ])
    P = np.array([P1,P2])
    
    Q1 = 0.05
    Q2 = 0.03
    Q=np.array([Q1,Q2])
    Omega = (P.dot(scaled_sigma).dot(P.T)) * np.eye(Q.shape[0])
    Omega_inv= linalg.inv(Omega)
    
    combined_return = linalg.inv(scaled_sigma_inv + P.T.dot(Omega_inv).dot(P)).dot(np.dot(scaled_sigma_inv,pi) + np.dot(np.dot(P.T,Omega_inv),Q))
    combined_covariance = sigma + linalg.inv(scaled_sigma_inv + P.T.dot(Omega_inv).dot(P))
    combined_cov_inv = linalg.inv(combined_covariance)
    
    w = (1/alpha)*((combined_cov_inv).dot(combined_return))
    
    
    

    num_asset = len(Corr)
    w = cvxpy.Variable(num_asset)
    
    
    constraints = []
    constraints.append(cvxpy.sum_entries(w) == 1)
    
    objective = cvxpy.Maximize(combined_return*w -0.5*alpha*(w.T*combined_covariance*w))
    problem = cvxpy.Problem(objective)
    problem.solve(solver='CVXOPT', verbose=True)
    
    print w.value
    
    '''