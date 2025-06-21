

from sqlite3.dbapi2 import Row
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
import yfinance as yf
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from google import genai





routes = Blueprint('routes', __name__)

def chat_with_gemini(chat_log):
    
    client = genai.Client(api_key="AIzaSyA0WzrG2UZYrKKc9SvhAir9oNYGQrimIVU")
    
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents= chat_log
    )
    return response.text




@routes.route('/')
def home():
    return render_template('home.html')


@routes.route('/index', methods=['POST', 'GET'])
@login_required
def index():
    return render_template('index.html')


@routes.route('/submit', methods=['POST'])
@login_required
def submit():
   
    errorMessage = f"Enter a real Company Ticker"
    user_input = request.form['Sname'] 
    stock = yf.Ticker(user_input)
    try:
         stockInfo = stock.info
    except:
        return render_template('index.html', errorMessage=errorMessage)
        
    conn = sqlite3.connect('/Users/mukudaniyengar/Desktop/Stocksite dupelicate/instance/database.db')
    cursor = conn.cursor()
    
    if stock.info:
        price = stock.info['regularMarketPrice']
        company_name = stock.info['longName']
        summ = stock.info['longBusinessSummary']
        quar = stock.info['mostRecentQuarter']
        goodOutput = f" Company name: {company_name}<br> price: ${price}<br>"
        now = datetime.now()
        today = now.strftime("%m/%d/%Y, %H:%M:%S")
        print(current_user.id)
        cursor.execute('''INSERT INTO search_history (id, ticker, date_searched, ticker_price) VALUES (?, ?, ?, ?)''', (current_user.id, user_input, now, float(price)))
        conn.commit()
        cursor.close()
        stock_data = yf.download(user_input, start='2024-06-08')[['Close', 'Volume']]
        plt.figure(figsize=(18, 10))
        stock_data.plot(subplots=True)
        plt.savefig('/Users/mukudaniyengar/Desktop/Stocksite dupelicate/app/static/plot.png')  
        plt.close()
    
    else:
        return render_template('index.html')

   
    return render_template('index.html', symbol=user_input, goodOutput = goodOutput, plot_url = url_for('static', filename='plot.png'))

@routes.route('/portfolio', methods = ['POST'])
@login_required
def Add_to_Portfolio():
    stock_input = request.form['Stname']
    amount_input = request.form['Amount']
    stock2 = yf.Ticker(stock_input)
    errorMessage = f"Enter a real Company Ticker"
    conn = sqlite3.connect('/Users/mukudaniyengar/Desktop/Stocksite dupelicate/instance/database.db')
    cursor = conn.cursor()
    try:
         stock2Info = stock2.info
    except:
        return render_template('portfolio.html', errorMessage=errorMessage)
 
    if stock2.info:
        price = stock2.info['regularMarketPrice']
        now = datetime.now()
        today = now.strftime("%Y-%m-%D %H:%M:%S")
        total_cost = (int(amount_input)*float(price)) 
        cursor.execute('''INSERT INTO portfolio(id, ticker, date_purchased, ticker_price, amount, total_cost) VALUES (?, ?, ?, ?, ?, ?)''', (current_user.id, stock_input, now, float(price), int(amount_input), total_cost))
        conn.commit()
        cursor.close()
        return render_template('portfolio.html')
    else:
        return render_template('portfolio.html')
    
    

    

@routes.route('/get_history', methods=['POST', 'GET'])
@login_required
def get_history():
    conn = sqlite3.connect('/Users/mukudaniyengar/Desktop/Stocksite dupelicate/instance/database.db')
    cursor = conn.cursor()
    ids = current_user.id
    cursor.execute('SELECT ticker, date_searched, ticker_price  FROM search_history WHERE id = ?', (ids,))
    rows = cursor.fetchall()
    output_lines = []
    for row in rows:
        ticker, date_searched, ticker_price = row
        output_lines.append(f"{ticker} {date_searched} {ticker_price}")

    output_string = "<br>".join(output_lines) 

    cursor.close()
    conn.close()
    return render_template('index.html', out=output_string)

@routes.route('/get_portfolio', methods=['POST', 'GET'])
@login_required
def get_portfolio():
    conn = sqlite3.connect('/Users/mukudaniyengar/Desktop/Stocksite dupelicate/instance/database.db')
    cursor = conn.cursor()
    ids = current_user.id
    cursor.execute('SELECT ticker, date_purchased, ticker_price, total_cost  FROM portfolio WHERE id = ?', (ids,))
    rows2 = cursor.fetchall()
    output_lines = []
    for row in rows2:
        ticker, date_purchased, ticker_price, total_cost= row
        output_lines.append(f"{ticker} {date_purchased} ${ticker_price} ${total_cost}")

    output_string = "<br>".join(output_lines)  

        
    cursor.close()
    conn.close()
    return render_template('portfolio.html', rows2 = output_string)

@routes.route('/prompt_ai', methods=['POST', 'GET'])
@login_required
def prompt_ai(): 
    conn = sqlite3.connect('/Users/mukudaniyengar/Desktop/Stocksite dupelicate/instance/database.db')
    cursor = conn.cursor()
    ids = current_user.id
    ai_response = ""

    if request.method == 'POST':
        query = request.form['prompt']
    
        question = "if the input has the words 'searched' or 'looked up' Here is the table definition of a sqlite3 table - search_history(id integer, ticker string(10), date_searched Datetime, ticker_price decimal(10,2)), give me a SQL statement for this question :"
        question2 = "or if the input has the words 'portfolio' or 'bought' Here is the table definition of a sqlite3 table - portfolio(id integer, ticker string(10), date_purchased Datetime, ticker_price decimal(10,2), amount integer, total_cost decimal(20,3)), give me a SQL statement for this question :"
        
        ai_user_input = query + question + question2 +"Return only the SQL statement with no quotes or extra words. If input lacks 'searched, looked up, portfolio, bought, buy, or search', return error Format like: SELECT ticker FROM search_history WHERE DATE(date_searched) = DATE('now')."
        
        
        sql_response = chat_with_gemini(ai_user_input) + 'AND id = ?'
        if 'error' in sql_response:
            ai_response = 'error'
        else:
            cursor.execute(sql_response, (ids,))
            ai_response = cursor.fetchall()
        
        

    return render_template('aiprompt.html', ai_response=ai_response)
        



    
    