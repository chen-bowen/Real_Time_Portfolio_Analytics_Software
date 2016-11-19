from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for, render_template
from common.Return_Data_Collector import get_asset_return_data, get_SP500, get_market_portfolio_weights
from common.MVO_Transaction_Costs import mvoptimization
from common.Black_Litterman import Black_Litterman,update_views
import pandas as pd

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


@app.route('/portfolio/get_optimal_portfolio_mvo', methods=['GET'])
def get_optimal_portfolio_MVO():
    df_return = pd.read_sql_table("returns", db.get_engine(app))

    # request.args for GET methods
    weights = mvoptimization(df_return, float(request.args['risk_limit'])/100)
    return render_template('portfolio.html', name="Optimal Portfolio", data=weights.to_html())
''''
@app.route('/portfolio/get_optimal_portfolio_black_litterman', methods=['GET'])
def get_optimal_portfolio_black_litterman():
   df_return = pd.read_sql_table("returns", db.get_engine(app))
'''
@app.route('/portfolio/save_data', methods=['POST'])
def save_data():
    df_return = get_asset_return_data(["GOOG", "AAPL", "AMZN", "FB", "TSLA", "UWTI", "NFLX", "TVIX"], start_date='2010-01-01')['df_return']
    SP500 = get_SP500()

    df_return.to_sql("returns", db.get_engine(app), if_exists='replace')
    SP500.to_sql("SP500", db.get_engine(app), if_exists='replace')
    # return render_template("user.html", name=["GOOG", "AAPL"], data=df.head(10).to_html())
    return redirect(url_for('portfolio'))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
