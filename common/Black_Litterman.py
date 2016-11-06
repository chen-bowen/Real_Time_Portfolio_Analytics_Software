

import numpy as np
from scipy import linalg
from Return_Data_Collector import get_return_data
import cvxpy


def Black_Litterman(return_data, alpha, P, Q, wmkt):
    # P indicates which of the asset is relevant to the investor's view, right now it is hard coded
    # Q represent the value of the views

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

    # The standard error in investor's views
    Omega = (P.dot(scaled_sigma).dot(P.T)) * np.eye(Q.shape[0])
    Omega_inv= linalg.inv(Omega)

    # Find combined returns and combined covariance for the updated quadratic optimization
    combined_return = linalg.inv(scaled_sigma_inv + P.T.dot(Omega_inv).dot(P)).dot(np.dot(scaled_sigma_inv,pi) + np.dot(np.dot(P.T,Omega_inv),Q))
    combined_covariance = sigma + linalg.inv(scaled_sigma_inv + P.T.dot(Omega_inv).dot(P))
    #combined_cov_inv = linalg.inv(combined_covariance)

    # For some reason this doesn't work

    num_asset = len(sigma)
    w = cvxpy.Variable(num_asset)


    constraints = []
    constraints.append(cvxpy.sum_entries(w) == 1)

    objective = cvxpy.Maximize(combined_return * w - 0.5 * alpha * cvxpy.quad_form(w, combined_covariance))
    # objective = cvxpy.Maximize(combined_return*w -0.5*alpha*(w.T*combined_covariance*w))
    problem = cvxpy.Problem(objective)
    problem.solve(solver='CVXOPT', verbose=True)

    print w.value

    return [w, combined_return]

'''
    # Calculate the weights
    w = (1/alpha)*((combined_cov_inv).dot(combined_return))


'''
if __name__ == "__main__":
    return_data = get_return_data(['GOOG', 'AMZN', 'AAPL', 'TVIX'])['df_return']

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

    # right now most of the parameters are hard coded



