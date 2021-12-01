import requests
from flask import Flask, render_template, request
from flask_mail import Mail, Message
from bs4 import BeautifulSoup as soup
from threading import Thread, Timer
from datetime import date, datetime
import os


app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "tientran.test@gmail.com",
    "MAIL_PASSWORD": "blofpvyhdixyzklj"
}

recipients = {}
send_mail_date = {}

app.config.update(mail_settings)
mail = Mail(app)


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


def getExchange(recipients, send_mail_date):
    get_exchange_rate(recipients, send_mail_date)
    t = Timer(5, getExchange, args=(recipients, send_mail_date))
    t.start()


def wake_up():
    request.get("https://exchangeratetracking.herokuapp.com/")
    t = Timer(1500, wake_up)
    t.start()


getExchange(recipients, send_mail_date)
wake_up()


@app.route("/")
def entry_page():
    entry_headling = "Welcome to Exchange Rate Tracking Site "
    return render_template("entry.html", entry_headling = entry_headling)


@app.route("/register", methods=["POST"])
def register():
    value = float(request.form["value"].replace(",", ""))
    email = request.form["email"].strip()

    recipients[email] = value
    
    return render_template("register.html")


@app.route("/view")
def view():    
    return render_template("view.html", recipients = recipients, send_date = send_mail_date)

    
app.secret_key = "abc"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port = port)