import numpy as np
from scipy import linalg
from Return_Data_Collector import get_asset_return_data,get_SP500, get_market_portfolio_weights
import cvxpy
import pandas as pd


def update_views(list_assets, num_views, relevant_assets, P_views_values, Q_views_values):
        P = np.zeros((num_views,len(list_assets)))
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
                P[i,index] = P_views_values[i][j]
        # update views matrix Q
        Q = np.array([Q_views_values[i] for i in range(len(Q_views_values))]).reshape(num_views, 1)

        return [P,Q]


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
        #combined_cov_inv = linalg.inv(combined_covariance)

        # For some reason this doesn't work

        num_asset = len(sigma)
        w = cvxpy.Variable(num_asset) #30 assets

        constraints = []
        # constraints.append(cvxpy.abs(w) <= 0.4)
        constraints.append(w >= 0)
        constraints.append(cvxpy.sum_entries(w) == 1)

        objective = cvxpy.Maximize(combined_return.T * w - 0.5 * alpha * cvxpy.quad_form(w, combined_covariance))
        # objective = cvxpy.Maximize(combined_return*w -0.5*alpha*(w.T*combined_covariance*w))
        problem = cvxpy.Problem(objective, constraints)
        problem.solve(solver='CVXOPT', verbose=True)

        Return = (combined_return.T * w - 0.5 * alpha * cvxpy.quad_form(w, combined_covariance)).value
        weights = pd.DataFrame(w.value, index=name_asset, columns=['Holding'])
        return [weights,Return]

'''
    # Calculate the weights
    w = (1/alpha)*((combined_cov_inv).dot(combined_return))


'''
if __name__ == "__main__":

    SP500 = get_SP500()
    market_portfolio_weights = get_market_portfolio_weights(SP500,3)
    list_assets = list(market_portfolio_weights['Symbol'])
    return_data = get_asset_return_data(list_assets)['df_return']
    market_weights = np.array(market_portfolio_weights['market portfolio weights'])
#    expected_return = return_data.mean()
#    market_port_return = market_weights.dot(expected_return)
    num_views = 2
    P = np.zeros((num_views,len(list_assets)))
    alpha = 2.5

    num_views = 2
    relevant_assets = [['AZO', 'GOOGL'],['IBM']]
    P_views_values = [[0,0],[0]]
    Q_views_values = [0,0]
    Views_Matrices = update_views(list_assets, num_views, relevant_assets, P_views_values, Q_views_values)
    P = Views_Matrices[0]
    Q = Views_Matrices[1]
    result =  Black_Litterman(return_data, alpha, P, Q, market_weights)
    print result[0]
    print"Return of ",result[1]*100, "%"



