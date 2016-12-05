from flask import Flask, make_response, session
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for, render_template
from common.Return_Data_Collector import get_asset_return_data, get_SP500, get_market_portfolio_weights, get_market_portfolio_weights_customized, get_price_changes_data
from common.Black_Litterman import Black_Litterman,update_views,combine_momentum_oscilator_views, get_RSI_assets,update_relevant_assets_RSI, find_stochastic_osciliator, update_relevant_assets_Stochastic
import pandas as pd
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import StringIO

# from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@hostname/database_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://zbkogjiodhmxob:3LpsDLCEaBHv1b_cu99otyPdY6@ec2-54-235-119-29.compute-1.amazonaws.com:5432/ddv0hgedai3tgo'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['SECRET_KEY'] = 'super-secret'
# app.config['SECURITY_REGISTERABLE'] = True

app.debug = True
db = SQLAlchemy(app)

# """
# Models
# """
# roles_users = db.Table('roles_users',
#        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
#        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))
#
#
# class Role(db.Model, RoleMixin):
#    id = db.Column(db.Integer(), primary_key=True)
#    name = db.Column(db.String(80), unique=True)
#    description = db.Column(db.String(255))
#
#
# class User(db.Model, UserMixin):
#    id = db.Column(db.Integer, primary_key=True)
#    email = db.Column(db.String(255), unique=True)
#    password = db.Column(db.String(255))
#    active = db.Column(db.Boolean())
#    confirmed_at = db.Column(db.DateTime())
#    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
#
#
# #Setup Flask-Security
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(app, user_datastore)
#

"""
Routes
"""


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('security/login.html')


@app.route('/portfolio')
#@login_required
def portfolio():
    return render_template('portfolio.html', name='Run Portfolio Optimization')


@app.route('/customportfolio')
#@login_required
def customportfolio():
    return render_template('customportfolio.html', name='Run Customized Portfolio Optimization')


@app.route('/portfolio/get_optimal_portfolio_black_litterman', methods=['GET','POST'])
def get_optimal_portfolio_black_litterman():
    number_assets = request.args.get("number")
    print number_assets

    SP500 = get_SP500()
    market_portfolio_weights = get_market_portfolio_weights(SP500, int(number_assets))
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

    print RSI_views
    print STO_views

    RSI_big = RSI_views[3]
    RSI_small = RSI_views[4]
    STO_big = STO_views[3]
    STO_small = STO_views[4]

    print RSI_small
    print RSI_big

    RSI_views = RSI_views[:3]
    STO_views = STO_views[:3]

    relevant_assets = combine_momentum_oscilator_views(RSI_views, STO_views)[0]
    P_views_values = combine_momentum_oscilator_views(RSI_views, STO_views)[1]
    Q_views_values = combine_momentum_oscilator_views(RSI_views, STO_views)[2]

    Views_Matrices = update_views(list_assets, relevant_assets, P_views_values, Q_views_values)
    P = Views_Matrices[0]
    Q = Views_Matrices[1]
    weights,Return = Black_Litterman(return_data, alpha, P, Q, market_weights)
    Return = ((1 + Return) ** 12 - 1) * 100
    Return_dict = [{'Return':Return}]
    Return_fr = pd.DataFrame(Return_dict)
    Return_fr = Return_fr.transpose()
    Return_fr = Return_fr.rename(columns={0: 'Holding'})
    weights = weights.append(Return_fr)
    weights.to_sql("Optimal Weight", db.get_engine(app), if_exists='replace')

    #weights = weights[weights.Holding > 0.001]
    weights = weights.round(2)

    weightsport = weights[:-1].to_html(classes = 'table table-striped table-bordered table-hover id="portfolio')

    session['data'] = weightsport
    session['Return'] = Return.round(2)
    session['rsi_small'] = RSI_small
    session['rsi_big'] = RSI_big
    session['sto_small'] = STO_small
    session['sto_big'] = STO_big

    #saving
    weights = pd.read_sql_table("Optimal Weight", db.get_engine(app))

    weights = weights.transpose()
    weights.columns = weights.iloc[0]

    weights[1:].to_sql("Weights", db.get_engine(app), index=False, if_exists='append')

    return redirect('/result')

    '''return render_template('portfolio.html', name="Optimal Portfolio", data=weightsport)'''


