import requests
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf, pandas as pd
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.secret_key = '3d2ea423831c9ca9649c46aa0acb23e0'
db = SQLAlchemy(app)

class Stock(db.Model):
    id = db.Column((db.Integer), primary_key=True)
    ticker = db.Column((db.String(50)), nullable=False)
    def __repr__(self):
        return f"Stock('{self.ticker}')"


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        new_stock = request.form.get('ticker')
        if new_stock:
            new_stock_obj = Stock(ticker=new_stock)
            db.session.query(Stock).delete()
            db.session.commit()
            db.session.add(new_stock_obj)
            db.session.commit()
    stock = Stock.query.first()
    try:
        ticker = yf.Ticker(stock.ticker)
        dictionary = ticker.info
        financial_info = {'name':dictionary['shortName'], 
         'ticker':'' + dictionary['symbol'], 
         'price':'${:,}'.format(dictionary['bid']), 
         'market_cap':'${:,}'.format(dictionary['marketCap']), 
         'high':'${:,}'.format(dictionary['fiftyTwoWeekHigh']), 
         'low':'${:,}'.format(dictionary['fiftyTwoWeekLow'])}
        if dictionary['dividendYield'] == None:
            financial_info['div_yield'] = 'N/A'
        else:
            financial_info['div_yield'] = str(round(100 * float(dictionary['dividendYield']), 2)) + '%'
        return render_template('financial_info.html', data=financial_info)
    except:
        return render_template('financial_info.html', data={'name':'Invalid Stock Symbol',  'ticker':'-'})


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", category='success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'tdrenis@gmail.com':
            if form.password.data == 'sarelis':
                flash('You have been logged in!', category='success')
                return redirect(url_for('home'))
        flash('Login Unsuccessful. Please check username and password.', category='danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)