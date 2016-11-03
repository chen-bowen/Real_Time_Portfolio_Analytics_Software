

import numpy as np
from scipy import linalg
from utils import get_return_data

def Black_Litterman(return_data, alpha, P, Q, wmkt):
    # set tau scalar
    tau = 0.05
    # find the covariance matrix according to the return data
    sigma = return_data.cov().as_matrix()
    # pre-calculate the product fo tau and sigma
    scaled_sigma = tau*sigma
    # pre-calculate [tau*sigma]^-1
    scaled_sigma_inv = linalg.inv(scaled_sigma)

    # The implied return of the asset, calculated from CAPM asset pricing model
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
    P1 = np.array([0,  0, 1.00, -1.0])
    P2 = np.array([0, 1.0, 0, -1.0 ])
    P = np.array([P1,P2])
    
    Q1 = 0.05
    Q2 = 0.03
    Q=np.array([Q1,Q2])
    
    result =  Black_Litterman(return_data, alpha, P, Q, wmkt)
    print result
    
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


