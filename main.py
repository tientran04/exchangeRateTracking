import re
import requests
from flask import Flask, render_template, request, url_for
from flask_mail import Mail, Message
from bs4 import BeautifulSoup as soup
from threading import Thread, Timer
from datetime import date, datetime
import os
from DBcm import UseDatabase


app = Flask(__name__)

recipients = {}
send_mail_date = {}

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "tientran.test@gmail.com",
    "MAIL_PASSWORD": "blofpvyhdixyzklj"
}


app.config.update(mail_settings)
mail = Mail(app)


app.config["dbconfig"] = {  'host': '127.0.0.1',
                            'user': 'postgres',
                            'password': '123',
                            'database': 'exchangeratetracking'}


def get_exchange_rate(recipients, send_mail_date):
    print("###Get Exchange: Start " + datetime.now().strftime("%H:%M:%S"))
    url = "https://www.google.com/search?q=nzd+to+vnd"
    res = requests.get(url).content
    web_content = soup(res, "lxml")
    exchange_rate_text = web_content.find_all("div", class_="BNeawe iBp4i AP7Wnd")[-1].get_text()
    exchange_rate_array = exchange_rate_text.replace(",", "").split()
    exchange_rate = float(exchange_rate_array[0])

    print(f"###Exchange rate: {exchange_rate}")

    for email, value in recipients.items():
        if (exchange_rate - 150) > value:
            if email not in send_mail_date or send_mail_date[email] != date.today():
                send_mail(exchange_rate, email)
                send_mail_date[email] = date.today()


def send_mail(exchange_rate, email):
    with app.app_context():
        msg = Message(subject = f"Update NZD/VND exchange rate {date.today()}",
                      sender = "Exchange Rate Tracking",
                      recipients = [email],
                      body = f"NZD/VND is {exchange_rate} at the moment.")
        mail.send(msg)
    return "Send mail successfully!"


def getExchange(recipients, send_mail_date):
    get_exchange_rate(recipients, send_mail_date)
    t = Timer(5, getExchange, args=(recipients, send_mail_date))
    t.start()


def wake_up():
    with app.app_context():
        requests.get("https://exchangeratetracking.herokuapp.com/")
        t = Timer(1500, wake_up)
        t.start()


@app.route("/")
def index():
    entry_headling = "Welcome to NZD Exchange Rate Tracking Site "
    return render_template("index.html", entry_headling = entry_headling)


@app.route("/start")
def start():
    getExchange(recipients, send_mail_date)
    wake_up()
    return "Start get exchange successfully!"


@app.route("/register", methods=["GET", "POST"])
def register():
    #render register.html if get
    if request.method == "GET":
        return render_template("register.html")

    #update database if post
    value = float(request.form["value"].replace(",", ""))
    email = request.form["email"].strip()
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SELECT_SQL="""SELECT * FROM recipients WHERE email = %s;"""
            cursor.execute(_SELECT_SQL, (email,))
            check = cursor.fetchone()
            if check:
                _UPDATE_SQL="""UPDATE recipients SET exchange_rate = %s WHERE email = %s;"""
                cursor.execute(_UPDATE_SQL, (value, email))
                message = "You have updated exchange rate value successfully!"
            else:
                _INSERT_SQL="""INSERT INTO recipients (email, exchange_rate)
                        VALUES (%s, %s);"""
                cursor.execute(_INSERT_SQL, (email, value))
                message = "You have registered successfully!"
    except Exception as error:
        print(error)
        message = error

    return render_template("successful.html", message = message)


@app.route("/unfollow", methods=["GET", "POST"])
def unfollow():
    #handle GET request
    if request.method == "GET":
        return render_template("unfollow.html")

    #handle POST request
    email = request.form["email"].strip()
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
                    _SQL="""DELETE FROM recipients
                            WHERE email = %s;"""
                    cursor.execute(_SQL, (email,))
        message = "You have unfollowed the exchange rate tracking site!"
    except Exception as error:
        print(error)
        message = error
    return render_template("successful.html", message = message)


@app.route("/view")
def view():    
    return render_template("view.html", recipients = recipients, send_date = send_mail_date)

    
app.secret_key = "abc"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port = port)
