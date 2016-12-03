from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for, render_template
from common.Return_Data_Collector import get_asset_return_data, get_SP500, get_market_portfolio_weights, get_market_portfolio_weights_customized, get_price_changes_data
from common.Black_Litterman import Black_Litterman,update_views,combine_momentum_oscilator_views, get_RSI_assets,update_relevant_assets_RSI, find_stochastic_osciliator, update_relevant_assets_Stochastic
import pandas as pd
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import StringIO


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@hostname/database_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://zbkogjiodhmxob:3LpsDLCEaBHv1b_cu99otyPdY6@ec2-54-235-119-29.compute-1.amazonaws.com:5432/ddv0hgedai3tgo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# app.debug = True
db = SQLAlchemy(app)

"""
Models
"""

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(255), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

"""
Routes
"""
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user')
def user():
    myUser = User.query.all()
    return render_template('user.html', myUser=myUser)


@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/customportfolio')
def customportfolio():
    return render_template('customportfolio.html')

@app.route('/user/post_user', methods=['POST'])
def post_user():
    user = User(request.form['username'], request.form['email'])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('user'))


@app.route('/user/delete_user', methods=['POST'])
def delete_user():
    user = User.query.filter_by(username=request.form['username']).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('user'))


@app.route('/portfolio/get_optimal_portfolio_black_litterman', methods=['GET','POST'])
def get_optimal_portfolio_black_litterman():

    SP500 = get_SP500()
    market_portfolio_weights = get_market_portfolio_weights(SP500, 3)
    list_assets = list(market_portfolio_weights['Symbol'])
    return_data = get_asset_return_data(list_assets)['df_return']
    return_data.to_sql("returns", db.get_engine(app), if_exists='replace')
    SP500.to_sql("SP500", db.get_engine(app), if_exists='replace')
    market_weights = np.array(market_portfolio_weights['market portfolio weights'])

    Close_prices = get_price_changes_data(list_assets)
    Close_prices_copy = Close_prices.copy(deep=True)
    High_prices = get_price_changes_data(list_assets, price_type='High')
    Low_prices = get_price_changes_data(list_assets, price_type='Low')
    RSI = get_RSI_assets(Close_prices_copy)
    STO = find_stochastic_osciliator(High_prices, Low_prices, Close_prices)
    alpha = 2.5

    RSI_views = update_relevant_assets_RSI(RSI)
    STO_views = update_relevant_assets_Stochastic(STO)

    relevant_assets = combine_momentum_oscilator_views(RSI_views, STO_views)[0]
    P_views_values = combine_momentum_oscilator_views(RSI_views, STO_views)[1]
    Q_views_values = combine_momentum_oscilator_views(RSI_views, STO_views)[2]

    Views_Matrices = update_views(list_assets, relevant_assets, P_views_values, Q_views_values)
    P = Views_Matrices[0]
    Q = Views_Matrices[1]
    weights,Return = Black_Litterman(return_data, alpha, P, Q, market_weights)
    weights.to_sql("Optimal Weight", db.get_engine(app), if_exists='replace')

    return render_template('portfolio.html', name="Optimal Portfolio", data=weights.to_html())


@app.route('/customportfolio/get_optimal_customportfolio_black_litterman', methods=['GET','POST'])
def get_optimal_customportfolio_black_litterman():
    list_assets = request.form.getlist("check")

    SP500 = get_SP500()
    market_portfolio_weights = get_market_portfolio_weights_customized(SP500, list_assets)
    '''list_assets = list(market_portfolio_weights['Symbol'])'''
    return_data = get_asset_return_data(list_assets)['df_return']
    market_weights = np.array(market_portfolio_weights['market portfolio weights'])
    num_views = 2
    P = np.zeros((num_views, len(list_assets)))
    alpha = 2.5

    num_views = 2
    relevant_assets = [[list_assets[0], list_assets[1]], [list_assets[2]]]
    P_views_values = [[0, 0], [0]]
    Q_views_values = [0, 0]
    Views_Matrices = update_views(list_assets, num_views, relevant_assets, P_views_values, Q_views_values)
    P = Views_Matrices[0]
    Q = Views_Matrices[1]
    weights,Return = Black_Litterman(return_data, alpha, P, Q, market_weights)
    weights.to_sql("Optimal Weight", db.get_engine(app), if_exists='replace')

    weights.to_json(orient='records')

    return render_template('customportfolio.html', name="Custom Optimal Portfolio", data=weights.to_html())


@app.route('/portfolio/save_data', methods=['GET','POST'])
def save_data():
    weights = pd.read_sql_table("Optimal Weight", db.get_engine(app))
    weights = weights.transpose()
    weights.columns =weights .iloc[0]
    #weights.reindex(weights.index.drop('index'))
    print weights

    weights[1:].to_sql("Weights", db.get_engine(app), index=False, if_exists='append')

    # return render_template("user.html", name=["GOOG", "AAPL"], data=df.head(10).to_html())
    return redirect(url_for('portfolio'))


@app.route('/customportfolio/custom_save_data', methods=['GET','POST'])
def custom_save_data():
    weights = pd.read_sql_table("Optimal Weight", db.get_engine(app))
    weights = weights.transpose()
    weights.columns =weights .iloc[0]
    #weights.reindex(weights.index.drop('index'))
    print weights

    weights[1:].to_sql("Weights", db.get_engine(app), index=False, if_exists='append')

    # return render_template("user.html", name=["GOOG", "AAPL"], data=df.head(10).to_html())
    return redirect(url_for('customportfolio'))

@app.route('/chart')
def chart(chartID = 'chart_ID', chart_type = 'bar', chart_height = 350):
    return render_template('chart.html', name='chart')


@app.route('/plot.png')
def plot():
    weights = pd.read_sql_table("Weights", db.get_engine(app))
    weight = weights.tail(1)

    labels = list(weight.columns.values)
    values = weight.values.tolist()

    fig = plt.figure()
    plt.pie(values[0], labels=labels)

    canvas = FigureCanvas(fig)
    output = StringIO.StringIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@app.route('/compare')
def compare():
    weights = pd.read_sql_table("Weights", db.get_engine(app))
    weightsmod = weights.to_html(classes = 'table table-striped table-bordered table-hover id="example')
    print weightsmod
    return render_template('compare.html', name='Compare', data=weightsmod)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