@app.route('/customportfolio/get_optimal_customportfolio_black_litterman', methods=['GET','POST'])
def get_optimal_customportfolio_black_litterman():
    list_assets = request.form.getlist("assets")
    list_assets = ''.join(list_assets)
    list_assets = list_assets.replace(" ", "")
    list_assets = list_assets.split(",")
    print list_assets

    view1 = request.form.getlist("view1")
    view2 = request.form.getlist("view2")

    view1 = ''.join(view1)
    view1 = view1.replace("%", "")
    view1 = view1.replace("by", "")
    view1 = view1.split(" ")
    if "" in view1: view1.remove("")

    view2 = ''.join(view2)
    view2 = view2.replace("%", "")
    view2 = view2.replace("by", "")
    view2 = view2.split(" ")
    if "" in view2: view2.remove("")

    print view1
    print view2

    SP500 = get_SP500()
    market_portfolio_weights = get_market_portfolio_weights_customized(SP500, list_assets)
    print market_portfolio_weights
    '''list_assets = list(market_portfolio_weights['Symbol'])'''
    return_data = get_asset_return_data(list_assets)['df_return']
    market_weights = np.array(market_portfolio_weights['market portfolio weights'])

    alpha = 2.5

    relevant_assets = [[view1[0], view1[2]], [view2[0], view2[2]]] #list asset, first two are only needed for relative view
    P_views_values = [[1, -1], [1, -1]]
    Q_views_values = [float(str(view1[3]))/100.0, float(str(view2[3]))/100.0]

    Views_Matrices = update_views(list_assets, relevant_assets, P_views_values, Q_views_values)
    P = Views_Matrices[0]
    Q = Views_Matrices[1]
    weights,Return = Black_Litterman(return_data, alpha, P, Q, market_weights)
    Return = ((1 + Return) ** 12 - 1) * 100
    Return_dict = [{'Return':Return}]
    Return_fr = pd.DataFrame(Return_dict)
    Return_fr = Return_fr.transpose()
    Return_fr = Return_fr.rename(columns={0: 'Holding'})
    weights = weights.append(Return_fr)

    weights.to_sql("Optimal Weight", db.get_engine(app), if_exists='replace')

    #weights = weights[weights.Holding > 0.01]
    weights = weights.round(2)


    weightscust = weights[:-1].to_html(classes = 'table table-striped table-bordered table-hover id="portfolio')

    session['data'] = weightscust
    session['Return'] = Return.round(2)

    weights = pd.read_sql_table("Optimal Weight", db.get_engine(app))
    weights = weights.transpose()
    weights.columns = weights.iloc[0]

    weights[1:].to_sql("Weights", db.get_engine(app), index=False, if_exists='append')

    return redirect('/customresult')
    '''return render_template('customportfolio.html', name="Custom Optimal Portfolio", data=weightscust)'''


@app.route('/chart')
def chart():
    return render_template('chart.html', name='chart')


@app.route('/plot.png')
def plot():
    weights = pd.read_sql_table("Weights", db.get_engine(app))
    weight = weights.ix[:, weights.columns != 'Return'].tail(1)

    weight = weight.loc[:, (weight > 0.001).any(axis=0)]

    labels = list(weight.columns.values)
    values = weight.values.tolist()

    cs = cm.Set1(np.arange(40) / 40.)

    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.pie(values[0], labels=labels, colors=cs)
    plt.axis('equal')

    canvas = FigureCanvas(fig)
    output = StringIO.StringIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@app.route('/compare')
def compare():
    weights = pd.read_sql_table("Weights", db.get_engine(app))
    weights = weights.fillna(0)
    weights = weights.round(2)

    weightsmod = weights.to_html(classes = 'table table-striped table-bordered table-hover id="example')

    return render_template('compare.html', name='Compare Saved Portfolio Weights', data=weightsmod)


@app.route('/result')
def result():
    data = session.get('data', None)
    Return = session.get('Return', None)
    RSI_small = session.get('rsi_small', None)
    RSI_big = session.get('rsi_big', None)
    STO_small = session.get('sto_small', None)
    STO_big = session.get('sto_big', None)

    return render_template('result.html', name='Result', data=data, upRSIstock=RSI_small[0], upRSI=RSI_small[1],
                           downRSIstock=RSI_big[0], downRSI=RSI_big[1], upSTOstock=STO_small[0], upSTO=STO_small[1],
                           downSTOstock=STO_big[0], downSTO=STO_big[1], Return=Return)


@app.route('/customresult')
def customresult():
    data = session.get('data', None)
    Return = session.get('Return', None)
    print Return
    return render_template('customresult.html', name='Result', data=data, Return=Return)


@app.route('/result/save_data', methods=['GET','POST'])
def save_data():
    data = session.get('data', None)

    weights = pd.read_sql_table("Optimal Weight", db.get_engine(app))
    weights = weights.transpose()
    weights.columns = weights.iloc[0]

    weights[1:].to_sql("Weights", db.get_engine(app), index=False, if_exists='append')

    # return render_template("user.html", name=["GOOG", "AAPL"], data=df.head(10).to_html())
    return render_template('result.html', name='Result', data=data)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
